# SubtitleFX
**SubtitleFX** is a comprehensive Python package for generating, formatting, and styling subtitles. It focuses on user-friendliness while providing high-end visual features for video editing and automation.


[![GitHub release (latest by date including pre-releases)](https://img.shields.io/github/v/release/moonlitmarigold/SubTextHighlight?include_prereleases)](https://img.shields.io/github/v/release/moonlitmarigold/SubTextHighlight?include_prereleases) \
[![GitHub last commit](https://img.shields.io/github/last-commit/moonlitmarigold/SubTextHighlight)](https://img.shields.io/github/last-commit/moonlitmarigold/SubTextHighlight) \
[![GitHub issues](https://img.shields.io/github/issues-raw/moonlitmarigold/SubTextHighlight)](https://img.shields.io/github/issues-raw/moonlitmarigold/SubTextHighlight) \
[![GitHub pull requests](https://img.shields.io/github/issues-pr/moonlitmarigold/SubTextHighlight)](https://img.shields.io/github/issues-pr/moonlitmarigold/SubTextHighlight) \
[![GitHub](https://img.shields.io/github/license/moonlitmarigold/SubTextHighlight)](https://img.shields.io/github/license/moonlitmarigold/SubTextHighlight)

Below is a clip from *1984*, styled using SubtitleFX as an example:

https://github.com/user-attachments/assets/0a6f01fd-72bb-4dc5-a9e1-9a0d14330490

## Table of Contents

- [Requirements](#-requirements)
- [Installation](#-installation)
- [How to Use](#-how-to-use)
  - [1. Config & SubtitleBuild — The Single Entry Point](#1-config--subtitlebuild--the-single-entry-point)
  - [2. Style — Text Appearance](#2-style--text-appearance)
  - [3. Highlight Options](#3-highlight-options)
  - [4. Effects & Borders](#4-effects--borders)
  - [5. Whisper / Transcription](#5-whisper--transcription)
  - [6. Shortcuts & Presets](#6-shortcuts--presets)
- [Feedback & Contributions](#feedback--contributions)

---

## 🛠 Requirements

* **FFmpeg**: Must be installed and added to your system PATH.
    * [Download FFmpeg](https://ffmpeg.org/)
* **Docker**: Only required if you use `rounded_border` or `highlight_as_borders` — these effects render through a containerised backend.

## 📦 Installation

```bash
# Via pip
pip install SubtitleFX

# Via GitHub (latest)
pip install git+https://github.com/moonlitmarigold/SubTextHighlight.git@main
```

---

## 🚀 How to Use

### 1. `Config` & `SubtitleBuild` — The Single Entry Point

All settings live on a single **`Config`** object (a Pydantic model). To actually build subtitles, pass it to **`SubtitleBuild`**, used as a context manager: `run()` executes the pipeline, `save()` writes the output (or returns the `pysubs2.SSAFile` object directly if `output=None`).

```python
    from SubtitleFX import Config, SubtitleBuild, Style, Formatters, preset_youtube

    input = './tests/input/plain_video.mp4'  # set the input to a video, which will generate the subtitles for me
    output = './media/output_video.mp4'  # set the output to a .mp4, so that the subtitles will be burned in

    conf = Config(
        input=input,
        output=output,
        subtitle_type=Formatters.sentence,
        fill_sub_times=False,
        alignment=2,
        highlight_style=Style(primarycolor='00AAFF'),
        highlight_char_max=0,
        highlight_as_borders=True,
        fade=(50, 50),
    )

    with SubtitleBuild(conf) as build:
        build.run()
        build.save()

    # Or use the youtube preset, that gives a similar result
    preset_youtube(input, output)
```

`run()` processes the input and generates the subtitle data (`SubtitleBuild` also returns `self`, so `build.run().save()` chains fine). `save()` writes the output and returns the output path, or the `pysubs2.SSAFile` object if `output=None`.

Need to change a setting after the fact? `SubtitleBuild.change(**kwargs)` updates the `Config` in place and rebuilds the pipeline if it's already been entered, so the new value actually takes effect on the next `run()`:

```python
with SubtitleBuild(conf) as build:
    build.change(input='another_file.srt', fade=(20, 20))
    build.run()
    build.save()
```

---

#### Full Parameter Reference

##### Input / Output

| Parameter | Type | Default | Description |
|---|---|---|---|
| `input` | `str \| dict \| list[dict] \| WhisperResult \| pysubs2.SSAFile` | **required** | Path to a video/audio/srt file, a raw transcript dict, a stable-whisper result, or an existing `SSAFile`. |
| `output` | `str \| None` | **required** | Output path (`.ass`, or a video file to burn subtitles into). Pass `None` to get the `pysubs2.SSAFile` object back from `save()` instead of writing a file. |
| `input_video` | `str \| None` | `None` | Separate video file path, if the subtitle input differs from the video to burn into. |
| `resolution` | `tuple[int, int] \| None` | `None` | Explicit `(width, height)`. Inferred from `input`/`input_video` when possible; only required if neither is a video and `rounded_border` is used. |
| `duration` | `float \| None` | `None` | Explicit duration in seconds. Inferred from `input`/`input_video` via `ffprobe` when possible; set this if neither is a media file and `fill_sub_times` needs a duration to fill gaps up to. |

##### Subtitle Layout

| Parameter | Type | Default | Description |
|---|---|---|---|
| `subtitle_type` | `str` (use the `Formatters` enum) | **required** | `Formatters.one_word`, `Formatters.joined` (group by `char_max`), or `Formatters.sentence` (split at sentence-ending punctuation). |
| `subtitle_style` | `Style` | `Style()` | Style for the main subtitle text — see [Style](#2-style--text-appearance). |
| `char_max` | `int` | `11` | Maximum characters per subtitle line when using `Formatters.joined`. |
| `add_time_seconds` | `float` | `0.0` | Time offset (seconds) added to all subtitle timestamps. |
| `fill_sub_times` | `bool` | `True` | Automatically fill gaps between subtitle lines up to the next line / end of video. Requires a known video duration — pair with `input_video`, or an `input` that's itself a video/audio file. |
| `alignment` | `int` | `2` | Numpad positioning (`2` = bottom center, `5` = center). |

`subtitle_type` is imported via `from SubtitleFX import Formatters`. The available options are `Formatters.one_word`, `Formatters.joined`, and `Formatters.sentence`.

---

### 2. `Style` — Text Appearance

Visual styling is handled by **`Style`** objects. Pass one to `subtitle_style` for the main text and optionally another to `highlight_style` for highlighted words — any attribute you don't explicitly set on `highlight_style` inherits from `subtitle_style` at render time.

```python
from SubtitleFX import Style

main_style = Style(
    fontname='Arial Rounded MT Bold',
    fontsize=28,
    primarycolor='FFFFFF',
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
| `angle` | `float` | `0.0` | Rotation angle in degrees. |

#### Colors

*Accepts hex strings (e.g. `'FF0000'`), `pysubs2.Color` objects, `(r, g, b)`/`(r, g, b, a)` tuples, or dicts.*

| Attribute | Default | Description |
|---|---|---|
| `primarycolor` | White | Main text fill color. |
| `secondarycolor` | Black | Used for karaoke/transitional effects. |
| `backcolor` | Black | Background color for boxed styles. |
| `outlinecolor` | Black | Text outline color. |
| `tertiarycolor` | Black | Secondary outline color. |

#### Layout & Visuals

| Attribute | Default | Description |
|---|---|---|
| `outline` | `1` | Outline thickness in pixels. |
| `shadow` | `0` | Drop shadow offset in pixels. |
| `spacing` | `0.75` | Line spacing multiplier. |

Note: `alignment` is not set through `Style(...)` directly — it's driven by `Config.alignment` and applied automatically by the rendering pipeline.

---

### 3. Highlight Options

| Parameter | Type | Default | Description |
|---|---|---|---|
| `highlight_style` | `Style \| None` | `None` | Style for highlighted words. Attributes left unset inherit from `subtitle_style`. |
| `highlight_char_max` | `int \| None` | `None` | Number of characters highlighted together at once. `0` = single word. `None` disables highlighting. |
| `highlight_as_borders` | `bool` | `False` | Use the rounded border effect as the highlight indicator instead of a text color change. Cannot be combined with `appear=True`. |

---

### 4. Effects & Borders

#### Fade & Appear

| Parameter | Type | Default | Description |
|---|---|---|---|
| `fade` | `tuple[float, float]` | `(0.0, 0.0)` | `(fade_in, fade_out)` duration in milliseconds. |
| `appear` | `bool` | `False` | Words appear cumulatively rather than replacing each other. |
| `rounded_border` | `bool` | `False` | Enable the rounded background box behind the text — configured via `border_config` below. Renders through Docker. |
| `container` | `Container \| None` | `None` | An existing container to render through, instead of booting a fresh one per `run()`. Usually set via `SubtitleBuild.set_container()` — see [Docker / Rendering Backend](#docker--rendering-backend). |

#### Rounded Borders

Set `rounded_border=True` to enable custom background box rendering. Its appearance is controlled by a nested `border_config`:

```python
from SubtitleFX import Config, BorderConfig

conf = Config(
    ...,
    rounded_border=True,
    border_config=BorderConfig(height_scaling=1.0, radius=10),
)
```

| `border_config` field | Type | Default | Description |
|---|---|---|---|
| `offset` | `int` | `6` | Padding between text and border edge. |
| `radius` | `int` | `6` | Corner radius. |
| `transformy` | `int` | `1` | Vertical shift/correction for the border. |
| `height_scaling` | `float` | `1.2` | Border height multiplier relative to text height. |
| `color` | `Color` | Black | Border fill color. Accepts the same values as `Style` colors. |

#### Docker / Rendering Backend

Rounded borders render through a containerised backend, configured via a nested `docker_config`:

```python
from SubtitleFX import Config, DockerConfig

conf = Config(
    ...,
    rounded_border=True,
    docker_config=DockerConfig(force_install=True, fonts_path='./fonts'),
)
```

| `docker_config` field | Type | Default | Description |
|---|---|---|---|
| `fonts_path` | `list \| str \| None` | `None` | Path(s) to custom font directories to mount into the container. |
| `packages` | `list[str] \| None` | `None` | Extra system packages to install inside the container. |
| `force_install` | `bool` | `False` | Install Docker automatically if it's missing, instead of prompting. |
| `traceback` | `bool` | `False` | Show full tracebacks from inside the container. |

By default, `SubtitleBuild` boots a fresh container for every `run()` and pauses it afterward. If you're rendering several variants of the same input (see `multiple_edit` below), or otherwise want to reuse one container across multiple builds instead of paying container-startup cost each time, create it explicitly and attach it via `Config.container` / `SubtitleBuild.set_container()`:

```python
from SubtitleFX import Config, SubtitleBuild, Container

conf = Config(..., rounded_border=True)
container = Container.return_base_container(conf)  # boots one container, using conf.docker_config

with SubtitleBuild(conf) as build:
    build.set_container(container)
    build.run()
    build.save()
```

`set_container()` behaves like `change()`: it rebuilds the pipeline if it's already been entered, so the container takes effect on the next `run()` even when set after entering the `with` block. The container is left paused between builds and is only torn down once the `Container` object is garbage-collected.

---

### 5. Whisper / Transcription

When `input` is a video or audio file, SubtitleFX will transcribe it automatically using [stable-whisper](https://github.com/jianfch/stable-ts). Whisper behavior is configured via a nested `whisper_config`:

```python
from SubtitleFX import Config, WhisperConfig

conf = Config(
    ...,
    whisper_config=WhisperConfig(model='large-v3', device='cuda'),
)
```

| `whisper_config` field | Type | Default | Description |
|---|---|---|---|
| `model` | `str` | `'medium.en'` | Whisper model name (e.g. `'base'`, `'large-v3'`). |
| `device` | `str` | `'cpu'` | Device for inference (`'cpu'` or `'cuda'`). |
| `refine` | `bool` | `False` | Refine word-level timestamps (English only). |

---

### 6. Shortcuts & Presets

For common cases, `SubtitleFX` ships ready-made functions that build the `Config`, run the pipeline, and save the result in one call:

1. `preset_youtube` — A modern, clean style inspired by YouTube's default captions.
2. `preset_tiktok` — A clean style with a rounded border, inspired by TikTok's captions.
3. `fast` — Create a subtitle file/render it with minimal processing and default styling, for quick results.
4. `fast_subtitle_file` — Generate a subtitle file with minimal processing and default styling, without rendering a video, just returning the `pysubs2.SSAFile` object.
5. `fast_highlight` — Create a simple subtitle file or video with simple word-level highlighting, without advanced effects or styling.
6. `multiple_edit(input, output, options, input_video=None)` — Render the same input multiple times with different `Config` overrides. `options` is a list of kwarg dicts, one per variant; returns a list of results in the same order. A single Docker container is created once, from the first entry in `options`, and reused across every variant instead of being rebuilt per option.

---

## Feedback & Contributions

Feedback is always welcome! Please feel free to open issues on GitHub.
I am not finished with this project and there are many features I want to add, so if you have any suggestions or want to contribute, please do not hesitate to reach out.
