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

- [Requirements](#-requirements)
- [Installation](#-installation)
- [How to Use](#-how-to-use)
  - [1. SubtitleConfig — The Single Entry Point](#1-subtitleconfig--the-single-entry-point)
  - [2. StyleConfig — Text Appearance](#2-styleconfig--text-appearance)
  - [3. Highlight Options](#3-highlight-options)
  - [4. Effects & Borders](#4-effects--borders)
  - [5. Whisper / Transcription](#5-whisper--transcription)
- [Example Usage](#-example-usage)
- [Feedback & Contributions](#feedback--contributions)

---

## 🛠 Requirements

* **FFmpeg**: Must be installed and added to your system PATH.
    * [Download FFmpeg](https://ffmpeg.org/)

## 📦 Installation

```bash
# Via pip
pip install SubTextHighlight

# Via GitHub (latest)
pip install git+https://github.com/kalterBebapKacke/SubTextHighlight@main
```

---

## 🚀 How to Use

### 1. `SubtitleConfig` — The Single Entry Point

The API has been consolidated into a single configuration class: **`SubtitleConfig`**. Instead of instantiating and passing multiple separate argument classes, you now configure everything in one place and call `.render()` followed by `.save()`.

```python
from SubTextHighlight import SubtitleConfig, StyleConfig, preset_youtube
    input = './tests/input/plain_video.mp4'  # set the input to a video, which will generate the subtitles for me
    output = './media/output_video.mp4'  # set the output to a .mp4, so that the subtitles will be burned in

    conf = SubtitleConfig(
        input, output,
        subtitle_type='separate_on_period',
        fill_sub_times=False,
        subtitle_style=StyleConfig(alignment=2),
        highlight_style=StyleConfig(primarycolor='00AAFF'),
        highlight_word_max=0,
        highlight_as_borders=True,
        fade=(50, 50),
    )
    conf.render()
    conf.save()

    # Or use the youtube preset, that gives a similar result
    preset_youtube(input, output)
```

`render()` processes the input and generates the subtitle data. `save()` writes the output and returns the output path (or `None` if no file was written).

---

#### Full Parameter Reference

##### Input / Output

| Parameter | Type | Default | Description |
|---|---|---|---|
| `input` | `str \| dict \| list[dict] \| WhisperResult` | **required** | Path to a video/audio/srt file, a raw transcript dict, or a stable-whisper result. |
| `output` | `str \| None` | **required** | Output path (`.ass`, `.mp4`). Pass `None` to return the `pysubs2.SSAFile` object directly from `save()`. |
| `input_video` | `str \| None` | `None` | Separate video file path, if the subtitle input differs from the video to burn into. |

##### Subtitle Layout

| Parameter | Type | Default | Description |
|---|---|---|---|
| `subtitle_type` | `str` | `'join'` | `'one_word_only'`, `'join'` (group by `word_max`), or `'separate_on_period'` (split at sentence ends). |
| `word_max` | `int` | `11` | Maximum words per subtitle line when using `'join'` mode. |
| `add_time` | `float` | `0.0` | Time offset (seconds) added to all subtitle timestamps. |
| `fill_sub_times` | `bool` | `True` | Automatically fill gaps between subtitle lines. |

---

### 2. `StyleConfig` — Text Appearance

Visual styling is now handled by **`StyleConfig`** objects. Pass one to `subtitle_style` for the main text and optionally another to `highlight_style` for highlighted words.

```python
from SubTextHighlight import StyleConfig

main_style = StyleConfig(
    fontname='Arial Rounded MT Bold',
    fontsize=28,
    primarycolor='FFFFFF',
    borderstyle=3,
)
```

#### Font & Text

| Attribute | Type | Default | Description |
|---|---|---|---|
| `fontname` | `str` | `'Arial'` | Font family (must be installed on the system). |
| `fontsize` | `float` | `24` | Font size in points. |
| `bold` | `bool` | `True` | Bold text. |
| `italic` | `bool` | `False` | Italic text. |
| `underline` | `bool` | `False` | Underlined text. |

#### Colors

*Accepts `pysubs2.Color` objects or HEX strings (e.g. `'FF0000'`).*

| Attribute | Default | Description |
|---|---|---|
| `primarycolor` | White | Main text fill color. |
| `secondarycolor` | Black | Used for karaoke/transitional effects. |
| `backcolor` | Black | Background color for boxed styles. |
| `outlinecolor` | Black | Text outline color. |

#### Layout & Visuals

| Attribute | Default | Description |
|---|---|---|
| `outline` | `1` | Outline thickness in pixels. |
| `shadow` | `0` | Drop shadow offset in pixels. |
| `alignment` | `5` | Numpad positioning (`2` = bottom center, `5` = center). |
| `borderstyle` | `1` | `1`: Outline only, `3`: Opaque box. |
| `spacing` | `0.75` | Line spacing multiplier. |

---

### 3. Highlight Options

| Parameter | Type | Default | Description |
|---|---|---|---|
| `highlight_style` | `StyleConfig \| None` | `None` | Style for highlighted words. Attributes left at `None` inherit from `subtitle_style`. |
| `highlight_word_max` | `int \| None` | `None` | Number of words highlighted at once. `0` = single word. `None` disables highlighting. |
| `highlight_as_borders` | `bool` | `False` | Use the rounded border effect as the highlight indicator instead of a text color change. Cannot be combined with `appear=True`. |

---

### 4. Effects & Borders

#### Fade & Appear

| Parameter | Type | Default | Description |
|---|---|---|---|
| `fade` | `tuple[float, float]` | `(0.0, 0.0)` | `(fade_in, fade_out)` duration in milliseconds. |
| `appear` | `bool` | `False` | Words appear cumulatively rather than replacing each other. |

#### Rounded Borders

Set `rounded_border=True` to enable custom background box rendering. The border parameters below control its appearance.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `rounded_border` | `bool` | `False` | Enable rounded background border rendering. |
| `offset` | `int` | `6` | Padding between text and border edge. |
| `radius` | `int` | `6` | Corner radius. |
| `transformy` | `int` | `1` | Vertical shift/correction for the border. |
| `height_scaling` | `float` | `1.2` | Border height multiplier relative to text height. |
| `color` | `pysubs2.Color \| None` | `None` | Border fill color. Defaults to white if `None`. |

#### Docker / Rendering Backend

These parameters control the containerised rendering pipeline used for advanced border effects.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `fonts_path` | `list \| str \| None` | `None` | Path(s) to custom font directories to mount. |
| `packages` | `list[str] \| None` | `None` | Extra system packages to install inside the container. |
| `container_run_func` | `callable \| None` | `None` | Custom function for containerised rendering. |
| `force_install` | `bool` | `False` | Force reinstallation of container dependencies. |
| `docker_verbose` | `bool` | `False` | Print verbose Docker output. |
| `docker_traceback` | `bool` | `False` | Show full tracebacks from inside the container. |

---

### 5. Whisper / Transcription

When `input` is a video or audio file, SubTextHighlight will transcribe it automatically using [stable-whisper](https://github.com/jianfch/stable-ts).

| Parameter | Type | Default | Description |
|---|---|---|---|
| `whisper_model` | `str` | `'medium.en'` | Whisper model name (e.g. `'base'`, `'large-v3'`). |
| `whisper_device` | `str` | `'cpu'` | Device for inference (`'cpu'` or `'cuda'`). |
| `whisper_refine` | `bool` | `False` | Refine word-level timestamps (English only). |

---

### 6. Shortcuts & Presets
The `presets` module contains pre-configured styles and settings for common use cases. For example, `preset_youtube()` applies a popular YouTube-style subtitle format with a single function call.

The presets here include:
1. `preset_youtube` — A modern, clean style inspired by YouTube's default captions.
2. `preset_tiktok` — A clean style with a rounded border, inspired by TikTok's captions.
3. `fast` — Create a subtitle file/render it with minimal processing and default styling, for quick results.
4. `fast_subtitle_file` — Generate a subtitle file with minimal processing and default styling, without rendering a video, just returning the `pysubs2.SSA_File` object.
5. `fast_highlight` — Create a simple subtitle file or video with simple word-level highlighting, without advanced effects or styling.

---

## Feedback & Contributions

Feedback is always welcome! Please feel free to open issues on GitHub.
I am not finished with this project and there are many features I want to add, so if you have any suggestions or want to contribute, please do not hesitate to reach out.