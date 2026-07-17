import stable_whisper
from . import formatters
from .styles.style_class import StyleConfig
from dataclasses import dataclass, field
from typing import Any
import sys
import pysubs2
from pydantic import BaseModel, field_validator, model_validator, Field3
from typing import Annotated, Any, Union, Optional
from annotated_types import Gt, Len, Interval
import pysubs2
from .utils import *
import logging
logger = logging.getLogger(__name__)


class Config(BaseModel):

    # input args
    input: str | dict[str, Any] | list[dict[str, Any]] | stable_whisper.result.WhisperResult | pysubs2.SSAFile
    output: str | None
    input_video: Optional[str] = None
    resolution: Optional[Resolution] = None

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
    highlight_word_max: Optional[PositiveInt]  = None
    highlight_style: StyleConfig = Field(default_factory=StyleConfig)
    highlight_as_borders: bool = False

    # borders
    BorderConfig:BorderConfig = Field(default_factory=BorderConfig)
    # docker
    DockerConfig:DockerConfig = Field(default_factory=DockerConfig)
    # whisper
    WhisperConfig:Optional[WhisperConfig] = None
    # internal




    @field_validator('subtitle_type', mode='after')
    @classmethod
    def check_formatter(cls, value:str):
        _formatters = formatters.FORMATTER_REGISTER.keys()
        if value not in _formatters:
            raise FormatterError(value, _formatters)
        return value


