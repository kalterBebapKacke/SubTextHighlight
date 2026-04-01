from . import config
from . import style_class
from typing import Any
import stable_whisper

def fast(
        input:str | dict[str, Any] | list[dict[str, Any]] | stable_whisper.result.WhisperResult,
        output: str | None,
    ):
    conf = config.SubtitleConfig(
        input=input,
        output=output,
    )
    conf.render()
    return conf.save()

def fast_subtitle_file(
        input: str | dict[str, Any] | list[dict[str, Any]] | stable_whisper.result.WhisperResult,
    ):

    conf = config.SubtitleConfig(
        input=input,
        output=None,
    )
    conf.render()
    return conf.save()

def auto_highlight(
    input: str | dict[str, Any] | list[dict[str, Any]] | stable_whisper.result.WhisperResult,
    output: str | None,
    ):

    conf = config.SubtitleConfig(
        input=input,
        output=output,
        highlight_word_max=1,
        highlight_style=style_class.StyleConfig(primarycolor='00AAFF')
    )
    conf.render()
    return conf.save()

def preset_tiktok(
        input: str | dict[str, Any] | list[dict[str, Any]] | stable_whisper.result.WhisperResult,
        output: str | None,
    ):
    conf = config.SubtitleConfig(
        input, output,
        subtitle_type="one_word_only",
        rounded_border=True,
        fill_sub_times=True,
        fade=(20, 20),
        height_scaling=1.0,
    )
    conf.render()
    return conf.save()

def preset_youtube(
        input: str | dict[str, Any] | list[dict[str, Any]] | stable_whisper.result.WhisperResult,
        output: str | None,
    ):
    conf = config.SubtitleConfig(
        input, output,
        rounded_border=True,
        fade=(50, 50),
        word_max=15,
        height_scaling=1.0,
    )
    conf.render()
    return conf.save()

def multiple_edit(
        input: str | dict[str, Any] | list[dict[str, Any]] | stable_whisper.result.WhisperResult,
        output: str | None,
        options: list[dict]
    ):

    results = list()

    for option in options:
        conf = config.SubtitleConfig(
            input, output, **option
        )
        conf.render()
        render_output = conf.save()
        results.append(render_output)

    return results
