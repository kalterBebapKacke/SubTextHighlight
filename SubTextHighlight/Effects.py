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
            subs = self.rounded_borders(subs, sub_file)
        return subs

    def fade(self, subs):
        for i, sub in enumerate(subs):
            sub.fade_in =  self.args.fade_in_duration
            sub.fade_out = self.args.fade_out_duration
        return subs

    def appear(self, subs:list):
        styles = (r'{\alpha&HFF}', '')
        for sub in subs:
            sub.appear_style = styles
        return subs

    def rounded_borders(self, subs:list, sub_file:pysubs2.SSAFile):
        builder = utils.subs_builder()

        # check whether res is set, else raise error
        if not utils.check_for_PlayRes(sub_file):
            raise RuntimeError('The subtitle file does not contain a Resolution. For the right scaling of the subtitles a input with a video resolution has to be set.')

        # Check if appear is active and if so throw an expectation
        if self.args.args_border.use_borders_as_highlight and self.args.appear:
            raise RuntimeError('Cant use borders as highlighted subtitles and the appear at the same time.')

        # Check if Borders are used as highlight and build part of the background (if one is given)
        use_subs = builder(subs)

        # if borders as highlight, replace highlight with appear
        if self.args.args_border.use_borders_as_highlight:
            highlight_style = subs[0].highlight_style
            for sub in use_subs:
                sub.text = r'{\alpha&HFF}' + sub.text
                sub.text = sub.text.replace(highlight_style[1], highlight_style[1] + r'{\alpha&HFF}')

        # make copy of ssafile
        sub_file_copy = copy.deepcopy(sub_file)
        sub_file_copy.events = use_subs

        #print(sub_file_copy.to_string('ass'))

        # start the docker wrapper and execute the script
        # only execute on the part, that becomes the background
        dw = docker_wrapper.main.DockerWrapper()
        output : pysubs2.SSAFile = dw(
            input_ass=sub_file_copy,
            args_border=self.args.args_border,
            _traceback=True,
            cleanup=True,
        )

        events = output.events

        # TODO: Implement better segments, so that the backgrounds appear next to the subs, not at the end of the file

        # fix the fad tag issue
        segmented_subs = utils.fix_fad_issue(events)

        # layer the subs
        for sub in subs:
            sub.layer = 1

        # merge subs and backgrounds
        for x in segmented_subs:
            subs.extend([utils.background_wrapper(event) for event in x[1:]])

        return subs