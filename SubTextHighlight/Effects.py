import os
from os import fdatasync
from . import Highlight
from . import docker_wrapper
from . import utils
import copy

import pysubs2

class effects_args:

    def __init__(self,
        fade:tuple[float, float] = (0.0, 0.0), # first is fadeIn and second is fadeOut
        appear:bool = False,
        args_border:docker_wrapper.base.args_border | None = None,
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
        self.args_border = args_border


class Effects:

    def __init__(self, args:effects_args):
        self.args = args

    def logic_highlighter(self, highlighter:Highlight.Highlighter, sample_highlighter:Highlight.Highlighter):
        # sees whether the highlighter already exists as it is needed for some effects
        if self.args.appear:
            # sets highlighter if it does not already exist
            if highlighter is not None:
                new_highlighter = highlighter
            else:
                new_highlighter = sample_highlighter
            return new_highlighter
        else:
            return highlighter

    def __call__(self, subs:list, sub_file:pysubs2.SSAFile):
        if self.args.fade_out_duration != 0 and self.args.fade_in_duration != 0:
            subs = self.fade(subs)
        if self.args.appear:
            subs = self.appear(subs)

        if self.args.args_border is not None:
            # Implement rounded borders
            self.rounded_borders(subs, sub_file)
        return subs

    def fade(self, subs):
        for i, sub in enumerate(subs):
            sub.fade_in =  fr'{{\fad({self.args.fade_in_duration},0)}}'
            sub.fade_out = fr'{{\fad(0,{self.args.fade_out_duration})}}'
        return subs

    def appear(self, subs:list):
        styles = (r'{\alpha&HFF}', '')
        for sub in subs:
            sub.appear_style = styles
        return subs

    def rounded_borders(self, subs:list, sub_file:pysubs2.SSAFile):
        # TODO: Build Subs and upgrade builder
        # TODO: Implement function
        builder = utils.subs_builder()

        # check whether res is set, else raise error
        if not utils.check_for_PlayRes(sub_file):
            raise RuntimeError('The subtitle file does not contain a Resolution. For the right scaling of the subtitles a input with a video resolution has to be set.')

        # build part of the background without the highlighting split (if one is given)
        text_only_subs = builder(subs, 'text_only')

        # make copy of saafile and replace events with text only
        sub_file_copy = copy.deepcopy(sub_file)
        sub_file_copy.events = text_only_subs

        # start the docker wrapper and execute the script
        # only execute on the part, that becomes the background
        dw = docker_wrapper.main.DockerWrapper()
        output : pysubs2.SSAFile = dw(
            input_ass=sub_file_copy,
            args_border=self.args.args_border,
            _traceback=True,
            cleanup=True,
        )
        print(output)
        print(output.to_string('ass'))
        print()

        # filter out text from background

        # combine both text and background

        # return new subtitles list


