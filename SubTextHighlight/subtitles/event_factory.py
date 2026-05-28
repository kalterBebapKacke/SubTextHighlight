from pysubs2 import SSAEvent
from .subtitle_render import SAAEventBuilder
from . Highlight import Highlighter
import logging
logger = logging.getLogger(__name__)

class EventFactory:
    def __init__(self, highlighter: Highlighter | None = None):
        self.highlighter = highlighter

    def build(self, text: str, start, end, sub_list: list = ()) -> list:
        event = SSAEvent(text=text, start=start, end=end, style="MainStyle")
        builder = SAAEventBuilder(event)

        logger.debug(str(';'.join(["Event Factory:", text, str(start), str(end), str(sub_list)])))

        if self.highlighter:
            builder = self.highlighter.annotate(builder, sub_list, end)

        return [builder]