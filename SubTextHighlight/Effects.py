import os
from os import fdatasync
from . import Highlight

import pysubs2

class effects_args:

    def __init__(self,
        fade:tuple[float, float] = (0.0, 0.0), # first is fadeIn and second is fadeOut
        appear:bool = False,
                 ):
        """
        fade: Controls the fade-in and fade-out durations.
        - fade[0]: Duration of fade-in (in seconds).
        - fade[1]: Duration of fade-out (in seconds).
        Defaults to (0.0, 0.0) — no fading.
        - 'appear': Words accumulate as they appear.
        """
        self.fade_in_duration = fade[0]
        self.fade_out_duration = fade[1]
        self.appear = appear


class Effects:

    def __init__(self, args:effects_args):
        self.args = args

    def logic_highlighter(self, highlighter:Highlight.Highlighter, sample_highlighter:Highlight.Highlighter):
        # sees whether the highlighter already exists as it is needed for some effects
        if self.args.appear:
            # sets highlighter if it doesnt already exists
            if highlighter is not None:
                new_highlighter = highlighter
            else:
                new_highlighter = sample_highlighter
            return new_highlighter
        else:
            return highlighter

    def __call__(self, subs:list):
        if self.args.fade_out_duration != 0 and self.args.fade_in_duration != 0:
            subs = self.fade(subs)
        if self.args.appear:
            subs = self.appear(subs)
        return subs

    def fade(self, subs):
        for i, sub in enumerate(subs):
            if type(sub) == list:
                sub[0].text = fr'{{\fad({self.args.fade_in_duration},0)}}{sub[0].text}'
                sub[-1].text = fr'{{\fad(0,{self.args.fade_out_duration})}}{sub[-1].text}'
            else:
                sub.text = fr'{{\fad({self.args.fade_in_duration},{self.args.fade_out_duration})}}{sub.text}'
        return subs

    def appear(self, subs:list):
        for sub_list in subs:
            for i, sub in enumerate(sub_list):
                # split text and put them back so that the second half is transparent
                num_split = (sub.text.find(r'{\r}') + len(r'{\r}'))
                if sub.text[num_split:].strip() != '':
                    sub.text = sub.text[:num_split] + r'{\alpha&HFF}' + sub.text[num_split:] + r'{\r}'
        return subs
