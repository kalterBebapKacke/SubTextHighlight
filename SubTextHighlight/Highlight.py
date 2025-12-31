import os
import pysubs2
from . import utils
from .utils import dprint, advanced_SAA_Events
import dataclasses

@dataclasses.dataclass(kw_only=True)
class highlight_args(utils.args_styles):
    """
        Configuration arguments for subtitle text highlighting.

        Inherits visual styling properties from `utils.args_styles` and adds
        specific constraints for the highlighting engine.

        Attributes:
            highlight_word_max (int | None): The maximum number of words to be
                highlighted simultaneously in a single subtitle event.
                Defaults to 0 (no limit or disabled).
        """
    highlight_word_max: int | None = 0

    def replace_main_style(self, main_style: pysubs2.SSAStyle):
        self.fontname = self.fontname if self.fontname is not None else main_style.fontname
        self.fontsize = self.fontsize if self.fontsize is not None else main_style.fontsize
        self.primarycolor = self.primarycolor if self.primarycolor is not None else main_style.primarycolor
        self.backcolor = self.backcolor if self.backcolor is not None else main_style.backcolor
        self.secondarycolor = self.secondarycolor  if self.secondarycolor is not None else main_style.secondarycolor
        self.outlinecolor = self.outlinecolor if self.outlinecolor is not None else main_style.outlinecolor
        self.tertiarycolor = self.tertiarycolor if self.tertiarycolor is not None else main_style.tertiarycolor
        self.outline = self.outline if self.outline is not None else main_style.outline
        self.spacing = self.spacing if self.spacing is not None else main_style.spacing
        self.shadow = self.shadow if self.shadow is not None else main_style.shadow
        self.alignment = self.alignment if self.alignment is not None else main_style.alignment
        self.bold = self.bold if self.bold is not None else main_style.bold
        self.angle = self.angle if self.angle is not None else main_style.angle
        self.borderstyle = self.borderstyle if self.borderstyle is not None else main_style.borderstyle
        self.italic = self.italic  if self.italic is not None else main_style.italic
        self.underline = self.underline if self.underline is not None else main_style.underline


class Highlighter:

    def __init__(self, args:highlight_args, main_style: pysubs2.SSAStyle, subtitle_type:str):
        self.args = args
        self.args.replace_main_style(main_style)

        self.highlight_word_min = args.highlight_word_max

        # color, background, are possible values

        self.highlight_style = [r'{\rHighlight}', r'{\r}']

        self.subtitle_type = subtitle_type

    def __call__(self, cur_word: str, start, end, all_subs:list, sub_list: list):
        return_subs = list()
        highlighted_words = ''
        progress_in_words = ''
        cur_word += ' '
        last_index = 0

        sub_event = advanced_SAA_Events(text=cur_word, start=start, end=end, style="MainStyle", highlight_style=self.highlight_style)

        #dprint(sub_list)

        for i, sub in enumerate(sub_list):
            last_iteration = len(sub_list) - 1 == i

            if (self.highlight_word_min < len(highlighted_words) + len(sub.text)) or last_iteration:
                highlighted_words += f' {sub.text}'
                highlighted_words = highlighted_words.strip()

                progress_in_words = progress_in_words.strip()

                if not last_iteration:
                    end_time = sub_list[i + 1].start
                else:
                    end_time = end

                if start is None:
                    start = sub.start

                #return_subs.append(pysubs2.SSAEvent(start=start, end=end_time, text=new_cur_word.strip(), style="MainStyle"))
                sub_event.add_highlight_entry(last_index, i, start, end_time)

                last_index = i + 1
                highlighted_words = ''
                start = None
                progress_in_words += f' {sub.text}'
            else:
                highlighted_words += f' {sub.text}'
                progress_in_words += f' {sub.text}'
                if start is None:
                    start = sub.start

        #all_subs.append(return_subs)
        all_subs.append(sub_event)
        return all_subs

    def return_highlighted_style(self, style:pysubs2.SSAStyle):
        return self.args.return_style()

    def background_back(self):
        # return [r'{\3c&H000000&\4c&H0000FF&\4a&H40&\bord5\shad0\be1}', r'{\r}']
        return [r'{\c&H000000&\3c&HFFFF00&\bord5}', r'{\r}']  # {\c&H000000&\3c&HFFFF00&\bord8}

    def _replace(self, to_replace:str, new_word:str, progress_in_word:str):
        to_replace = to_replace.replace(progress_in_word, '', 1)
        if new_word[0] == ' ':
            _new = fr' {self.highlight_style[0]}{new_word.strip()}{self.highlight_style[1]} '
        else:
            _new = fr'{self.highlight_style[0]}{new_word.strip()}{self.highlight_style[1]} '

        highlighted_part = to_replace.replace(new_word, _new, 1)
        return progress_in_word + highlighted_part

    def highlight_background(self, subs):
        return_subs = list()
        background_style = self.background_back()
        for sub in subs:
            copy_subs = [x.copy() for x in sub]
            sub = self.replace_junk_styles(sub)
            for copy_sub in copy_subs:
                copy_sub.layer = 1
                for i, style in enumerate(background_style):
                    copy_sub.text = copy_sub.text.replace(self.highlight_style[i], style)
            return_subs.append(sub)
            return_subs.append(copy_subs)
        return return_subs

    def replace_junk_styles(self, subs:list):
        for sub in subs:
            for x in self.highlight_style:
                sub.text = sub.text.replace(x, '')
        return subs