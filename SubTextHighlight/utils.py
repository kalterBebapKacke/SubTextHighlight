import dataclasses
import re
from copy import deepcopy
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

def get_duration_resolution(file_path):
    cmd = [
        'ffprobe', '-v', 'quiet', '-print_format', 'json',
        '-show_format', '-show_streams', file_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    data = json.loads(result.stdout)

    # Get resolution from the first video stream
    resolution = None
    for stream in data['streams']:
        if stream['codec_type'] == 'video':
            width = stream['width']
            height = stream['height']
            resolution = (width, height)
            break
    return float(data['format']['duration']), resolution

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

def return_script_info(subtitleFile:pysubs2.SSAFile):
    string_subtitles = subtitleFile.to_string('ass')
    return string_subtitles[string_subtitles.find('[Script Info]'):string_subtitles.find('[V4+ Styles]')]

def check_for_PlayRes(subtitleFile:pysubs2.SSAFile):
    script_info = return_script_info(subtitleFile)
    if script_info.__contains__('PlayResX:') and script_info.__contains__('PlayResY:'):
        return True
    else:
        return False

def write_res(subtitleFile:str):
    pass

def set_play_res(subtitleFile:pysubs2.SSAFile, resolution:tuple[int, int]):
    string_subtitles = subtitleFile.to_string('ass')
    script_info = return_script_info(subtitleFile)

    # check if playres is set
    if check_for_PlayRes(subtitleFile):
        # if playres is set, confirm it is the right one
        playresx = script_info[script_info.find('PlayResX:') + len('PlayResX:'):]
        playresx = int(playresx[:playresx.find('\n')])
        playresy = script_info[script_info.find('PlayResY:') + len('PlayResY:'):]
        playresy = int(playresy[:playresy.find('\n')])
        if (playresx, playresy) == resolution:
            return subtitleFile
        else:
            script_info = update_playres(script_info, resolution[0], resolution[1])
            return build_full_sub_file(string_subtitles, script_info)
    else:
        # if it is not set, just add them to the file
        script_info = update_playres(script_info, resolution[0], resolution[1])
        return build_full_sub_file(string_subtitles, script_info)


def update_playres(ass_content, playres_x, playres_y):
    """
    Update or add PlayResX and PlayResY values in ASS subtitle file content.

    Args:
        ass_content (str): The content of the ASS file as a string
        playres_x (int): The new PlayResX value
        playres_y (int): The new PlayResY value

    Returns:
        str: Updated ASS file content
    """
    lines = ass_content.split('\n')
    playres_x_found = False
    playres_y_found = False
    script_info_idx = -1

    # Find [Script Info] section and existing PlayRes values
    for i, line in enumerate(lines):
        stripped = line.strip()

        if stripped == '[Script Info]':
            script_info_idx = i
        elif stripped.startswith('PlayResX:'):
            lines[i] = f'PlayResX: {playres_x}'
            playres_x_found = True
        elif stripped.startswith('PlayResY:'):
            lines[i] = f'PlayResY: {playres_y}'
            playres_y_found = True
        elif stripped.startswith('[') and script_info_idx != -1 and i > script_info_idx:
            # We've reached the next section
            break

    # If PlayRes values weren't found, add them after [Script Info]
    if script_info_idx != -1:
        insert_idx = script_info_idx + 1

        if not playres_y_found:
            lines.insert(insert_idx, f'PlayResY: {playres_y}')
        if not playres_x_found:
            lines.insert(insert_idx, f'PlayResX: {playres_x}')

    return '\n'.join(lines)

def build_full_sub_file(string_subs:str, script_info:str):
    segments = string_subs.split('[')
    segments[1] = script_info[1:]
    segments = '['.join(segments)
    return pysubs2.SSAFile.from_string(segments)



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

class subs_builder():

    def __init__(self):
        # tracks the dimensions of the builded subs, which is important to rebuild the backgrounds, if present
        self.dimensions_tracker = list()

    def __call__(self, subs, type=None): # text_only
        if type == 'text_only':
            return self.text_only_build(subs)
        if type == 'return_only_highlighted_texts':
            return self.return_only_highlighted_texts(subs)
        else:
            return self.normal_build(subs)

    def normal_build(self, subs:list):
        new_subs = list()
        build_subs = [x() for x in subs]
        for sub in build_subs:
            if type(sub) == list:
                new_subs.extend(sub)
            else:
                new_subs.append(sub)
        return new_subs

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

    def return_background_copy(self):
        copy = deepcopy(self)
        copy.highlighted_texts = []
        copy.highlighted_texts = []
        copy.highlight_style = []
        copy.appear_style = []
        return copy

    def return_only_highlighted_texts(self):
        return_list = []
        for index_start, index_end, start, end in self.highlighted_texts:
            return_list.append(pysubs2.SSAEvent(text=' '.join(self.text_list[index_start:index_end+1]), start=start, end=end, style="MainStyle", layer=self.layer))
        return return_list


    def __call__(self):
        return_subs = []
        if self.highlighted_texts != () and self.highlighted_texts != []:
            # If appear is true, replace the highlight styles
            if self.appear_style != () and self.appear_style != []:
                self.highlight_style = ['', self.appear_style[0]]

            # Build the subs
            for index_start, index_end, start, end  in self.highlighted_texts:
                # build the text with hightlighting marks
                text = f'{' '.join(self.text_list[0:index_start])} {self.highlight_style[0]}{' '.join(self.text_list[index_start:index_end+1])}{self.highlight_style[1]} {' '.join(self.text_list[index_end+1:])}'
                return_subs.append(pysubs2.SSAEvent(text=text.strip(), start=start, end=end, style="MainStyle", layer=self.layer))

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

@dataclasses.dataclass(repr=False, eq=False, order=False)
class Background_event(pysubs2.SSAEvent):
    # position offset == 1/2 remaining text
    background:str = ""
    fade_in:float = 0
    fade_out:float = 0
    highlight_position_offset:int = 0

    @property
    def background_list(self):
        return self.background.split(r"\ ".strip())

    def __call__(self):
        return_subs = []
        if self.highlight_position_offset != 0:
            pass # r"\ ".strip().join(self.background_list)
        else:
            text = fr'{{\fad({self.fade_in},{self.fade_out})}}{self.background}'

        return pysubs2.SSAEvent(text=text, start=self.start, end=self.end, style="MainStyle", layer=0)

class background_wrapper():

    def __init__(self, background_event:pysubs2.SSAEvent):
        self.event = background_event

    def __call__(self):
        return self.event
