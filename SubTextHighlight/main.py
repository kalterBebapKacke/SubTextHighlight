import os
import datetime
import pysubs2
from Cython.Build.Dependencies import join_path
from .utils import dprint
from .Highlight import Highlighter, highlight_args
from .Effects import Effects, effects_args
from . import utils
import fleep
import stable_whisper

off_time = datetime.timedelta(seconds=0.025)

class sub_args(utils.args_styles):

    def __init__(self,
        input: str | dict[str, any] | list[dict[str, any]] | stable_whisper.result.WhisperResult,
        output: str | None,
        input_video: str | None = None,
        subtitle_type: str = 'one_word_only',  # one_word_only, join, separate_on_period, appear
        word_max: int = 11,
        add_time:float = 0,
        fill_sub_times:bool = True,
        whisper_model: str = 'medium.en',
        whisper_device: str = 'cpu',
        whisper_refine:bool = False,
        fontname: str = 'Arial',
        fontsize: float | int = 24,
        primarycolor: pysubs2.Color | str = pysubs2.Color(255, 255, 255),
        backcolor: pysubs2.Color | str = pysubs2.Color(0, 0, 0),
        secondarycolor: pysubs2.Color | str = pysubs2.Color(0, 0, 0, ),  # Black for border/shadow
        outlinecolor: pysubs2.Color | str = pysubs2.Color(0, 0, 0),
        tertiarycolor: pysubs2.Color | str = pysubs2.Color(0, 0, 0),  # Black outline
        outline: float | int = 1,
        spacing: float | int = 0.75,
        shadow: float | int = 0,
        alignment: int = 5,
        bold: bool = True,
        angle: float = 0.0,
        borderstyle: int = 1,
        italic: bool = False,
        underline: bool = False
        ):
        """
            Configuration for subtitle generation.

            Attributes:
                input (str): Path to the input to process.
                output (str): Path where the generated subtitles will be saved.
                input_video (str): Path to the input video, in which generated subtitles could be burned in.
                subtitle_type (str): Subtitle formatting style. One of:
                    - 'one_word_only': One word per subtitle.
                    - 'join': Joins all words into subtitles segments with respect to the word_max parameter.
                    - 'separate_on_period': Splits subtitles at sentence boundaries.
                word_max (int): Maximum words per subtitle segment (used only when subtitle_type is not 'one_word_only').
                add_time (float): Extra seconds to add to each subtitle's duration.
                fill_sub_times (bool):
                whisper_model (str) = Controls which whisper model is used if necessary.
                whisper_device (str) = Controls which device is used for whisper if necessary.
                whisper_refine (bool) = Whether the results are refined for better timestamps.
                The rest of the attributes inherit from the utils.args_styles.
            """
        super().__init__(
            fontname,
            fontsize,
            primarycolor,
            backcolor,
            secondarycolor,  # Black for border/shadow
            outlinecolor,   # Black outline
            tertiarycolor,
            outline,
            spacing,
            shadow,
            alignment,
            bold,
            angle,
            borderstyle,
            italic,
            underline
        )

        self.subtitle_type: str = subtitle_type # one_word_only, join, separate_on_period
        self.word_max: float = word_max
        self.add_time = add_time
        self.input = input
        self.output = output
        self.input_video = input_video
        self.whisper_model: str = whisper_model
        self.whisper_device: str = whisper_device
        self.fill_sub_times: bool = fill_sub_times
        self.whisper_refine: bool = whisper_refine



class Subtitle_Edit:

    def __init__(self,
                 args_sub_edit_:sub_args,
                 args_highlight:highlight_args | None = None,
                 args_effects: effects_args | None = None,
                ):

        # args
        self.args = args_sub_edit_

        # Style
        self.main_style = self.args.return_style()

        # Needed Variables for the formatting
        self.word_max = self.args.word_max
        self.subtitle_type = self.args.subtitle_type
        self.add_time = self.args.add_time
        self.input = self.args.input
        self.input_video = self.args.input_video
        self.output = self.args.output
        self.whisper_model= self.args.whisper_model
        self.whisper_device= self.args.whisper_device
        self.fill_sub_times = self.args.fill_sub_times
        self.whisper_refine = self.args.whisper_refine

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
        sub_file = self.interpret_input(self.input)
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
            subs  = self.effects(subs)

        # build and save
        subs = self.build_finished_subs(subs)
        sub_file.events = subs
        return self.interpret_output(self.output, sub_file)

    def interpret_input(self, input):
        if type(input) == stable_whisper.result.WhisperResult:
            subs_str = utils.return_whisper_result(input)
            return pysubs2.SSAFile.from_string(subs_str)
        elif type(input) is dict[str, any] or type(input) is list[dict[str, any]]:
            return pysubs2.load_from_whisper(input)
        elif type(input) is str:
            file_extension = input.split('.')[-1]
            if file_extension == 'srt' or file_extension == 'ass':
                return pysubs2.load(input)
            else:
                with open(input, "rb") as file:
                    info = fleep.get(file.read(128))
                if info.type == ['audio'] or info.type == ['video']:
                    subs_str = utils.use_whisper(input, self.whisper_model, self.whisper_device, self.whisper_refine)
                    return pysubs2.SSAFile.from_string(subs_str)
                else:
                    return pysubs2.SSAFile.from_string(input)

    def interpret_output(self, output, output_file:pysubs2.SSAFile):
        if type(output) is str:
            file_extension = output.split('.')[-1]
            if file_extension == 'ass':
                output_file.save(output)
            elif self.input_video is not None:
                with open(self.input_video, "rb") as file:
                    info = fleep.get(file.read(128))
                if info.type == ['video']:
                    utils.add_subtitles_with_ffmpeg(self.input_video, output, output_file)
            else:
                raise ValueError('Output format has to be a either ".ass" or a video type')
        elif output is None:
            return output_file

    def add_subtitle(self, cur_word:str, index:int, start, end, all_subs:list, highlight_words:bool=False, sub_list:list=()):
        if highlight_words is True:
            return self.highlighter(cur_word, start, end, all_subs, sub_list)
        else:
            all_subs.append(pysubs2.SSAEvent(start=start, end=end, text=cur_word.strip(), style="MainStyle"))
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
            # check whether the input is an audio or video
            with open(self.input, "rb") as file:
                info = fleep.get(file.read(128))
            if info.type == ['video'] or info.type == ['audio']:
                # main part
                end_time = utils.get_duration(self.input)
                return pysubs2.make_time(s=0), pysubs2.make_time(s=end_time)
            # if not check if input video exists
            elif self.input_video is not None:
                # check if input video is audio or video
                with open(self.input_video, "rb") as file:
                    info = fleep.get(file.read(128))
                if info.type == ['video']:
                    # main part
                    end_time = utils.get_duration(self.input_video)
                    return pysubs2.make_time(s=0), pysubs2.make_time(s=end_time)
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

    def build_finished_subs(self, subs):
        new_subs = list()
        for sub in subs:
            if type(sub) == list:
                new_subs.extend(sub)
            else:
                new_subs.append(sub)
        return new_subs

