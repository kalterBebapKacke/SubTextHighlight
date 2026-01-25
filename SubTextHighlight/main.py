import os
import datetime
import pysubs2
from Cython.Build.Dependencies import join_path
from .utils import dprint, advanced_SAA_Events
from .Highlight import Highlighter, highlight_args
from .Effects import Effects, effects_args
from . import utils
import fleep
import stable_whisper
import dataclasses
from . import handler

# TODO: Update Example Video
# TODO: Package and distribute package

off_time = datetime.timedelta(seconds=0.025)

@dataclasses.dataclass(kw_only=True)
class sub_args(utils.args_styles):
    """
    Configuration for the core subtitle generation and transcription process.

    This class defines the input/output paths, the transcription engine
    settings (Whisper), and the logic for how text is segmented into
    subtitle events.

    Attributes:
        input (str | dict | list | WhisperResult): The source to process. Can be
            a file path, a pre-transcribed dictionary/list, or a
            `stable_whisper.WhisperResult` object.
        output (str | None): File path where the generated subtitle file will
            be saved.
        input_video (str | None): Path to the source video file. Used for
            resolution detection and potential burning of subtitles.
        subtitle_type (str): The segmentation strategy. Supported options:
            - 'one_word_only': Displays exactly one word at a time.
            - 'join': Groups words into segments up to `word_max`.
            - 'separate_on_period': Splits segments at sentence boundaries.
        word_max (int): Maximum word count per subtitle event.
            Note: This is ignored if `subtitle_type` is 'one_word_only'.
        add_time (float): Time offset (in seconds) to extend the duration
            of each subtitle segment.
        fill_sub_times (bool): If True, ensures there are no gaps between
            consecutive subtitle segments.
        whisper_model (str): The specific OpenAI Whisper model size or
            language variant (e.g., 'medium.en', 'large-v3').
        whisper_device (str): The hardware device for inference (e.g., 'cpu',
            'cuda', or 'mps').
        whisper_refine (bool): If True, uses `stable-whisper` refinement to
            improve timestamp precision using audio frequencies.
    """

    input: str | dict[str, any] | list[dict[str, any]] | stable_whisper.result.WhisperResult
    output: str | None
    input_video: str | None = None
    subtitle_type: str = 'one_word_only'  # one_word_only, join, separate_on_period, appear
    word_max: int = 11
    add_time: float = 0
    fill_sub_times: bool = True
    whisper_model: str = 'medium.en'
    whisper_device: str = 'cpu'
    whisper_refine: bool = False



