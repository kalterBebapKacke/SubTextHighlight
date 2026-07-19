from typing import Annotated, Any, Union, Optional
from annotated_types import Len, Interval
from pydantic import Field
import re
from typing import Any
import pysubs2
from pydantic import GetCoreSchemaHandler, BeforeValidator
from pydantic_core import core_schema
from pathlib import Path

PositiveInt = Annotated[int, Field(gt=0)]
PositiveIntFloat = Annotated[Union[int, float], Field(gt=0)]
NonNegativeIntFloat = Annotated[Union[int, float], Field(ge=0)]
Fade = Annotated[tuple[PositiveIntFloat, PositiveIntFloat], Len(max_length=2)]
Alignment = Annotated[int, Interval(gt=0, lt=10)]
Resolution = Annotated[tuple[PositiveInt, PositiveInt], Len(max_length=2)]

class Color:
    __slots__ = ("r", "g", "b", "a")
    HEX_RE = re.compile(r"^#?([0-9a-fA-F]{6}|[0-9a-fA-F]{8})$")

    def __init__(self, r: int, g: int, b: int, a: int = 0):
        for name, val in (("r", r), ("g", g), ("b", b), ("a", a)):
            if not (0 <= val <= 255):
                raise ValueError(f"Color channel {name!r} must be 0-255, got {val}")
        self.r, self.g, self.b, self.a = r, g, b, a

    def __eq__(self, other):
        return isinstance(other, Color) and (self.r, self.g, self.b, self.a) == (other.r, other.g, other.b, other.a)

    def __repr__(self):
        return f"Color(r={self.r}, g={self.g}, b={self.b}, a={self.a})"

    def to_hex(self, include_alpha: bool = False) -> str:
        if include_alpha:
            return f"#{self.r:02x}{self.g:02x}{self.b:02x}{self.a:02x}"
        return f"#{self.r:02x}{self.g:02x}{self.b:02x}"

    def to_pysubs2(self) -> pysubs2.Color:
        return pysubs2.Color(self.r, self.g, self.b, self.a)

    @classmethod
    def from_hex(cls, value: str) -> "Color":
        m = Color.HEX_RE.match(value)
        if not m:
            raise ValueError(f"Invalid hex color: {value!r}")
        s = m.group(1)
        r, g, b = int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16)
        a = int(s[6:8], 16) if len(s) == 8 else 0
        return cls(r, g, b, a)

    @classmethod
    def _validate(cls, value: Any) -> "Color":
        if isinstance(value, cls):
            return value
        if isinstance(value, pysubs2.Color):
            return cls(value.r, value.g, value.b, value.a)
        if isinstance(value, str):
            return cls.from_hex(value)
        if isinstance(value, (tuple, list)):
            return cls(*value)
        if isinstance(value, dict):
            return cls(**value)
        raise TypeError(f"Cannot convert {type(value)!r} to Color")

    @classmethod
    def __get_pydantic_core_schema__(cls, source_type: Any, handler: GetCoreSchemaHandler) -> core_schema.CoreSchema:
        return core_schema.no_info_plain_validator_function(
            cls._validate,
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda c: c.to_hex(), return_schema=core_schema.str_schema(),
            ),
        )

def coerce_path(value: Any) -> Any:
    if isinstance(value, (str, Path)):
        return value  # let Pydantic's built-in Path validation handle it
    if hasattr(value, "read"):  # file-like object (TextIO, BinaryIO, etc.)
        name = getattr(value, "name", None)
        if name is None:
            raise ValueError(
                "Cannot derive a path from an in-memory file object (no .name "
                "attribute) — pass a string or pathlib.Path instead."
            )
        return name
    raise TypeError(f"Cannot convert {type(value)!r} to a path")

AnyPath = Annotated[Path, BeforeValidator(coerce_path)]