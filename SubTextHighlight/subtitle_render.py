import pysubs2
from dataclasses import dataclass, field
from typing import Self
import copy

from build.lib.SubTextHighlight.utils import return_whisper_result


@dataclass
class HighlightEntry:
    index_start: int
    index_end: int
    start: int
    end: int

@dataclass(frozen=True)
class FadeSpec:
    fade_in: float
    fade_out: float

    @property
    def is_active(self) -> bool:
        return self.fade_in != 0 or self.fade_out != 0

    def for_segment(self, is_first: bool, is_last: bool) -> str:
        if is_first and is_last:
            return f'{{\\fad({self.fade_in},{self.fade_out})}}'
        if is_first:
            return f'{{\\fad({self.fade_in},0)}}'
        if is_last:
            return f'{{\\fad(0,{self.fade_out})}}'
        return ''

class SAAEventBuilder:
    def __init__(self, event: pysubs2.SAAEvent):
        self._event = event
        self._highlights: list[HighlightEntry] = []
        self._backgrounds: list = []
        self._fade: FadeSpec | None = None
        self._highlight_style: tuple[str, str] = ('', '')
        self._appear_style: str | None = None
        self._layer: int = 0
        self._style: str = "MainStyle"

    @property
    def text_list(self):
        return self._event.text.split()

    def set_fade(self, fade_in: float, fade_out: float) -> Self:
        self._fade = FadeSpec(fade_in, fade_out)
        return self

    def set_highlight_style(self, prefix: str, suffix: str) -> Self:
        self._highlight_style = (prefix, suffix)
        return self

    def set_appear_style(self, style: str) -> Self:
        self._appear_style = style
        return self

    def set_layer(self, layer: int) -> Self:
        self._layer = layer
        return self

    def set_start(self, start: int) -> Self:
        self._event.start = start
        return self

    def set_end(self, end: int) -> Self:
        self._event.end = end
        return self

    def add_highlight(self, index_start: int, index_end: int,
                      start: int, end: int) -> Self:
        self._highlights.append(
            HighlightEntry(index_start, index_end, start, end)
        )
        return self

    def add_background(self, background: list) -> Self:
        self._backgrounds.append(background)
        return self

    def build(self) -> list[pysubs2.SSAEvent]:
        # render logic lives here, not on the event

        if self._highlights.__len__() == 0:
            return self.build_single_sub()
        else:
            return self.build_highlighted_subs()

    def build_single_sub(self):
        text = copy.copy(self._event.text)

        if self._fade.is_active:
            fade = self._fade.for_segment(True, True)
            text = fade[0] + text

        return_subs = [self.build_event(text)]

        if self.backgrounds != ():
            for background in self.backgrounds:
                return_subs.extend(background)

        return return_subs

    def build_highlighted_subs(self):
        return_subs = []

        # If appear is true, set the highlight styles
        if self._appear_style is not None:
            highlight_style = ['', self._appear_style[0]]
        else:
            highlight_style = self._highlight_style

        # Build the subs
        max_iterations = len(self._highlights) - 1

        for i, entry in enumerate(self._highlights):
            # build the text with hightlighting marks
            text = str(' '.join(self.text_list[0:entry.index_start])) + str(highlight_style[0]).strip() + str(' '.join(self.text_list[entry.index_start:entry.index_end + 1])) + str(highlight_style[1]).strip() + str(' '.join(self.text_list[entry.index_end + 1:]))
            if self._fade.is_active:
                fade = self._fade.for_segment(i == 0, i == max_iterations)
                text = fade[0] + text

            return_subs.append(self.build_event(text.strip()))

            # add backgrounds to the subs
            if self.backgrounds != ():
                return_subs.extend(self.backgrounds[i])

        return return_subs

    def build_event(self, text: str):
        event = pysubs2.SSAEvent(
            text=text,
            start=self._event.start,
            end=self._event.end,
            style=self._style,
            layer=self._layer
        )
        return event




