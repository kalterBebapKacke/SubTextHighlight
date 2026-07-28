import dataclasses
import pysubs2
import copy
from . import appear
from .. import utils
from .. import docker_module
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

def strip_bad_color_tags(ass_text: str) -> str:
    """
    Removes malformed CSS-style color/alpha tags from ASS override blocks:
      - \c#RRGGBB   (invalid; should be \c&HBBGGRR&)
      - \1aN         (invalid; should be \1a&HXX&)
    """
    # Matches \c#FFFFFF, \c#ffffff, \c#000000, etc.
    text = re.sub(r'\\c#[0-9A-Fa-f]{6}', '', ass_text)

    # Matches \1a0, \1a255, \1aFF, etc. (bare number/hex after \1a)
    text = re.sub(r'\\1a[0-9A-Fa-f]+', '', text)

    return text

@dataclasses.dataclass
class Border:

    border_as_highlight: bool
    docker_config:utils.DockerConfig
    border_config:utils.BorderConfig

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
        dw = docker_module.DockerWrapper(self.docker_config)
        output : pysubs2.SSAFile = dw(
            ssa_file,
            self.border_config,
        )
        events = output.events

        logger.info('Finisehd with docker programm')
        logger.debug('Subtitles after Docker:')
        for event in events:
            logger.debug(event)

        # Remove the wrong tags and add a background style
        # TODO: Later fix with new script inside the docker
        events = self.post_process_subs(events)

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

    @staticmethod
    def post_process_subs(events:list[pysubs2.SSAEvent]):
        for event in events:
            if is_drawing_line(event.is_drawing):
                event.text = strip_bad_color_tags(event.text)
                event.style = 'BackgroundStyle'
        return events
