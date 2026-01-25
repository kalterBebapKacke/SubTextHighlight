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
            Configuration for visual subtitle effects and animations.

            This class defines how subtitles transition onto the screen and whether
            additional decorative elements, like borders, are applied.

            Attributes:
                fade_in_duration (float): Time in seconds for the subtitle to transition
                    from transparent to opaque.
                fade_out_duration (float): Time in seconds for the subtitle to transition
                    from opaque to transparent.
                appear (bool): If True, words in a sequence stay on screen as new ones
                    appear (cumulative display). If False, words typically replace
                    one another.
                args_border (docker_wrapper.base.args_border, optional): Configuration
                    object for border-specific styling and effects.
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
        if not utils.is_subfile_resolution_set(sub_file):
            raise RuntimeError('The subtitle file does not contain a Resolution. For the right scaling of the subtitles a input with a video resolution has to be set.')

        # Check if appear is active and if so throw an expectation
        if self.args.args_border.use_borders_as_highlight and self.args.appear:
            raise RuntimeError('Cant use borders as highlighted subtitles and the appear at the same time.')

        # Check if Borders are used as highlight and build part of the background (if one is given)
        use_subs, depth = builder(subs, return_depth=True)


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
        dw = docker_wrapper.main.DockerWrapper(self.args.args_border.force_install)
        output : pysubs2.SSAFile = dw(
            input_ass=sub_file_copy,
            args_border=self.args.args_border,
            _traceback=True,
            cleanup=True,
        )

        events = output.events

        # fix the fad tag issue
        segmented_subs = utils.fix_fad_issue(events)

        # layer the subs
        for sub in subs:
            sub.layer = 1

        # merge subs and backgrounds
        #subs[index].add_background(segment[1:])
        segment_index = 0
        for i, cur in enumerate(depth):
            for x in range(cur):
                subs[i].add_background(segmented_subs[segment_index][1:])
                segment_index += 1

        return subs