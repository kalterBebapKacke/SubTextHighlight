import pysubs2
from dataclasses import dataclass, field
from typing import Self
import copy
import logging
import time
import os

logger = logging.getLogger(__name__)

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
    def __init__(self, event: pysubs2.SSAEvent):
        self._event = event
        self._highlights: list[HighlightEntry] = []
        self._backgrounds: list = []
        self._fade: FadeSpec | None = None
        self._highlight_style: tuple[str, str] = ('', '')
        self._appear_style: str | None = None
        self._layer: int = 0
        self._style: str = "MainStyle"

        logger.debug(f"Created SAAEventBuilder for event: {self._event.start}ms-{self._event.end}ms, text: {len(self.text_list)} words")
        logger.debug(f"Initial config: highlights={len(self._highlights)}, fade={self._fade}, style={self._style}, layer={self._layer}")

    def __str__(self) -> str:
        return f"SAAEventBuilder(event={self._event}, highlights={self._highlights}, backgrounds={self._backgrounds}, fade={self._fade}, highlight_style={self._highlight_style}, appear_style={self._appear_style}, layer={self._layer})"

    @property
    def text_list(self):
        return self._event.text.split()

    def set_fade(self, fade_in: float, fade_out: float) -> Self:
        self._fade = FadeSpec(fade_in, fade_out)
        logger.info(f"Config fade to: in={fade_in}s, out={fade_out}s")
        return self

    def set_highlight_style(self, prefix: str, suffix: str) -> Self:
        self._highlight_style = (prefix, suffix)
        logger.info(f"Config highlight style: prefix='{prefix}', suffix='{suffix}'")
        return self

    def set_appear_style(self, style: str) -> Self:
        self._appear_style = style
        logger.info(f"Config appear style: '{style}'")
        return self

    def set_layer(self, layer: int) -> Self:
        self._layer = layer
        logger.info(f"Config layer to: {layer}")
        return self

    def set_start(self, start: int) -> Self:
        self._event.start = start
        logger.info(f"Config start time to: {start}ms")
        return self

    def set_end(self, end: int) -> Self:
        self._event.end = end
        logger.info(f"Config end time to: {end}ms")
        return self

    def add_highlight(self, index_start: int, index_end: int,
                      start: int, end: int) -> Self:
        self._highlights.append(
            HighlightEntry(index_start, index_end, start, end)
        )
        logger.info(f"Added highlight: words[{index_start}:{index_end+1}] at {start}ms-{end}ms")
        return self

    def add_background(self, background: list) -> Self:
        self._backgrounds.append(background)
        logger.debug(f"Added background: {len(background)} event(s)")
        return self

    def build(self) -> list[pysubs2.SSAEvent]:
        start_time = time.time()
        logger.info(f"Building subtitle: event={self._event.start}ms-{self._event.end}ms, highlights={len(self._highlights)}, backgrounds={len(self._backgrounds)}")

        if self._highlights.__len__() == 0:
            logger.info("No highlights detected, building single-sub mode")
            result = self.build_single_sub()
        else:
            logger.info(f"Highlights detected: {len(self._highlights)} segments, building highlighted mode")
            result = self.build_highlighted_subs()

        elapsed = (time.time() - start_time) * 1000
        logger.debug(f"Build completed in {elapsed:.2f}ms, generated {len(result)} events")
        return result

    def build_single_sub(self):
        logger.info(f"build_single_sub: event text: {self._event.text!r}")
        text = copy.copy(self._event.text)

        if self._fade.is_active:
            fade = self._fade.for_segment(True, True)
            text = fade + text
            logger.debug(f"Applied fade effect: {fade!r}")
        else:
            logger.debug("No fade effect configured")

        return_subs = [self.build_event(text)]
        logger.debug(f"Base sub created with text: {text!r}")

        for background in self._backgrounds:
            logger.debug(f"Adding {len(background)} background event(s)")
            return_subs.extend(background)

        logger.info(f"build_single_sub completed: produced {len(return_subs)} event(s)")
        return return_subs

    def build_highlighted_subs(self):
        logger.info(f"build_highlighted_subs: {len(self._highlights)} highlight segments")
        return_subs = []

        # If appear is true, set the highlight styles
        if self._appear_style is not None:
            highlight_style = ['', self._appear_style]
            logger.info(f"Using appear style: {self._appear_style!r}")
        else:
            highlight_style = self._highlight_style
            logger.debug(f"Using highlight style: {highlight_style!r}")

        # Build the subs
        max_iterations = len(self._highlights) - 1

        for i, entry in enumerate(self._highlights):
            logger.debug(f"--- Highlight iteration {i} ---")
            logger.debug(f"Segment: words[{entry.index_start}:{entry.index_end+1}], time [{entry.start}ms-{entry.end}ms]")

            space_before = ' ' if entry.index_start > 0 else ''
            space_after = ' ' if entry.index_end < max_iterations + 1 else ''

            text = (
                str(' '.join(self.text_list[0:entry.index_start])) +
                space_before +
                str(highlight_style[0]).strip() +
                str(' '.join(self.text_list[entry.index_start:entry.index_end + 1])) +
                str(highlight_style[1]).strip() +
                space_after +
                str(' '.join(self.text_list[entry.index_end + 1:]))
            )

            if entry.index_start == 0 and entry.index_end == max_iterations:
                logger.info("Single-word highlight detected, using special case")
            else:
                logger.debug(f"Multi-word segment, text parts: pre='{space_before}', post='{space_after}'")

            if self._fade.is_active:
                fade = self._fade.for_segment(i == 0, i == max_iterations)
                if i == 0:
                    logger.debug(f"Applying fade-in: {fade!r}")
                elif i == max_iterations:
                    logger.debug(f"Applying fade-out: {fade!r}")
                text = fade + text
                logger.debug(f"Faded text: {text!r}")

            logger.debug(f"Final text: {text.strip()!r}")
            event = self.build_event(text.strip(), entry.start, entry.end)
            return_subs.append(event)

            logger.debug(f"Created event: {event.start}ms-{event.end}ms, style={event.style}, text={len(event.text)} chars")

            # add backgrounds to the subs
            if self._backgrounds:
                logger.debug(f"Adding {len(self._backgrounds)} background event(s)")
                return_subs.extend(self._backgrounds[i])
            else:
                logger.debug("No backgrounds configured")

        logger.info(f"build_highlighted_subs completed: produced {len(return_subs)} events")
        return return_subs

    def build_highlights_only(self) -> list[pysubs2.SSAEvent]:
        logger.debug(f"build_highlights_only: extracting only highlighted segments")
        return_list = []
        for i, entry in enumerate(self._highlights):

            space_before = ' ' if entry.index_start > 0 else ''
            space_after = ' ' if entry.index_end < len(self._highlights) else ''

            text = (
                    r'{\alpha&HFF}' +
                    str(' '.join(self.text_list[0:entry.index_start])) +
                    space_before +
                    r'{\r}' +
                    str(' '.join(self.text_list[entry.index_start:entry.index_end + 1])) +
                    r'{\alpha&HFF}' +
                    space_after +
                    str(' '.join(self.text_list[entry.index_end + 1:]))
            )
            event = self.build_event(text, entry.start, entry.end)
            return_list.append(event)
            logger.debug(f"Extracted highlight {i}: words[{entry.index_start}:{entry.index_end+1}]")
        return return_list

    def build_event(self, text: str, start:int = None, end:int = None):
        _start = start if start is not None else self._event.start
        _end = end if end is not None else self._event.end

        event = pysubs2.SSAEvent(
            text=text,
            start=_start,
            end=_end,
            style=self._style,
            layer=self._layer
        )
        return event

    def as_plain_event(self) -> pysubs2.SSAEvent:
        return self.build_event(self._event.text)


