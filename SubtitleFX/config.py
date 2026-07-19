import stable_whisper
from . import formatters
from pydantic import BaseModel, ConfigDict, field_validator, model_validator, Field
from .utils import *
import logging
logger = logging.getLogger(__name__)


class Config(BaseModel):
    model_config = ConfigDict(validate_assignment=True, arbitrary_types_allowed=True)

    # input args
    input: str | dict[str, Any] | list[dict[str, Any]] | stable_whisper.result.WhisperResult | pysubs2.SSAFile
    output: str | None
    input_video: Optional[str] = None
    resolution: Optional[Resolution] = None

    # subtitle styles
    # need to import both style and type
    subtitle_style: Style = Field(default_factory=Style)
    subtitle_type: str
    char_max:PositiveIntOrZero = 11
    add_time_seconds:PositiveIntFloat = 0
    fill_sub_times: bool = True
    alignment: Alignment = 2

    # effect args
    fade:Fade = (0.0, 0.0)
    appear: bool  = False
    rounded_border: bool = False

    # highlight styles
    highlight_char_max: Optional[PositiveIntOrZero] = None
    highlight_style: Optional[Style] = None
    highlight_as_borders: bool = False

    # borders
    border_config:BorderConfig = Field(default_factory=BorderConfig)
    # docker
    docker_config:DockerConfig = Field(default_factory=DockerConfig)
    # whisper
    whisper_config:Optional[WhisperConfig] = None
    # internal




    @field_validator('subtitle_type', mode='after')
    @classmethod
    def check_formatter(cls, value:str):
        _formatters = formatters.FORMATTER_REGISTER.keys()
        if value not in _formatters:
            raise FormatterError(value, _formatters)
        return value


