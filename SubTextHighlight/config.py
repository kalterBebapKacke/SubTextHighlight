import stable_whisper
from .style_class import StyleConfig
import pysubs2
import docker_wrapper
from . import handler, Highlight
from .main import Subtitle_Edit

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
    highlight_word_max: int | None = None
    highlight_style: StyleConfig | None = None
    highlight_as_borders: bool | None = None

    # effect args
    fade: tuple[float, float] | None = None #(0.0, 0.0)
    appear: bool | None = None

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
    sub_file: pysubs2.SSAFile = field(init=False)


    @property
    def is_effect_needed(self):
        if self.highlight_as_borders is None and self.fade is None and self.appear is None:
            return False
        return True

    @property
    def is_highlighter_needed(self):
        if self.highlight_as_borders is None and self.highlight_word_max is None and self.highlight_style is None:
            return False
        return True

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


    def highlighter_logic(self, main_style: pysubs2.SSAStyle):
        # TODO: Rework highlighter to work
        if self.highlight_word_max is None:
            self.highlight_word_max = 0
        if self.highlight_style is None:
            self.highlight_style = StyleConfig()

        highlighter = Highlight.Highlighter(self.highlight_word_max, self.subtitle_type)

        if not self.is_highlighter_needed:
            if not self.is_effect_needed:
                return None

        return highlighter

    def render(self):
        # get subfile and set highlighter
        sub_file = self.input_handler.handle_input()

        # set main style
        main_style = self.subtitle_style.return_style()
        sub_file.styles["MainStyle"] = main_style

        # set highlighter and style
        self.highlighter = self.highlighter_logic(main_style)
        sub_file.styles["Highlight"] = self.highlight_style.compare_style(main_style)

        # edit subs
        self.sub_file = Subtitle_Edit(
            args=self,
            highlighter=self.highlighter,
            effects=None,
        )(sub_file)






