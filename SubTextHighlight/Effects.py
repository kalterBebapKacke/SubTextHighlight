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
        # TODO: Rework for appear
        # TODO: Highlight with rounded borders
        builder = utils.subs_builder()

        # check whether res is set, else raise error
        if not utils.check_for_PlayRes(sub_file):
            raise RuntimeError('The subtitle file does not contain a Resolution. For the right scaling of the subtitles a input with a video resolution has to be set.')

        # build part of the background without the highlighting split (if one is given)
        text_only_subs = builder(subs, 'text_only')



        ####### TEST PURPOSE
        subs[0].text = 'Test.        Test.'
        subs[1].text = '      '
        ####### TEST PURPOSE





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
        # filter out text from background and give it the right timing
        background = list()
        events = output.events
        for event in events:
            if utils.is_drawing_line(event.text):
                new_event = subs[0].return_background_copy()
                new_event.start, new_event.end = event.start, event.end
                new_event.text = event.text
                background.append(new_event)

        # Put the subs one layer up to be in front of the background
        for sub in subs:
            sub.layer = 1

        # combine both text and background
        subs.extend(background)

        # return new subtitles list
        return subs