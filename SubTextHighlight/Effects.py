import os
from os import fdatasync

import pysubs2

class effects_args:

    def __init__(self,
        fade:tuple[float, float] = (0.0, 0.0) # first is fadeIn and second is fadeOut
                 ):
        """
        fade: Controls the fade-in and fade-out durations.
        - fade[0]: Duration of fade-in (in seconds).
        - fade[1]: Duration of fade-out (in seconds).
        Defaults to (0.0, 0.0) — no fading.
        """
        self.fade_in_duration = fade[0]
        self.fade_out_duration = fade[1]


class Effects:

    def __init__(self, args:effects_args):
        self.args = args

    def __call__(self, subs):
        if self.args.fade_out_duration != 0 and self.args.fade_in_duration != 0:
            subs = self.fade(subs)
        else:
            subs = subs
        return subs

    def fade(self, subs):
        for i, sub in enumerate(subs):
            if type(sub) == list:
                sub[0].text = fr'{{\fad({self.args.fade_in_duration},0)}}{sub[0].text}'
                sub[-1].text = fr'{{\fad(0,{self.args.fade_out_duration})}}{sub[-1].text}'
            else:
                sub.text = fr'{{\fad({self.args.fade_in_duration},{self.args.fade_out_duration})}}{sub.text}'
        return subs
