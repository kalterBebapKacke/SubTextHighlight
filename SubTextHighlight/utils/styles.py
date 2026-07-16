from pydantic import BaseModel, ConfigDict, field_validator, Field
import pysubs2
from .custom_types import *


class Style(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)  # pysubs2.Color/SSAStyle aren't pydantic-native

    fontname: str = "Arial"
    fontsize: PositiveIntFloat = 24
    primarycolor: Color = pysubs2.Color(255, 255, 255)
    backcolor: Color = pysubs2.Color(0, 0, 0)
    secondarycolor: Color = pysubs2.Color(0, 0, 0)
    outlinecolor: Color = pysubs2.Color(0, 0, 0)
    tertiarycolor: Color = pysubs2.Color(0, 0, 0)
    outline: NonNegativeIntFloat = 1
    spacing: NonNegativeIntFloat = 0.75
    shadow: NonNegativeIntFloat = 0        # <- see note below
    bold: bool = True
    angle: NonNegativeIntFloat = 0.0
    italic: bool = False
    underline: bool = False

    alignment:Alignment = Field(default=2, init=False)


    def return_style(self) -> pysubs2.SSAStyle:
        return pysubs2.SSAStyle(
            fontname=self.fontname, fontsize=self.fontsize,
            primarycolor=self.primarycolor, backcolor=self.backcolor,
            secondarycolor=self.secondarycolor, outlinecolor=self.outlinecolor,
            tertiarycolor=self.tertiarycolor, outline=self.outline,
            spacing=self.spacing, shadow=self.shadow,
            alignment=pysubs2.Alignment(self.alignment), bold=self.bold,
            angle=self.angle,
            italic=self.italic, underline=self.underline,
        )

    def merge_onto(self, base_style: pysubs2.SSAStyle) -> pysubs2.SSAStyle:
        merged = self.return_style()
        for name in self.model_fields:
            if name not in self.model_fields_set:      # not explicitly set -> inherit from base
                setattr(merged, name, getattr(base_style, name))
        return merged