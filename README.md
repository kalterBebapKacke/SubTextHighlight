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

For example, 1 = bottom-left, 5 = center, 9 = top-right.

`spacing: float | int (default: 0.75)`
Line spacing multiplier. Use values < 1 for tighter spacing or > 1 for looser spacing.

`angle: float (default: 0.0)`
Rotation angle in degrees. Positive = clockwise, negative = counter-clockwise.

## sub_args
Inherits all styles options from `utils.args_styles`

The following are the configurable parameters for subtitle generation:

- **`input`** (`str` or whisper transcript output form, *required*):  
  Path to the input file (e.g., video or transcript) or whisper transcript to be processed. Valid inputs are srt, ass, video, audio or plain text srt in srt string. If input is a video or audio, whisper will automatically transcribe the audio. If input is in srt or ass format (whether in plain str or as an input file) has to only contain one word per subtitle segment, otherwise the formatting might not work. Also a plain `stable_whisper.result.WhisperResult` can be inputted, when for example generating your own subtitles with stable whisper.

- **`output`** (`str`, *required*):  
  Path to where the output file should be stored. The file has to be either stored as an ass-file, or a video path (via **`input_video`**) could be inputted to make ffmpeg automatically burn in the subs into the output video. Be careful to use the right file extension. If output is `None`, then calling the edit class will return the `pysubs2.SSAFile` class of the formated subtitle.

- **`input_video`** (`str` or `None`, *optional*): 
  Path to the video where the subtitles could be burned in if wanted, if not leave this argument `None`. 

- **`subtitle_type`** (`str`, *optional*, default=`'one_word_only'`):  
  Determines the subtitle formatting style. Available options:  
  - `'one_word_only'`: Shows one word at a time.
  - `'join'`: Joins all words into subtitles segments with respect to the **`word_max`** parameter.
  - `'separate_on_period'`: Splits subtitles at sentence boundaries (periods).

- **`word_max`** (`int`, *optional*, default=`11`):  
  Maximum number of characters per subtitle segment, without breaking words in half. Ignored in `'one_word_only'` mode.

- **`add_time`** (`float`, *optional*, default=`0`):  
  Extra time in seconds to add to each subtitle's display duration. Useful for adjusting readability speed or if something like an intro is played at the start.

- **`fill_sub_times`** (`float`, *optional*, default=`0`):
  Decides whether to fill the time between the end of one segment and the next one. 

- **`whisper_model`** (`str`, *optional*, default=`medium.en`):  
  Controls which whisper model should be used. To see the list of available models please refer to the [Whisper GitHub Repository](https://github.com/openai/whisper).

- **`whisper_refine`** (`bool`, *optional*, default=`False`):  
  Whether the results are refined for better timestamps. This can make computing the subtitles more complex, but also yields a better result. This option is here to give a little bit of refinement right out of the box, but for even better results making own whisper predictions is recommended. See the [Stable TTS GitHub Repository](https://github.com/jianfch/stable-ts/tree/main).

## highlight_args
Here the class again inherits all the parameters from `utils.args_styles`, but now for all attributes is the default attribute `None`. When this is the case the styling of the `sub_args` will be copied. Only non `None` values will decide how the highlighted segment will look like.

The only really new parameter is **`highlight_word_max`** (`int | None`, *required*, default=`0`), which controls how many words should be highlighted. If this argument is 0, then only one word will be highlighted.

## effects_args
Controls the effects that should be applied to the subtitles.

- **`fade`** (`tuple[float, float]`, *optional*, default=`(0.0, 0.0)`):  
  - Controls the fade-in and fade-out durations.
  - fade[0]: Duration of fade-in (in ms).
  - fade[1]: Duration of fade-out (in ms).
  Defaults to (0.0, 0.0) — no fading.
  - **`'appear'`** (`bool`, *optional*, default=`False`): Words appear cumulatively (i.e., new words are added while retaining previous ones). How many words should reappear during each segment can be controlled via the highlight_args and its attribute `highlight_word_max`. For this effect to work the highlight_args dont have to be set. If the highlight_args are `None` then the program will automatically use a Highlighter with the default arguments.

## Example Usage
This code for example creates the example video from above, that can also be found in `media`. 
```python
import SubTextHighlight

input = './media/plain_video.webm'
output = './media/edited_video.mp4'
sub_args = SubTextHighlight.sub_args(input=input, output=output, input_video=input, subtitle_type='separate_on_period', fill_sub_times=False, alignment=2)
highlight_args =  SubTextHighlight.highlight_args(primarycolor='00AAFF')
effect_args = SubTextHighlight.effects_args((50, 50))
sub_edit = SubTextHighlight.Subtitle_Edit(sub_args, highlight_args, effect_args)
sub_edit()
```

This code for example creates the ass-transcript to the example video from above.
```python
import SubTextHighlight

input = './media/plain_video.webm'
output = './media/subtitles.ass'
sub_args = SubTextHighlight.sub_args(input=input, output=output, subtitle_type='separate_on_period', fill_sub_times=False, alignment=2)
highlight_args =  SubTextHighlight.highlight_args(primarycolor='00AAFF')
effect_args = SubTextHighlight.effects_args((50, 50))
sub_edit = SubTextHighlight.Subtitle_Edit(sub_args, highlight_args, effect_args)
sub_edit()
```
If you want even more examples see the test code in `example_code.py`.

# Feedback and Suggestions
Feel free 