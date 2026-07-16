import stable_whisper
from . import pipeline
from .handling import Output
from .formatters import base, register
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

@dataclass
class SubtitleConfig:
    # input args
    input: str | dict[str, Any] | list[dict[str, Any]] | stable_whisper.result.WhisperResult
    output: str | None
    input_video: str | None = None

    # subtitle styles
    subtitle_style: StyleConfig = field(default_factory=StyleConfig)
    subtitle_type: type[base.BaseFormatter] = register.Formatters.joined
    word_max: int = 11
    add_time: float = 0
    fill_sub_times: bool = True
    alignment:int = 2

    # highlight styles
    highlight_word_max: int | None = None
    highlight_style: StyleConfig | None = None
    highlight_as_borders: bool = False

    # effect args
    fade: tuple[float, float] = (0.0, 0.0)
    appear: bool  = False

    # border args
    rounded_border: bool = False
    offset: int = 6
    radius: int = 6
    transformy: int = 1
    height_scaling: float = 1.2
    color: pysubs2.Color | None = None

    # docker args
    fonts_path: list | str | None = None
    packages: list[str] | None = None
    container_run_func: None = None
    docker_force_install: bool = False
    docker_verbose: bool = False
    docker_traceback:bool = False

    # whisper args
    whisper_model: str = "medium.en"
    whisper_device: str = "cpu"
    whisper_refine: bool = False

    # internal (initialized later)
    sub_file: pysubs2.SSAFile = field(init=False)

    def render(self):

        with pipeline.BuildPipeline(self) as build_pipeline:
            _pipeline = build_pipeline.build()

        self.sub_file = _pipeline.run()

    def save(self):
        output_obj = Output.Output(self.output, self.input_video)
        _output = output_obj.handle_output(self.sub_file)

        if _output is not None:
            return _output
        return None

    def debug(self, file_location='subtitles.log'):
        logging.basicConfig(filename=file_location, filemode='w', encoding='utf-8', level=logging.DEBUG)

    def debug_no_file(self):
        logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)


class Config(BaseModel):

    # input args
    input: str | dict[str, Any] | list[dict[str, Any]] | stable_whisper.result.WhisperResult
    output: str | None
    input_video: str | None = None

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
    resolution:Resolution = Field(init=False)