class SubtitlePipeline:
    def __init__(self, builders: list[SAAEventBuilder]):
        self._builders = builders
        self.dimensions_tracker: list[int] = []

    def render(self) -> list[pysubs2.SSAEvent]:
        """Full render — expands all highlights, fades, backgrounds."""
        logger.info(f"render(): starting render of {len(self._builders)} builder(s)")
        start_time = time.time()
        result = []
        for i, builder in enumerate(self._builders):
            built = builder.build()
            result.extend(built)
            total_events = len(result)
            logger.debug(f"Builder {i} produced {len(built)} events, total so far: {total_events}")
        elapsed = (time.time() - start_time) * 1000
        logger.info(f"render() completed in {elapsed:.2f}ms, total events: {len(result)}")
        return result

    def render_with_depth(self) -> tuple[list[pysubs2.SSAEvent], list[int]]:
        """Same as render but also returns per-event depth for reverse mapping."""
        logger.debug(f"render_with_depth(): tracking event depths for {len(self._builders)} builders")
        result: list[pysubs2.SSAEvent] = []
        depth: list[int] = []
        for i, builder in enumerate(self._builders):
            built = builder.build()
            result.extend(built)
            depth.append(len(built))
            logger.debug(f"Builder {i}: {len(built)} events at depth level {i+1}")
        return result, depth

    def render_text_only(self) -> list[pysubs2.SSAEvent]:
        """Strips all styling — plain text events only."""
        logger.debug(f"render_text_only(): creating plain text events from {len(self._builders)} builders")
        result = [builder.as_plain_event() for builder in self._builders]
        logger.debug(f"render_text_only() completed: {len(result)} plain events")
        return result

    def render_highlights_only(self) -> list[pysubs2.SSAEvent]:
        """Returns only the highlighted word segments, tracks their counts."""
        self.dimensions_tracker.clear()
        logger.debug(f"render_highlights_only(): extracting highlight-only segments")
        result: list[pysubs2.SSAEvent] = []
        for i, builder in enumerate(self._builders):
            built = builder.build_highlights_only()
            self.dimensions_tracker.append(len(built))
            result.extend(built)
            logger.debug(f"Builder {i}: {len(built)} highlight-only segments")
        logger.info(f"render_highlights_only() completed: {len(result)} highlight events, tracker: {self.dimensions_tracker}")
        return result

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return

    def __iter__(self):
        return self._builders


