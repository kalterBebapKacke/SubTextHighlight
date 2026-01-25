import dataclasses
import re
from copy import deepcopy
import pysubs2
import subprocess
import tempfile
import os
import json


def get_duration_resolution(file_path):
    cmd = [
        'ffprobe', '-v', 'error', '-print_format', 'json',
        '-show_format', '-show_streams', file_path
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        data = json.loads(result.stdout)
    except (subprocess.CalledProcessError, json.JSONDecodeError):
        return 0.0, None

    # 1. Handle Duration
    # Try getting duration from format first, fallback to 0.0
    duration_str = data.get('format', {}).get('duration', 0)
    duration = float(duration_str)

    # 2. Handle Resolution (Video Only)
    resolution = None
    streams = data.get('streams', [])
    for stream in streams:
        if stream.get('codec_type') == 'video':
            width = stream.get('width')
            height = stream.get('height')
            if width and height:
                resolution = (width, height)
            break

    return duration, resolution

def is_subfile_resolution_set(sub_file:pysubs2.SSAFile):
    info = sub_file.info
    keys = info.keys()
    if 'PlayResX' in keys and 'PlayResY' in keys:
        return True
    else:
        return False

def dprint(txt):
    if os.environ['debug'] == 'True':
        print(txt)

def exec_command(command:list):
    try:
        result = subprocess.run(command, text=True, stdout=subprocess.PIPE)
        if result.returncode != 0:
            raise RuntimeError(result.stdout)
    except Exception as e:
        pass

def add_subtitles_with_ffmpeg(video_path, output_path, sub_file:pysubs2.SSAFile):
    with tempfile.NamedTemporaryFile(mode='w', suffix='.ass', delete=False) as temp_file:
        temp_file.write(sub_file.to_string(format_='ass'))
        temp_filename = temp_file.name
    add_subtitles_with_ffmpeg_with_given_ass(video_path, output_path, temp_filename)
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


#@dataclasses.dataclass
@dataclasses.dataclass(kw_only=True)
class args_styles:
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
        self.primarycolor = hex_to_pysub2_color(self.primarycolor) if type(self.primarycolor) is str else self.primarycolor
        self.backcolor = hex_to_pysub2_color(self.backcolor) if type(self.backcolor) is str else self.backcolor
        self.secondarycolor = hex_to_pysub2_color(self.secondarycolor) if type(self.secondarycolor) is str else self.secondarycolor
        self.outlinecolor= hex_to_pysub2_color(self.outlinecolor) if type(self.outlinecolor) is str else self.outlinecolor
        self.tertiarycolor = hex_to_pysub2_color(self.tertiarycolor) if type(self.tertiarycolor) is str else self.tertiarycolor
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

def is_drawing_line(line):
    """
    Determines if an ASS subtitle line contains a drawing or text.

    Args:
        line (str): A line from an ASS subtitle file

    Returns:
        bool: True if the line contains a drawing, False if it's text

    Examples:
        >>> is_drawing_line("Can I help you? Hmm?")
        False
        >>> is_drawing_line("{\\an7\\pos(640,678)\\p1}m -122 18.45 b -133.05...")
        True
    """
    # Check if line contains drawing mode tag \p1 or higher
    # \p0 means text mode, \p1 or higher means drawing mode
    drawing_pattern = r'\\p[1-9]'

    if re.search(drawing_pattern, line):
        return True

    return False

def segment_subs(events:list):
    result = []
    for event in events:
        if not is_drawing_line(event.text):
            result.append([event])
        else:
            result[-1].append(event)
    return result

def separate_tags(text:str):
    styles = text[text.find('{')+1:text.find('}')]
    return styles

def filter_out_fad_tag(tag:str):
    tags = tag.split(r"\ "[0])
    for tag in tags:
        if tag.__contains__('fad'):
            return tag
    return None

def fix_fad_issue(events:list):
    # check which tags dont contain an fad and then insert the needed fad tag
    segments = segment_subs(events)
    results = list()
    for segment in segments:
        text_tag = separate_tags(segment[0].text)
        background_tags = [separate_tags(x.text) for x in segment[1:]]

        # only continue if a fad statement is present
        if text_tag.__contains__('fad'):
            fad_tag = filter_out_fad_tag(text_tag)
            new_background_events = list()

            # only insert where the fad tag is not present
            for i, background_tag in enumerate(background_tags):
                if not fad_tag in background_tag:

                    # insert the new tags into the original text
                    new_background_events.append(background_tag + '\\'+ fad_tag)

                    # insert the new tags into the original text
                    segment[i+1].text = segment[i+1].text.replace(background_tag, background_tag + '\\'+ fad_tag)


            results.append(new_background_events)
    return segments



class subs_builder():

    def __init__(self):
        # tracks the dimensions of the builded subs, which is important to rebuild the backgrounds, if present
        self.dimensions_tracker = list()

    def __call__(self, subs, type=None, return_depth:bool=False): # text_only
        if type == 'text_only':
            return self.text_only_build(subs)
        if type == 'return_only_highlighted_texts':
            return self.return_only_highlighted_texts(subs)
        else:
            return self.normal_build(subs, return_depth)

    def normal_build(self, subs:list, return_depth:bool=False):
        new_subs = list()
        depth = list()
        build_subs = [x() for x in subs]
        for sub in build_subs:
            if type(sub) == list:
                new_subs.extend(sub)
                depth.append(len(sub))
            else:
                depth.append(1)
                new_subs.append(sub)

        # Depth needed to reverse input
        if not return_depth:
            return new_subs
        else:
            return new_subs, depth

    def text_only_build(self, subs:list):
        return [sub.return_saa_event() for sub in subs]

    def return_only_highlighted_texts(self, subs:list):
        return_subs = list()
        for sub in subs:
            new_subs = sub.return_only_highlighted_texts()
            # tracks length of subs
            self.dimensions_tracker.append(len(new_subs))
            return_subs.extend(new_subs)
        return return_subs

@dataclasses.dataclass(repr=False, eq=False, order=False)
class advanced_SAA_Events(pysubs2.SSAEvent):

    #text_list:list = ()
    highlighted_texts: list = ()
    highlight_style: list = ()
    appear_style:list = ()
    fade_in:float = 0
    fade_out:float = 0
    backgrounds:list = ()

    @property
    def text_list(self):
        return self.text.split(' ')

    def add_highlight_entry(self, index_start:int, index_end:int, start:int, end:int):
        # replace the tuple
        self.highlighted_texts = [] if len(self.highlighted_texts) == 0 else self.highlighted_texts
        self.highlighted_texts.append([index_start, index_end, start, end])

    def generate_fade(self, len_subs:int):
        if len_subs == 1:
            return fr'{{\fad({self.fade_in},{self.fade_out})}}', ''
        else:
            return fr'{{\fad({self.fade_in},0)}}', fr'{{\fad(0,{self.fade_out})}}'

    def return_saa_event(self):
        return pysubs2.SSAEvent(text=self.text.strip(), start=self.start, end=self.end, style="MainStyle")


    def return_only_highlighted_texts(self):
        return_list = []
        for index_start, index_end, start, end in self.highlighted_texts:
            return_list.append(pysubs2.SSAEvent(text=' '.join(self.text_list[index_start:index_end+1]), start=start, end=end, style="MainStyle", layer=self.layer))
        return return_list

    def add_background(self, backgrounds:list):
        if self.backgrounds == ():
            self.backgrounds = [backgrounds]
        else:
            self.backgrounds.append(backgrounds)

    def __call__(self):
        return_subs = []
        if self.highlighted_texts != () and self.highlighted_texts != []:
            # If appear is true, replace the highlight styles
            if self.appear_style != () and self.appear_style != []:
                self.highlight_style = ['', self.appear_style[0]]

            # Build the subs
            for i, (index_start, index_end, start, end)  in enumerate(self.highlighted_texts):
                # build the text with hightlighting marks
                text = f'{' '.join(self.text_list[0:index_start])} {self.highlight_style[0]}{' '.join(self.text_list[index_start:index_end+1])}{self.highlight_style[1]} {' '.join(self.text_list[index_end+1:])}'
                return_subs.append(pysubs2.SSAEvent(text=text.strip(), start=start, end=end, style="MainStyle", layer=self.layer))

                # add backgrounds to the subs
                if self.backgrounds != ():
                    return_subs.extend(self.backgrounds[i])

        else:
            return_subs = [pysubs2.SSAEvent(text=self.text, start=self.start, end=self.end, style="MainStyle", layer=self.layer)]

        # apply fade and return
        if len(return_subs) == 1:
            return_subs[0].text = self.generate_fade(len(return_subs))[0] + return_subs[0].text
            return return_subs[0]
        else:
            fade = self.generate_fade(len(return_subs))
            return_subs[0].text = fade[0] + return_subs[0].text
            return_subs[-1].text = fade[1] + return_subs[-1].text
            return return_subs