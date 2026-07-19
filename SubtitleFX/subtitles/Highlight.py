from .subtitle_render import SAAEventBuilder
import logging
logger = logging.getLogger(__name__)

class Highlighter:

    def __init__(self, highlight_char_max: int):
        self.highlight_char_max = highlight_char_max
        self.highlight_style = [r'{\rHighlight}', r'{\r}']

    def annotate(self, builder: SAAEventBuilder, sub_list: list, end) -> SAAEventBuilder:
        """
        Chunks sub_list into highlight windows and stamps
        each window onto the builder with timing.
        """
        builder.set_highlight_style(self.highlight_style[0], self.highlight_style[1])

        chunk_start_token = 0
        token_index = 0
        accumulated = ''
        start_time = None

        for i, sub in enumerate(sub_list):
            last = i == len(sub_list) - 1

            # a single timing entry can bundle more than one word (e.g. "It cost"),
            # so highlight windows must be indexed by word-token position - matching
            # SAAEventBuilder.text_list (event.text.split()) - not by sub_list position
            n_tokens = max(len(sub.text.split()), 1)
            chunk_end_token = token_index + n_tokens - 1

            accumulated += f' {sub.text}'
            if start_time is None:
                start_time = sub.start

            over_limit = self.highlight_char_max < len(accumulated) + len(sub.text)

            if over_limit or last:
                end_time = end if last else sub_list[i + 1].start
                builder.add_highlight(chunk_start_token, chunk_end_token, start_time, end_time)

                # reset window
                chunk_start_token = chunk_end_token + 1
                accumulated = ''
                start_time = None

            token_index += n_tokens

        return builder

def base_highlighter():
    return Highlighter(highlight_char_max=0)