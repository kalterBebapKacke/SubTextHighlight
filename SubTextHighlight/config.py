import stable_whisper
from .style_class import StyleConfig
import pysubs2
import docker_wrapper
from . import handler, Highlight

from dataclasses import dataclass, field
from typing import Any
import pysubs2

@dataclass
class SubtitleConfig:
    # input args
    input: str | dict[str, Any] | list[dict[str, Any]] | stable_whisper.result.WhisperResult
    output: str | None
    input_video: str | None = None

    # subtitle styles
    subtitle_style: StyleConfig = field(default_factory=StyleConfig)
    subtitle_type: str = "one_word_only"
    word_max: int = 11
    add_time: float = 0
    fill_sub_times: bool = True

    # highlight styles
    highlight_word_max: int | None = 0
    highlight_style: StyleConfig = field(default_factory=StyleConfig)
    highlight_as_borders: bool = False

    # effect args
    fade: tuple[float, float] = (0.0, 0.0)
    appear: bool = False

    # border args
    offset: int = 6
    radius: int = 6
    transformy: int = 1
    height_scaling: float = 1.2
    color: pysubs2.Color | None = None

    # docker args
    fonts_path: list | str | None = None
    packages: list[str] | None = None
    container_run_func: None = None
    force_install: bool = False

    # whisper args
    whisper_model: str = "medium.en"
    whisper_device: str = "cpu"
    whisper_refine: bool = False

    # internal (initialized later)
    args_border: docker_wrapper.base.args_border = field(init=False)
    input_handler: handler.Input_Output_Handler = field(init=False)
    highlighter: Highlight.Highlighter = field(init=False)

    def __post_init__(self):
        self.args_border = docker_wrapper.base.args_border(
            offset=self.offset,
            radius=self.radius,
            transformy=self.transformy,
            height_scaling=self.height_scaling,
            color=self.color,
            use_borders_as_highlight=self.highlight_as_borders,
            fonts_path=self.fonts_path,
            packages=self.packages,
            container_run_func=self.container_run_func,
            force_install=self.force_install,
        )

        self.input_handler = handler.Input_Output_Handler(
            input=self.input,
            output=self.output,
            input_video=self.input_video,
            whisper_model=self.whisper_model,
            whisper_device=self.whisper_device,
            whisper_refine=self.whisper_refine,
        )

        #self.highlighter = Highlight.Highlighter()
