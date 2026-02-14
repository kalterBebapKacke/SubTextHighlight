import pysubs2
from .utils import dprint, advanced_SAA_Events
from .Highlight import Highlighter
from .Effects import Effects, effects_args
from . import utils


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
                    args,
                    highlighter:Highlighter | None,
                    effects:Effects | None,
                ):

        # args
        self.args = args
        self.highlighter = highlighter
        self.effects = effects

        # Needed Variables for the formatting
        self.word_max = self.args.word_max
        self.subtitle_type = self.args.subtitle_type
        self.add_time = self.args.add_time
        self.fill_sub_times = self.args.fill_sub_times
        self.duration = self.args.Handler.duration

        # Set builder
        self.builder = utils.subs_builder()



    def __call__(self, sub_file:pysubs2.SSAFile=None):
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
        return sub_file

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
            if self.duration is not None:
                return pysubs2.make_time(s=0), pysubs2.make_time(s=self.duration)
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



