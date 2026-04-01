import stable_whisper
from .style_class import StyleConfig
import pysubs2
from . import docker_wrapper
from . import handler, Highlight
from .main import Subtitle_Edit
from .Effects import Effects
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
    subtitle_type: str = "join"
    word_max: int = 11
    add_time: float = 0
    fill_sub_times: bool = True

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
    force_install: bool = False
    docker_verbose: bool = False
    docker_traceback:bool = False

    # whisper args
    whisper_model: str = "medium.en"
    whisper_device: str = "cpu"
    whisper_refine: bool = False

    # internal (initialized later)
    args_border: docker_wrapper.base.args_border | None = field(init=False)
    Handler: handler.Input_Output_Handler = field(init=False)
    highlighter: Highlight.Highlighter = field(init=False)
    effects: Effects | None = field(init=False)
    sub_file: pysubs2.SSAFile = field(init=False)
    is_effect_needed : bool = field(init=False)
    is_highlighter_needed: bool = field(init=False)

    @property
    def _is_effect_needed(self):
        if not self.highlight_as_borders and self.fade == (0.0, 0.0) and not self.appear:
            return False
        return True

    @property
    def _is_highlighter_needed(self):
        if not self.highlight_as_borders and self.highlight_word_max is None and self.highlight_style is None:
            return False
        return True

    def __post_init__(self):
        if self.rounded_border or self.highlight_as_borders:
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
        else:
            self.args_border = None

        self.Handler = handler.Input_Output_Handler(
            input=self.input,
            output=self.output,
            input_video=self.input_video,
            whisper_model=self.whisper_model,
            whisper_device=self.whisper_device,
            whisper_refine=self.whisper_refine,
        )

        # Check if appear is active and if so throw an expectation
        if self.highlight_as_borders and self.appear:
            raise RuntimeError('Cant use borders as highlighted subtitles and the appear at the same time.')

        self.is_effect_needed = self._is_effect_needed
        self.is_highlighter_needed = self._is_highlighter_needed

        if self.highlight_word_max is None:
            self.highlight_word_max = 0
        if self.highlight_style is None:
            self.highlight_style = StyleConfig()

        self.highlighter = Highlight.Highlighter(self.highlight_word_max, self.subtitle_type)

        self.effects = Effects(
            fade_in_duration=self.fade[0],
            fade_out_duration=self.fade[1],
            appear=self.appear,
            rounded_border=self.rounded_border,
            border_as_highlight=self.highlight_as_borders,
            args_border=self.args_border,
            verbose=self.docker_verbose,
            traceback=self.docker_traceback,
        )


    def highlighter_logic(self):
        if not self.is_highlighter_needed:
            if self.appear:
                return self.highlighter
            return None
        return self.highlighter

    def effects_logic(self):
        if not self.is_effect_needed:
            return None
        return self.effects

    def render(self):
        # get subfile and set highlighter
        sub_file = self.Handler.handle_input()

        # set main style
        main_style = self.subtitle_style.return_style()
        sub_file.styles["MainStyle"] = main_style

        # set highlighter and style
        highlighter = self.highlighter_logic()
        if highlighter is not None:
            sub_file.styles["Highlight"] = self.highlight_style.compare_style(main_style)

        # set effects
        effects = self.effects_logic()

        # edit subs
        self.sub_file = Subtitle_Edit(
            args=self,
            highlighter=highlighter,
            effects=effects,
        )(sub_file)

    def save(self):
        output = self.Handler.handle_output(self.sub_file)
        if output is not None:
            return output
        return None