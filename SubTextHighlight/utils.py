import pysubs2
import stable_whisper
import subprocess
import tempfile
import os
import json

def use_whisper(path:str, model='base.en', device='cpu', refine:bool=False):
    model = stable_whisper.load_model(model, device=device)
    result = model.transcribe(audio=path, verbose=None)
    if refine:
        model.refine(path, result, word_level=False, only_voice_freq=True, precision=0.05)
    r = result.to_srt_vtt(None, segment_level=False, word_level=True)
    return r

def return_whisper_result(result:stable_whisper.result.WhisperResult):
    return result.to_srt_vtt(None, segment_level=False, word_level=True)

def dprint(txt):
    if os.environ['debug'] == 'True':
        print(txt)

def get_duration(file_path):
    cmd = [
        'ffprobe', '-v', 'quiet', '-print_format', 'json',
        '-show_format', file_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    data = json.loads(result.stdout)
    return float(data['format']['duration'])

def exec_command(command:list):
    try:
        result = subprocess.run(command, text=True, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
        #print(result)
    except Exception as e:
        print(e)

def add_subtitles_with_ffmpeg(video_path, output_path, sub_file:pysubs2.SSAFile):
    with tempfile.NamedTemporaryFile(mode='w', suffix='.ass', delete=False) as temp_file:
        temp_file.write(sub_file.to_string(format_='ass'))
        temp_filename = temp_file.name
    command = [
        "ffmpeg",
        "-y",
        "-i", video_path,
        "-vf",
        f"ass={temp_filename}",
        "-c:a", "copy",
        "-loglevel", "error",
        output_path
    ]
    exec_command(command)
    os.unlink(temp_filename)

def add_subtitles_with_ffmpeg_with_given_ass(video_path, output_path, ass_file):
    command = [
        "ffmpeg",
        "-y",
        "-i", video_path,
        "-vf",
        f"ass={ass_file}",
        "-c:a", "copy",
        "-loglevel", "error",
        output_path
    ]
    exec_command(command)

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
            >>> style = args_styles(
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