# SubTextHighlight
This is a Package for generating and formatting subtitles while focusing on user-friendliness and providing many features.

This is an example video generated with this package (The official [Dark Souls 3 Trailer](https://www.youtube.com/watch?v=_zDZYrIUgKE) is used as an example video):


# Requirements

For this package to work ffmpeg has to be installed on your machine. See the [ffmpeg website](https://ffmpeg.org/) for more details. 

# Installation

Not yet supported

# How to use

You have tree Args classes to input, that control, what should be done. These are:

1. `sub_args` - they control the styling of the subtitles, give the input and have general settings
2. `highlight_args` - they control the highlight args
3. `effects_args` - they control the effects and which should be used 

## General styling of subs and highlighted words - utils.args_styles

Both sub_args and highlight_args inherit from the utils.args_styles, which controls the styling of your text.

Here is an overview of the attributes:

### Font Settings

`fontname: str (default: 'Arial')`
Font family to use for subtitle text. Must be installed on the system.

`fontsize: float | int (default: 24)`
Size of the font in points.

`bold: bool (default: True)`
Renders text in bold for improved readability.

`italic: bool (default: False)`
Applies italic styling to the text.

`underline: bool (default: False)`
Enables underline decoration on subtitle text.

### Color Settings

All color values accept either pysubs2.Color objects or HEX colors (e.g., 'ff0000' for red).

`primarycolor: pysubs2.Color | str (default: Color(255, 255, 255))`
Main fill color for subtitle text.

`secondarycolor: pysubs2.Color | str (default: Color(0, 0, 0))`
Used for karaoke and transitional effects.

`backcolor: pysubs2.Color | str (default: Color(0, 0, 0))`
Background color behind text when using boxed styles.

`outlinecolor: pysubs2.Color | str (default: Color(0, 0, 0))`
Color of the text outline to enhance visibility.

`tertiarycolor: pysubs2.Color | str (default: Color(0, 0, 0))`
Optional secondary outline color for complex border effects.

### Visual Effects

`outline: float | int (default: 1)`
Thickness of the text outline in pixels.

`shadow: float | int (default: 0)`
Drop shadow offset in pixels. A value of 0 disables the shadow.

`borderstyle: int (default: 1)`
Specifies the text border style:

        1: Standard outline

        3: Opaque box background

### Layout and Positioning

`alignment: int (default: 5)`
Text positioning based on numpad-style layout:


    7 8 9
    4 5 6
    1 2 3

For example, `1 = bottom-left`, `5 = center`, `9 = top-right`.

- `spacing: float | int` (default: `0.75`) – Line spacing multiplier  
- `angle: float` (default: `0.0`) – Text rotation angle (degrees)

---

## `sub_args` – Subtitle Parameters

Inherits from `utils.args_styles`.

### Parameters:

- `input: str | WhisperResult` (**required**)  
Path to input file (video/audio/SRT/ASS/plain text). Supports automatic transcription via Whisper if using video/audio. Must contain **only one word per subtitle** for proper formatting.

- `output: str` (**required**)  
Output path (ASS or video). If `None`, returns `pysubs2.SSAFile`.

- `input_video: str | None`  
Video path for burned-in subs (optional).

- `subtitle_type: str` (default: `'one_word_only'`)  
  - `'one_word_only'`: One word per subtitle  
  - `'join'`: Join words into longer segments in respect to the `word_max` parameter
  - `'separate_on_period'`: Split at sentence boundaries

- `word_max: int` (default: `11`)  
Max words per subtitle segment (ignored in `'one_word_only'` mode).

- `add_time: float` (default: `0`)  
Extra seconds to shift the timestamps of all subtitles.

- `fill_sub_times: float` (default: `0`)  
Fills the gap between subtitle segments.

- `whisper_model: str` (default: `'medium.en'`)  
Whisper model name. See [Whisper GitHub](https://github.com/openai/whisper).

- `whisper_refine: bool` (default: `False`)  
Enables timestamp refinement for improved results. For even better results generating your own subtitles via [Stable TTS](https://github.com/jianfch/stable-ts/tree/main) is recommended. Only english Subtitles are supported with this parameter.

---

## `highlight_args` – Highlighted Word Styling

Also inherits from `utils.args_styles`, but with default values set to `None`. If an attribute is `None`, the corresponding `sub_args` value is used.

### New Parameter:

- `highlight_word_max: int` (default: `0`)  
Number of words to highlight per segment (`0` = highlight one word only).

---

## `effects_args` – Subtitle Effects

Controls special effects.

- `fade: tuple[float, float]` (default: `(0.0, 0.0)`)  
  - `fade[0]`: Fade-in duration (ms)  
  - `fade[1]`: Fade-out duration (ms)

- `appear: bool` (default: `False`)  
Words appear cumulatively. Controlled via `highlight_word_max`.  
If `highlight_args` is `None`, default settings are applied automatically.

---

## Example Usage

### Generate Video with Burned-in Subtitles
 
```python
import SubTextHighlight

input = './media/plain_video.webm'
output = './media/edited_video.mp4'
sub_args = SubTextHighlight.sub_args(input=input, output=output, input_video=input, subtitle_type='separate_on_period', fill_sub_times=False, alignment=2, whisper_refine=True)
highlight_args =  SubTextHighlight.highlight_args(primarycolor='00AAFF')
effect_args = SubTextHighlight.effects_args((50, 50))
sub_edit = SubTextHighlight.Subtitle_Edit(sub_args, highlight_args, effect_args)
sub_edit()
```

### Generate Subtitle File Only (`.ass`)
```python
import SubTextHighlight

input = './media/plain_video.webm'
output = './media/subtitles.ass'
sub_args = SubTextHighlight.sub_args(input=input, output=output, subtitle_type='separate_on_period', fill_sub_times=False, alignment=2, whisper_refine=True)
highlight_args =  SubTextHighlight.highlight_args(primarycolor='00AAFF')
effect_args = SubTextHighlight.effects_args((50, 50))
sub_edit = SubTextHighlight.Subtitle_Edit(sub_args, highlight_args, effect_args)
sub_edit()
```
If you want even more examples see the test code in `example_code.py`.

# We welcome feedback and feature suggestions!
This project aims to be feature-rich and highly customizable. While it's actively maintained, major updates may take time as they require careful planning. Your ideas and contributions are greatly appreciated. We hope you find this package useful and enjoyable in your own projects.