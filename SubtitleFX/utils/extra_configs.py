from .custom_types import *
from pydantic import BaseModel
from pysubs2 import Color as pysub2_Color

class BorderConfig(BaseModel):

    offset:PositiveInt = 6
    radius:PositiveInt = 6
    transformy: PositiveInt = 1
    height_scaling: PositiveIntFloat = 1.2
    color: Color = pysub2_Color(255, 255, 255)

class DockerConfig(BaseModel):

    fonts_path: list | str | None = None
    packages: list[str] | None = None
    container_run_func: None = None
    force_install: bool = False
    verbose: bool = False
    traceback:bool = False

class WhisperConfig(BaseModel):

    model: str = "medium.en"
    device: str = "cpu"
    refine: bool = False

    # TODO: Valid type checking
