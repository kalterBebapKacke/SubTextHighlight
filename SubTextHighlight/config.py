import stable_whisper
from . import pipeline
from .handling import Output
from . import formatters
from .styles.style_class import StyleConfig
from dataclasses import dataclass, field
from typing import Any
import sys
import pysubs2
from pydantic import BaseModel, field_validator, model_validator, Field
from typing import Annotated, Any, Union, Optional
from annotated_types import Gt, Len, Interval
from .utils import *
import logging
logger = logging.getLogger(__name__)


class Config(BaseModel):

    # input args
    input: str | dict[str, Any] | list[dict[str, Any]] | stable_whisper.result.WhisperResult
    output: str | None
    input_video: Optional[str]

    # subtitle styles
    # need to import both style and type
    subtitle_style: StyleConfig = Field(default_factory=StyleConfig)
    subtitle_type: str
    char_max:PositiveInt = 11
    add_time_seconds:PositiveIntFloat = 0
    fill_sub_times: bool = True
    alignment: Alignment = 2

    # effect args
    fade:Fade = (0.0, 0.0)
    appear: bool  = False
    rounded_border: bool = False

    # highlight styles
    highlight_word_max: Optional[PositiveInt]
    highlight_style: Optional[StyleConfig]
    highlight_as_borders: bool = False

    # borders
    # docker
    # whisper

    # internal
    resolution:Resolution | None = Field(init=False)

    @field_validator('subtitle_type', mode='after')
    @classmethod
    def check_formatter(cls, value:str):
        _formatters = formatters.FORMATTER_REGISTER.keys()
        if value not in _formatters:
            raise FormatterError(value, _formatters)
        return value
