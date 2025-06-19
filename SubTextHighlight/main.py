import os
import datetime
import pysubs2
from Cython.Build.Dependencies import join_path
from .Highlight import Highlighter, highlight_args
from .Effects import Effects, effects_args
from . import utils

off_time = datetime.timedelta(seconds=0.025)

class sub_args(utils.args_styles):

    def __init__(self,
        input: str,
        output: str,
        subtitle_type: str = 'one_word_only',  # one_word_only, join, separate_on_period, appear
        word_max: int = 11,
        add_time:float = 0,
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



class Subtitle_Edit:

    def __init__(self,
                 args_sub_edit_:sub_args,
                 args_highlight:highlight_args | None = None,
                 args_effects: effects_args | None =None,
                ):

        # args
        if args_sub_edit_ is not None:
            self.args = args_sub_edit_
        else:
            self.args = sub_args()

        # Style
        self.main_style = self.args.return_style()

        # Needed Variables for the formatting
        self.word_max = self.args.word_max
        self.subtitle_type = self.args.subtitle_type
        self.add_time = self.args.add_time
        self.path_to_srt = self.args.input
        self.output = self.args.output

        # Highlighters
        self.args_highlight = args_highlight

        if args_highlight is None:
            self.if_highlight = False
        else:
            self.if_highlight = True
            self.highlighter = Highlighter(args_highlight, self.main_style, self.subtitle_type)

        # Effects

        if args_effects is None:
            self.if_effects = False
        else:
            self.if_effects = True
            self.effects = Effects(args_effects)



    def __call__(self):
        sub_file = pysubs2.load(self.path_to_srt)
        sub_file.styles["MainStyle"] = self.main_style

        if self.if_highlight:
            sub_file.styles["Highlight"] = self.highlighter.return_highlighted_style(self.main_style)

        subs = sub_file.events

        # create subtitles
        if self.subtitle_type == 'one_word_only':
            subs = self.one_word_only(subs)
        elif self.subtitle_type == 'separate_on_period':
            subs = self.short_subtitles(subs)
        elif self.subtitle_type == 'join':
            subs = self.short_subtitles_no_separation(subs)
        elif self.subtitle_type == 'appear':
            if not self.if_highlight:
                self.highlighter = Highlighter(highlight_args(), self.main_style, self.subtitle_type)
                sub_file.styles["Highlight"] = self.highlighter.return_highlighted_style(self.main_style)
            subs = self.short_subtitles_no_separation(subs)
            subs = self.appear(subs)


        # shift time
        subs = self.shift_subs_time(subs)

        # edit
        if self.if_effects is True:
            subs  = self.effects(subs)


        # build and save
        subs = self.build_finished_subs(subs)
        sub_file.events = subs
        self.interpret_output(self.output, sub_file)

    def interpret_input(self, input):
        if type(input) is dict[str, any] or type(input) is list[dict[str, any]]:
            return pysubs2.load_from_whisper(input)
        elif type(input) is str:
            pass
            # implement check for sub file and audio

    def interpret_output(self, output, output_file:pysubs2.SSAFile):
        if type(output) is str:
            sub_file.save(output)
        elif output is None:
            return output_file

        
    def add_subtitle(self, cur_word:str, index:int, start, end, all_subs:list, highlight_words:bool=False, sub_list:list=()):
        if highlight_words is True:
            return self.highlighter(cur_word, start, end, all_subs, sub_list)
        else:
            all_subs.append(pysubs2.SSAEvent(start=start, end=end, text=cur_word.strip(), style="MainStyle"))
            return all_subs

    def short_subtitles(self, subs:list):
        new_subs = list()
        cur_word = ''
        index = 1
        start_time = 0
        last_end = subs[0].end

        for sub in subs:
            if len(cur_word) + len(sub.text) + 1 < self.word_max:
                cur_word = cur_word + sub.text + ' '
            else:
                end_time = sub.start
                #duration = end_time - start_time
                new_subs = self.add_subtitle(cur_word, index, start_time, sub.end, new_subs)
                cur_word = sub.text + ' '
                index += 1
                start_time = end_time

            if cur_word.__contains__('.') or cur_word.__contains__('?') or cur_word.__contains__('!'):
                #end_time = sub.end+datetime.timedelta(seconds=0.45)
                new_subs = self.add_subtitle(cur_word, index, start_time, sub.end, new_subs)
                cur_word = ''
                index += 1
                start_time = sub.end
            #last_end = sub.end

        if cur_word != '':
            new_subs = self.add_subtitle(cur_word, index, start_time, subs[-1].end, new_subs)

        return new_subs

    def one_word_only(self, subs:list):
        new_subs = list()
        index = 1
        sub_start = 0

        for i, sub in enumerate(subs):
            if i != len(subs)-1:
                end_time = subs[i+1].start
            else:
                end_time = sub.end
            new_subs = self.add_subtitle(sub.text, index, sub_start, end_time, new_subs)
            sub_start = end_time
        return new_subs

    def short_subtitles_no_separation(self, subs:list):
        word_highlight = self.if_highlight
        new_subs = list()
        cur_word = ''
        cur_sub_list = []
        index = 1
        start_time = 0
        #last_end = subs[0].end

        for i, sub in enumerate(subs):
            #print(cur_word)
            if len(cur_word) + len(sub.text) + 1 < self.word_max:
                cur_word = cur_word + sub.text + ' '
                cur_sub_list.append(sub)
            else:
                end_time = sub.start
                new_subs = self.add_subtitle(cur_word, index, start_time, end_time, new_subs, highlight_words=word_highlight, sub_list=cur_sub_list)
                cur_word = sub.text + ' '
                start_time = end_time
                cur_sub_list = [sub]

        if cur_word != '':
            new_subs = self.add_subtitle(cur_word, index, start_time, subs[-1].end, new_subs, highlight_words=word_highlight, sub_list=cur_sub_list)

        return new_subs

    def appear(self, subs:list):
        for sub_list in subs:
            for sub in sub_list:
                num_split = (sub.text.find(r'{\r}') + len(r'{\r}'))
                sub.text = sub.text[:num_split] + r'{\alpha&HFF}' +sub.text[num_split:] + r'{\r}'
        return subs



    def subs_cleanup(self, subs:list): #not working
        #last_end = subs[0].start
        for i, sub in enumerate(subs):
            cur_word = sub.text
            if (cur_word.__contains__('.') or cur_word.__contains__('?') or cur_word.__contains__('!')) and i + 1 != len(subs):
                check_sub = subs[i + 1]
                duration = sub.end.total_seconds() - sub.start.total_seconds()
                duration_check = check_sub.end.total_seconds() - check_sub.start.total_seconds()
                if duration < 0.35:
                    new_duration =  datetime.timedelta(seconds=duration_check) - datetime.timedelta(seconds=0.35)
                    if not new_duration.total_seconds() < 0:
                        subs[i + 1].start = subs[i + 1].end - new_duration
                        sub.end = sub.end + new_duration
        for i, sub in enumerate(subs):
            if i + 1 != len(subs):
                check_sub = subs[i + 1]
                if (check_sub.start.total_seconds() - sub.end.total_seconds()) < 0:
                    new_time = (check_sub.start + sub.end).total_seconds() / 2
                    sub.end = datetime.timedelta(seconds=new_time) - off_time
                    subs[i + 1].start = datetime.timedelta(seconds=new_time)
        return subs

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



if __name__ == "__main__":
    path = join_path('..', 'content', '930', 'srt_file.srt')
    subs = [x for x in pysubs2.load(path)]
    sub_file = pysubs2.load(path)
    highlight_color = '0000000000'
    print(sub_file.events)
    for sub in subs:
        pass
