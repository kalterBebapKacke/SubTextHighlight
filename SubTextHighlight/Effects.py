from . import docker_wrapper
from . import utils
import copy
from .subtitles import subtitle_render
import pysubs2


class Effects:

    def __init__(self,
                 fade_in_duration:float = 0,
                 fade_out_duration:float = 0,
                 appear:bool = False,
                 rounded_border:bool = False,
                 border_as_highlight:bool = False,
                 args_border:docker_wrapper.base.args_border | None = None,
                 verbose:bool = False,
                 traceback:bool = False
                 ):
        self.fade_in_duration = fade_in_duration
        self.fade_out_duration = fade_out_duration
        self.appear = appear
        self.rounded_border = rounded_border
        self.border_as_highlight = border_as_highlight
        self.args_border = args_border
        self.verbose = verbose
        self.traceback = traceback

    def __call__(self, subs:list, sub_file:pysubs2.SSAFile):
        if self.appear:
            subs = self._appear(subs)

        if self._borders():
            subs = self.rounded_borders(subs, sub_file)
        return subs

    def _borders(self):
        if self.border_as_highlight:
            return True
        if self.rounded_border:
            return True
        return False

    def fade(self, subs):
        for i, sub in enumerate(subs):
            sub.fade_in =  self.fade_in_duration
            sub.fade_out = self.fade_out_duration
        return subs

    def set_fade(self, subs:list[subtitle_render.SAAEventBuilder]):
        for sub in subs:
            sub.set_fade(self.fade_in_duration, self.fade_out_duration)
        return subs

    def _appear(self, subs:list):
        styles = (r'{\alpha&HFF}', '')
        for sub in subs:
            sub.appear_style = styles
        return subs

    def rounded_borders(self, subs:list, sub_file:pysubs2.SSAFile):
        # check whether res is set, else raise error
        if not utils.is_subfile_resolution_set(sub_file):
            raise RuntimeError('The subtitle file does not contain a Resolution. For the right scaling of the subtitles a input with a video resolution has to be set.')

        # Check if Borders are used as highlight and build part of the background (if one is given)
        with subtitle_render.SubtitlePipeline(subs) as pipeline:
            use_subs, depth = pipeline.render_with_depth()


        # if borders as highlight, replace highlight with appear
        if self.border_as_highlight:
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
        dw = docker_wrapper.main.DockerWrapper(self.args_border.force_install)
        output : pysubs2.SSAFile = dw(
            input_ass=sub_file_copy,
            args_border=self.args_border,
            _traceback=self.traceback,
            cleanup=True,
            verbose=self.verbose,
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
                new_backgrounds = segmented_subs[segment_index][1:]
                subs[i].add_background(new_backgrounds)
                segment_index += 1

        for sub in subs:
            print(sub.text)
            print(sub.backgrounds)
            print(sub())
        return subs