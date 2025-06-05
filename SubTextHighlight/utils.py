import pysubs2

def hex_to_pysub2_color(hex_color, alpha=0):
    """
    Convert hex color string to pysub2.Color format.

    Args:
        hex_color: A hex string in format 'RRGGBB' (e.g., 'ff0000' for red)
        alpha: Alpha/transparency value (0-255), default 0 (opaque)

    Returns:
        pysub2.Color object
    """

    # Remove '#' if present
    if hex_color.startswith('#'):
        hex_color = hex_color[1:]

    # Convert hex to RGB
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)

    # Create pysub2.Color object
    return pysubs2.Color(r, g, b, alpha)

def import_color(color:pysubs2.Color | str | None):
    if color is None:
        return None
    elif type(color) == pysubs2.Color:
        return color
    else:
        return hex_to_pysub2_color(color)

def replace_all(str_:str, replace_from, replace_with):
    while str_.__contains__(replace_from):
        str_ = str_.replace(replace_from, replace_with)
    return str_

class args_styles:

    def __init__(self,
        fontname:str = 'Arial',
        fontsize:float | int = 24,
        primarycolor:pysubs2.Color | str = pysubs2.Color(255, 255, 255),
        backcolor:pysubs2.Color | str = pysubs2.Color(0, 0, 0),
        secondarycolor:pysubs2.Color | str = pysubs2.Color(0, 0, 0, ),  # Black for border/shadow
        outlinecolor:pysubs2.Color | str = pysubs2.Color(0, 0, 0),
        tertiarycolor:pysubs2.Color | str = pysubs2.Color(0, 0, 0),       # Black outline
        outline:float | int = 1,
        spacing:float | int = 0.75,
        shadow:float | int = 0,
        alignment:int = 5,
        bold:bool = True,
        angle: float = 0.0,
        borderstyle: int = 1,
        italic: bool = False,
        underline: bool = False
    ):
        self.fontname = fontname
        self.fontsize = fontsize
        self.primarycolor = import_color(primarycolor)
        self.backcolor = import_color(backcolor)
        self.secondarycolor = import_color(secondarycolor) # Black for border/shadow
        self.outlinecolor = import_color(outlinecolor) # Black outline
        self.tertiarycolor = import_color(tertiarycolor)
        self.outline = outline
        self.spacing = spacing
        self.shadow = shadow
        self.alignment = alignment
        self.bold = bold
        self.angle: float = angle
        self.borderstyle: int = borderstyle
        self.italic: bool = italic
        self.underline: bool = underline


    def return_style(self):
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