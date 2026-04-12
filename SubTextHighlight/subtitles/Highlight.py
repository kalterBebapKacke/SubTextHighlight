from .subtitle_render import SAAEventBuilder

class Highlighter:
    def __init__(self, highlight_word_max: int):
        self.highlight_word_min = highlight_word_max
        self.highlight_style = [r'{\rHighlight}', r'{\r}']

    def annotate(self, builder: SAAEventBuilder, sub_list: list, end) -> SAAEventBuilder:
        """
        Chunks sub_list into highlight windows and stamps
        each window onto the builder with timing.
        """
        builder.set_highlight_style(self.highlight_style[0], self.highlight_style[1])

        chunk_start_index = 0
        accumulated = ''
        start_time = None

        for i, sub in enumerate(sub_list):
            last = i == len(sub_list) - 1

            accumulated += f' {sub.text}'
            if start_time is None:
                start_time = sub.start

            over_limit = self.highlight_word_min < len(accumulated) + len(sub.text)

            if over_limit or last:
                end_time = end if last else sub_list[i + 1].start
                builder.add_highlight(chunk_start_index, i, start_time, end_time)

                # reset window
                chunk_start_index = i + 1
                accumulated = ''
                start_time = None

        return builder