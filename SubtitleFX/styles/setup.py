import pysubs2

from . import style_class
import dataclasses
from . import style_class

@dataclasses.dataclass
class style_setup:

    main_style:style_class.StyleConfig
    highlight_style: style_class.StyleConfig
    alignment:int
    highlighter_needed: bool

    def render(self, subs_file):
        _sub_file : pysubs2.SSAFile = subs_file.sub_file

        self.main_style.alignment = self.alignment
        _sub_file.styles["MainStyle"] = self.main_style.return_style()

        if self.highlighter_needed:
            self.highlight_style = self.highlight_style if self.highlight_style is not None else self.main_style
            self.highlight_style.alignment = self.alignment
            _sub_file.styles["Highlight"] = self.highlight_style.compare_style(self.main_style.return_style())

        return subs_file