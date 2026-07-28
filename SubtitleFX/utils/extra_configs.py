from .custom_types import *
from pydantic import BaseModel, Field, SkipValidation


class BorderConfig(BaseModel):

    offset:PositiveInt = 6
    radius:PositiveInt = 6
    transformy: PositiveInt = 1
    height_scaling: PositiveIntFloat = 1.2
    color: Color = Field(default_factory=lambda: Color(0, 0, 0))

    def json_info(self):
        return {
            "offset": self.offset,
            "radius": self.radius,
            "transformY": self.transformy,
            "heightscaling": self.height_scaling,
            "borderColor": self.color.to_hex(),
            "borderAlpha": self.color.to_pysubs2().a,
        }


class DockerConfig(BaseModel):

    fonts_path: Optional[list | str] = None
    packages:  Optional[list[str]] = None
    force_install: bool = False
    traceback:bool = False

class WhisperConfig(BaseModel):

    model: str = "medium.en"
    device: str = "cpu"
    refine: bool = False

    # TODO: Valid type checking
