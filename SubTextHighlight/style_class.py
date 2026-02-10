import dataclasses
import pysubs2
from .utils import hex_to_pysub2_color

def manage_color_input(color_input):
    if isinstance(color_input, str):
        return hex_to_pysub2_color(color_input)
    elif isinstance(color_input, pysubs2.Color):
        return color_input
    else:
        raise ValueError("Invalid color input. Must be a hex string or pysubs2.Color object.")

#@dataclasses.dataclass
@dataclasses.dataclass(kw_only=True)
class StyleConfig:
    """
            Subtitle style configuration class for customizing text appearance and formatting.

            This class provides comprehensive control over subtitle rendering including font properties,
            colors, visual effects, and layout positioning using SubStation Alpha (SSA/ASS) format standards.

            Parameters:
                fontname (str): Font family name. Any system-installed font can be specified.
                    Default: 'Arial'

                fontsize (float | int): Font size in points. Larger values create bigger text.
                    Default: 24

                primarycolor (pysubs2.Color | str): Main text fill color in RGBA format (0-255).
                    Default: pysubs2.Color(255, 255, 255) (white)

                backcolor (pysubs2.Color | str): Background color behind text when using box border style.
                    Default: pysubs2.Color(0, 0, 0) (black)

                secondarycolor (pysubs2.Color | str): Secondary color for karaoke effects and transitions.
                    Default: pysubs2.Color(0, 0, 0) (black)

                outlinecolor (pysubs2.Color | str): Color of text outline/border for readability.
                    Default: pysubs2.Color(0, 0, 0) (black)

                tertiarycolor (pysubs2.Color | str): Additional outline color for complex border effects.
                    Default: pysubs2.Color(0, 0, 0) (black)

                outline (float | int): Thickness of text outline in pixels. Higher values create thicker borders.
                    Default: 1

                spacing (float | int): Line spacing multiplier. Values <1.0 create tighter spacing, >1.0 looser.
                    Default: 0.75

                shadow (float | int): Drop shadow offset in pixels. 0 disables shadow effect.
                    Default: 0

                alignment (int): Text positioning using numpad layout:
                    1-3: Bottom (left/center/right), 4-6: Middle (left/center/right), 7-9: Top (left/center/right)
                    Default: 5 (middle-center)

                bold (bool): Enable bold text formatting for improved readability.
                    Default: True

                angle (float): Text rotation angle in degrees. Positive values rotate clockwise.
                    Default: 0.0

                borderstyle (int): Border rendering style. 1=outline border, 3=opaque box background.
                    Default: 1

                italic (bool): Enable italic text formatting.
                    Default: False

                underline (bool): Enable underline text formatting.
                    Default: False

            Example:
                >>> # Create style with yellow text and blue outline
                >>> style = StyleConfig(
                ...     fontsize=28,
                ...     primarycolor=pysubs2.Color(255, 255, 0),
                ...     outlinecolor=pysubs2.Color(0, 100, 255),
                ...     outline=2,
                ...     alignment=2
                ... )

            Note:
                All color parameters accept either pysubs2.Color objects or compatible color strings.
                The default configuration creates bold white text with black outline, optimized for
                readability across various video backgrounds.
            """


    fontname: str = 'Arial'
    fontsize: float | int = 24
    primarycolor: pysubs2.Color | str = dataclasses.field(
        default_factory=lambda: pysubs2.Color(255, 255, 255)
    )
    backcolor: pysubs2.Color | str = dataclasses.field(
        default_factory=lambda: pysubs2.Color(0, 0, 0)
    )
    secondarycolor: pysubs2.Color | str = dataclasses.field(
        default_factory=lambda: pysubs2.Color(0, 0, 0)
    ) # Black for border/shadow
    outlinecolor: pysubs2.Color | str = dataclasses.field(
        default_factory=lambda: pysubs2.Color(0, 0, 0)
    )
    tertiarycolor: pysubs2.Color | str = dataclasses.field(
        default_factory=lambda: pysubs2.Color(0, 0, 0)
    )
    outline: float | int = 1
    spacing: float | int = 0.75
    shadow: float | int = 0
    alignment: int = 5
    bold: bool = True
    angle: float = 0.0
    borderstyle: int = 1
    italic: bool = False
    underline: bool = False


    def return_style(self):
        # convert Colors to pysub2.Color if in string format
        self.primarycolor = manage_color_input(self.primarycolor)
        self.backcolor = manage_color_input(self.backcolor)
        self.secondarycolor = manage_color_input(self.secondarycolor)
        self.outlinecolor= manage_color_input(self.outlinecolor)
        self.tertiarycolor = manage_color_input(self.tertiarycolor)
        # return the pysub2 style
        return pysubs2.SSAStyle(
            fontname=self.fontname,
            fontsize=self.fontsize,
            primarycolor=self.primarycolor,
            backcolor=self.backcolor,
            secondarycolor=self.secondarycolor,  # Black for border/shadow
            outlinecolor=self.outlinecolor,  # Black outline
            tertiarycolor=self.tertiarycolor,
            outline=self.outline,
            spacing=self.spacing,
            shadow=self.shadow,
            alignment=pysubs2.Alignment(self.alignment),
            bold=self.bold,
            angle=self.angle,
            borderstyle=self.borderstyle,
            italic=self.italic,
            underline=self.underline
        )