class Subtitle_Edit:
    """
        The central engine for subtitle generation and stylistic processing.

        This class handles the end-to-end workflow of subtitle creation, including
        input interpretation, style application, formatting logic (e.g., word-level
        splitting), visual effects, and final file building.

        Attributes:
            args (sub_args): Configuration object for subtitle editing and paths.
            main_style (ass.Style): The base visual style for the subtitles.
            word_max (int): Maximum number of words allowed per subtitle event.
            subtitle_type (str): The formatting strategy ('one_word_only',
                'separate_on_period', or 'join').
            highlighter (Highlighter, optional): Instance responsible for text
                highlighting logic.
            effects (Effects, optional): Instance responsible for visual animations
                and advanced styling.
            builder (utils.subs_builder): Utility to compile final subtitle events.
        """

    def __init__(self,
                 args_sub_edit:sub_args,
                 args_highlight:highlight_args | None = None,
                 args_effects: effects_args | None = None,
                ):
        """
                Initializes the Subtitle_Edit class with configuration and styles.

                Args:
                    args_sub_edit (sub_args): Core configurations including input/output
                        paths and model settings.
                    args_highlight (highlight_args, optional): Settings for text
                        highlighting. Defaults to None.
                    args_effects (effects_args, optional): Settings for visual effects
                        and animations. Defaults to None.
        """

        # args
        self.args = args_sub_edit

        # Style
        self.main_style = self.args.return_style()

        # Needed Variables for the formatting
        self.word_max = self.args.word_max
        self.subtitle_type = self.args.subtitle_type
        self.add_time = self.args.add_time
        self.fill_sub_times = self.args.fill_sub_times

        # Set handler and builder
        self.builder = utils.subs_builder()
        self.Handler = handler.Input_Output_Handler(args_sub_edit)

        # Highlighters
        #self.args_highlight = args_highlight

        if args_highlight is None:
            self.highlighter = None
        else:
            self.highlighter = Highlighter(args_highlight, self.main_style, self.subtitle_type)

        # Effects
        if args_effects is None:
            self.effects = None
        else:
            sample_highlighter = Highlighter(highlight_args(), self.main_style, self.subtitle_type)
            self.effects = Effects(args_effects)
            self.highlighter = self.effects.logic_highlighter(self.highlighter, sample_highlighter)


    def __call__(self):
        sub_file = self.Handler.handle_input()
        sub_file.styles["MainStyle"] = self.main_style

        if self.highlighter is not None:
            sub_file.styles["Highlight"] = self.highlighter.return_highlighted_style(self.main_style)

        subs = sub_file.events

        # create subtitles
        if self.subtitle_type == 'one_word_only':
            subs = self.one_word_only(subs)
        elif self.subtitle_type == 'separate_on_period':
            subs = self.short_subtitles(subs)
        elif self.subtitle_type == 'join':
            subs = self.short_subtitles_no_separation(subs)
        else:
            raise ValueError('Unsupported subtitle_type, please use a supported option.')

        # shift time
        if self.add_time != 0:
            subs = self.shift_subs_time(subs)

        # edit

        if self.effects is not None:
            subs  = self.effects(subs, sub_file)

        # build and save
        subs = self.builder(subs)
        sub_file.events = subs
        return self.Handler.handle_output(sub_file)

    def add_subtitle(self, cur_word:str, index:int, start, end, all_subs:list, highlight_words:bool=False, sub_list:list=()):
        if highlight_words is True:
            return self.highlighter(cur_word, start, end, all_subs, sub_list)
        else:
            all_subs.append(advanced_SAA_Events(start=start, end=end, text=cur_word.strip(), style="MainStyle"))
            return all_subs

    def short_subtitles(self, subs:list):
        word_highlight = self.return_if_highlight()
        new_subs = list()
        cur_word = ''
        index = 1
        start_time, end_time = self.start_end_time(subs)
        cur_sub_list = []

        for i, sub in enumerate(subs):
            #dprint(new_subs)
            last_iteration = len(subs) - 1 == i

            if sub.text.__contains__('.') or sub.text.__contains__('?') or sub.text.__contains__('!') or sub.text.__contains__(',') or last_iteration:
                cur_word = cur_word + sub.text
                cur_sub_list.append(sub)

                cur_end = self.return_end_time_logic(last_iteration, end_time, subs, sub, i)

                new_subs = self.add_subtitle(cur_word, index, start_time, cur_end, new_subs, highlight_words=word_highlight, sub_list=cur_sub_list)

                if not last_iteration:
                    start_time = subs[i+1].start

                cur_word = ''
                cur_sub_list = []
            else:
                cur_word = cur_word + sub.text + ' '
                cur_sub_list.append(sub)

        return new_subs

    def one_word_only(self, subs:list):
        word_highlight = self.return_if_highlight()
        new_subs = list()
        index = 1
        start_time, end_time = self.start_end_time(subs)

        for i, sub in enumerate(subs):
            last_iteration = len(subs) - 1 == i

            if not last_iteration:
                if self.fill_sub_times:
                    cur_end = subs[i+1].start
                else:
                    cur_end = sub.end
            else:
                cur_end = end_time

            new_subs = self.add_subtitle(sub.text, index, start_time, cur_end, new_subs, highlight_words=word_highlight,)

            if not last_iteration:
                start_time = subs[i + 1].start

        return new_subs

    def short_subtitles_no_separation(self, subs:list):
        word_highlight = self.return_if_highlight()
        new_subs = list()
        cur_word = ''
        cur_sub_list = []
        index = 1
        start_time, end_time = self.start_end_time(subs)

        for i, sub in enumerate(subs):
            last_iteration = len(subs) - 1 == i
            cur_word = f'{cur_word} {sub.text}'.strip()
            cur_sub_list.append(sub)

            next_word_len = len(cur_word) if last_iteration else len(cur_word) + 1 + len(subs[i+1].text)
            if self.word_max < next_word_len or last_iteration:

                cur_end = self.return_end_time_logic(last_iteration, end_time, subs, sub, i)

                new_subs = self.add_subtitle(cur_word, index, start_time, cur_end, new_subs, highlight_words=word_highlight, sub_list=cur_sub_list)
                cur_word = ''
                cur_sub_list = []
                if not last_iteration:
                    start_time = subs[i + 1].start

        return new_subs


    def return_if_highlight(self):
        if self.highlighter is None:
            return False
        else:
            return True

    def start_end_time(self, subs:list):
        if not self.fill_sub_times:
            return subs[0].start, subs[-1].end
        else:
            if self.Handler.duration is not None:
                return pysubs2.make_time(s=0), pysubs2.make_time(s=self.Handler.duration)
            else:
                raise ValueError('For the argument "fill_sub_times" an video has to be inputted via input_video or the subtitles have to generated from a audio/video.')

    def return_end_time_logic(self, last_iteration:bool, end_time:int, subs:list, sub:pysubs2.SSAEvent, i:int):
        if last_iteration:
            return end_time
        else:
            if self.fill_sub_times:
                return subs[i + 1].start
            else:
                return sub.end


    def shift_subs_time(self, subs:list):
        add_time = self.add_time
        for i, sub in enumerate(subs):
            if type(sub) == list:
                for _sub in sub:
                    _sub.shift(s=add_time)
            else:
                sub.shift(s=add_time)
        return subs


def generate_subs_simple(
        input,
        output,
    ):
    """
        Generates one-word-only subtitles from a media file with refined timestamps.

        This is a convenience wrapper that validates the input file type,
        transcribes it using the 'one_word_only' strategy, applies Whisper
        refinement for high precision, and saves the final result to disk.

        Args:
            input (str): Path to the source audio or video file.
            output (str): Destination path where the subtitle file (e.g., .ass, .srt)
                will be saved.

        Raises:
            ValueError: If the input file is not identified as a valid audio or
                video format by the `fleep` library.
        """
    # check for right type
    with open(input, "rb") as file:
        info = fleep.get(file.read(128))
    if not info.type == ['audio'] or info.type == ['video']:
        raise ValueError('The subtitles have to be generated from a audio/video.')
    else:
        sub_arg = sub_args(
            input=input,
            output=None,
            subtitle_type='one_word_only',
            fill_sub_times=False,
            whisper_refine=True
        )
        sub_file: pysubs2.SSAFile = Subtitle_Edit(sub_arg)()
        sub_file.save(output)


