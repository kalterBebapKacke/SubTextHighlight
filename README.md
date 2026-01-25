
# SubTextHighlight
**SubTextHighlight** is a comprehensive Python package for generating, formatting, and styling subtitles. It focuses on user-friendliness while providing high-end visual features for video editing and automation.


[![GitHub release (latest by date including pre-releases)](https://img.shields.io/github/v/release/kalterBebapKacke/SubTextHighlight?include_prereleases)](https://img.shields.io/github/v/release/kalterBebapKacke/SubTextHighlight?include_prereleases) \
[![GitHub last commit](https://img.shields.io/github/last-commit/kalterBebapKacke/SubTextHighlight)](https://img.shields.io/github/last-commit/kalterBebapKacke/SubTextHighlight) \
[![GitHub issues](https://img.shields.io/github/issues-raw/kalterBebapKacke/SubTextHighlight)](https://img.shields.io/github/issues-raw/kalterBebapKacke/SubTextHighlight) \
[![GitHub pull requests](https://img.shields.io/github/issues-pr/kalterBebapKacke/SubTextHighlight)](https://img.shields.io/github/issues-pr/kalterBebapKacke/SubTextHighlight) \
[![GitHub](https://img.shields.io/github/license/kalterBebapKacke/SubTextHighlight)](https://img.shields.io/github/license/kalterBebapKacke/SubTextHighlight)

Below is a clip from *1984*, styled using SubTextHighlight as an example:

https://github.com/user-attachments/assets/0a6f01fd-72bb-4dc5-a9e1-9a0d14330490

## Table of Contents

This is a table of contents for your project. It helps the reader navigate through the README quickly.
- [Requirements](#-Requirements)
- [Installation](#-Installation)
- [How to Use](#-How-to-Use)
  - [1. Style Basics](#1-style-basics-utilsargs_styles)
  - [2. Configuration Classes](#2-Configuration-Classes)
  - [3. Advanced Borders (args_border)](#3-Advanced-Borders-args_border)
- [Example Usage](#-Example-Usage)
- [Feedback & Contributions](#Feedback--Contributions)

## 🛠 Requirements

* **FFmpeg**: Must be installed and added to your system PATH.
    * [Download FFmpeg](https://ffmpeg.org/)

## 📦 Installation

Install from PYPI or directly from GitHub:

```bash
# Via pip
pip install SubTextHighlight

# Via GitHub (Latest)
pip install git+[https://github.com/kalterBebapKacke/SubTextHighlight@main](https://github.com/kalterBebapKacke/SubTextHighlight@main)
```

## 🚀 How to Use
This is the script to generate the shown subtitles:
```python
    import SubTextHighlight # import package

    # configure styles and set inputs
    sub_args = SubTextHighlight.sub_args(
        input='./media/plain_video.mp4', # set the input to a video, which will generate the subtitles for me
        output='./media/output_video.mp4', # set the output to a .mp4, so that the subtitles will be burned in
        subtitle_type='separate_on_period', # styling option
        alignment=2,
        fill_sub_times=False,
        # more styling options like size or font
    )
    highlight_args = SubTextHighlight.highlight_args(
        highlight_word_max=0 # only one word will be highlighted
        # Note: The default settings are the same as in sub_args (font, etc), only change what differs as a highlight
        # As the background is used as a highlight, no more settings are needed
    )
    effects_args = SubTextHighlight.effects_args(
        fade=(50,50),
        args_border=SubTextHighlight.args_border() # Just the default settings to use the borders as a highlight
    )

    # generate the subtitles
    SubTextHighlight.Subtitle_Edit(
        sub_args,
        highlight_args,
        effects_args,
    )()
```
The package uses three main configuration classes to control the output. You initialize these classes and pass them to `Subtitle_Edit`:

1. **`sub_args`**: Controls general styling, input/output paths, and transcription settings.
2. **`highlight_args`**: Controls the styling of highlighted words.
3. **`effects_args`**: Controls animations, transitions, and advanced border effects.

### 1. Style Basics (`utils.args_styles`)

Both `sub_args` and `highlight_args` inherit from `utils.args_styles`. These attributes control the visual appearance of your text.

#### **Font & Text Settings**

| Attribute | Type | Default | Description |
| --- | --- | --- | --- |
| `fontname` | `str` | `'Arial'` | Font family (must be installed on system). |
| `fontsize` | `float` | `24` | Font size in points. |
| `bold` | `bool` | `True` | Renders text in bold. |
| `italic` | `bool` | `False` | Renders text in italics. |
| `underline` | `bool` | `False` | Renders text with underline. |
---
#### **Color Settings**

*Accepts `pysubs2.Color` objects or HEX strings (e.g., `'ff0000'`).*

| Attribute | Default | Description |
| --- | --- | --- |
| `primarycolor` | `White` | Main text fill color. |
| `secondarycolor` | `Black` | Used for karaoke/transitional effects. |
| `backcolor` | `Black` | Background color for boxed styles. |
| `outlinecolor` | `Black` | Text outline color. |
---
#### **Layout & Visuals**

| Attribute | Default | Description |
| --- | --- | --- |
| `outline` | `1` | Thickness of text outline (pixels). |
| `shadow` | `0` | Drop shadow offset (pixels). |
| `alignment` | `5` | Numpad positioning (e.g., `2`=Bottom, `5`=Center). |
| `borderstyle` | `1` | `1`: Outline only, `3`: Opaque box. |
| `spacing` | `0.75` | Line spacing multiplier. |

### 2. Configuration Classes

#### `sub_args`

*General subtitle parameters.*

* **`input`** (`str | WhisperResult`): **Required.** Path to file (video/audio/srt) or Whisper result.
* **`output`** (`str`): **Required.** Output path (`.ass`, `.mp4`, or `None` to return the pysubs2 SSA_File object).
* **`subtitle_type`** (`str`):
* `'one_word_only'`: One word per subtitle.
* `'join'`: Join words based on `word_max`.
* `'separate_on_period'`: Split at the sentence ends.


* **`whisper_model`** (`str`): Model name (e.g., `'medium.en'`).
* **`whisper_refine`** (`bool`): Refine timestamps (English only).

---

#### `highlight_args`

*Highlight specific words.*

Inherits all style attributes from above. If an attribute is set to `None`, it defaults to the value set in `sub_args`.

* **`highlight_word_max`** (`int`): Number of words to highlight at once (`0` = single word).

---
#### `effects_args`

*Transitions and borders.*

* **`fade`** (`tuple[float, float]`): `(FadeIn, FadeOut)` duration in milliseconds.
* **`appear`** (`bool`): If `True`, words appear cumulatively rather than replacing each other.
* **`args_border`** (`args_border | None`): Configuration for advanced border/box rendering.

### 3. Advanced Borders (`args_border`)

Use the `args_border` class to create custom background boxes or border effects. Pass this object to `effects_args`.

```python
border_conf = SubTextHighlight.args_border(
    offset=6,
    radius=10,
    color="FF0000"
)
effects = SubTextHighlight.effects_args(args_border=border_conf)

```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `offset` | `int` | `6` | Padding between text and border edge. |
| `radius` | `int` | `6` | Corner radius for rounded boxes. |
| `transformy` | `int` | `1` | Vertical shift/correction. |
| `height_scaling` | `float` | `1.2` | Multiplier for border height relative to text. |
| `color` | `Color` | `None` | Border color. Defaults to White if None. |
| `use_borders_as_highlight` | `bool` | `False` | If True, uses the border style to indicate highlights. |
| `container_run_func` | `func` | `None` | Custom function for containerized rendering. |

## 💻 Example Usage

### 1. Burned-in Subtitles with Highlights

```python
import SubTextHighlight

# Define Input/Output
input_file = './media/plain_video.webm'
output_file = './media/edited_video.mp4'

# 1. Configure General Settings
sub_args = SubTextHighlight.sub_args(
    input=input_file,
    output=output_file,
    input_video=input_file,
    subtitle_type='separate_on_period',
    fontname='Arial Rounded MT Bold',
    alignment=2,
    whisper_refine=True
)

# 2. Configure Highlights (Blue text)
highlight_args = SubTextHighlight.highlight_args(
    primarycolor='00AAFF'
)

# 3. Configure Effects (Fade + Custom Border)
border_settings = SubTextHighlight.args_border(
    radius=10, 
    color='000000', 
    height_scaling=1.1
)
effect_args = SubTextHighlight.effects_args(
    fade=(50, 50), 
    args_border=border_settings
)

# 4. Run
sub_edit = SubTextHighlight.Subtitle_Edit(sub_args, highlight_args, effect_args)
sub_edit()

```

### 2. Generate `.ass` File Only

```python
import SubTextHighlight

sub_args = SubTextHighlight.sub_args(
    input='./media/plain_video.webm', 
    output='./media/subtitles.ass',
    subtitle_type='separate_on_period'
)
# ... initialize other args as needed
sub_edit = SubTextHighlight.Subtitle_Edit(sub_args, None, None)
sub_edit()

```

# Feedback & Contributions

We welcome feedback! This project aims to be highly customizable. Please feel free to open issues or submit PRs on GitHub.


