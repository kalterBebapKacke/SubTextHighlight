import dataclasses
import pysubs2
import copy
from . import appear
from . import docker_wrapper
import re
import logging
logger = logging.getLogger(__name__)

def is_drawing_line(line):
    # Check if line contains drawing mode tag \p1 or higher
    # \p0 means text mode, \p1 or higher means drawing mode
    drawing_pattern = r'\\p[1-9]'

    if re.search(drawing_pattern, line):
        return True

    return False

@dataclasses.dataclass
class Border:

    border_as_highlight: bool
    force_install: bool
    args_border: docker_wrapper.base.args_border | None
    traceback: bool
    verbose: bool

    def render(self, sub_file):
        # check whether res is set, else raise error
        #if not utils.is_subfile_resolution_set(sub_file):
        #    raise RuntimeError('The subtitle file does not contain a Resolution. For the right scaling of the subtitles a input with a video resolution has to be set.')

        # make a copy to process it for the background, so that the original subs are not changed for the layering at the end
        sub_file_copy = copy.deepcopy(sub_file)

        # Check if Borders are used as highlight and build part of the background (if one is given)
        with sub_file_copy.return_render_object() as pipeline:
            if not self.border_as_highlight:
                use_subs, depth = pipeline.render_with_depth()
            else:
                use_subs = pipeline.render_highlights_only()
                depth = pipeline.dimensions_tracker

        logger.debug('Sub to render in Docker:')
        for sub in use_subs:
            logger.debug(sub)

        ssa_file = sub_file_copy.return_ssa_file()
        ssa_file.events = use_subs

        # start the docker wrapper and execute the script
        # only execute on the part, that becomes the background
        dw = docker_wrapper.main.DockerWrapper(self.force_install)
        output : pysubs2.SSAFile = dw(
            input_ass=ssa_file,
            args_border=self.args_border,
            _traceback=self.traceback,
            cleanup=True,
            verbose=self.verbose,
        )
        events = output.events

        logger.info('Finisehd with docker programm')
        logger.debug('Subtitles after Docker:')
        for event in events:
            logger.debug(event)

        segmented_subs = self.segment_subs(events)

        # layer the subs
        logger.debug('Layering subtitles')
        self.layer_subs(sub_file)

        # Now start working on the real subs
        # merge subs and backgrounds
        subs = sub_file.return_events()
        segment_index = 0
        for i, cur in enumerate(depth):
            for x in range(cur):
                new_backgrounds = segmented_subs[segment_index][1:]
                subs[i].add_background(new_backgrounds)
                segment_index += 1
        sub_file.set_events(subs)
        return sub_file

    def segment_subs(self, events: list):
        result = []
        for event in events:
            if not is_drawing_line(event.text):
                result.append([event])
            else:
                result[-1].append(event)
        return result

    def layer_subs(self, sub_file):
        events = sub_file.return_events()
        for event in events:
            event.set_layer(1)
        sub_file.set_events(events)