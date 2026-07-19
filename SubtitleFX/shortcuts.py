from . import config
from .styles.style_class import StyleConfig
from typing import Any
import stable_whisper
from .formatters import register

def fast(
        input:str | dict[str, Any] | list[dict[str, Any]] | stable_whisper.result.WhisperResult,
        output: str | None,
        input_video: str | None = None
    ):
    conf = config.SubtitleConfig(
        input=input,
        output=output,
        input_video=input_video,
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

def fast_highlight(
        input: str | dict[str, Any] | list[dict[str, Any]] | stable_whisper.result.WhisperResult,
        output: str | None,
        input_video: str | None = None
    ):

    conf = config.SubtitleConfig(
        input=input,
        output=output,
        input_video=input_video,
        highlight_word_max=1,
        highlight_style=StyleConfig(primarycolor='00AAFF')
    )
    conf.render()
    return conf.save()

def preset_tiktok(
        input: str | dict[str, Any] | list[dict[str, Any]] | stable_whisper.result.WhisperResult,
        output: str | None,
        input_video: str | None = None
    ):
    conf = config.SubtitleConfig(
        input, output, input_video,
        subtitle_type=register.Formatters.one_word,
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
        input_video: str | None = None
    ):
    conf = config.SubtitleConfig(
        input, output, input_video,
        subtitle_type=register.Formatters.sentence,
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
        options: list[dict],
        input_video: str | None = None,
    ):

    results = list()

    for option in options:

        if 'input_video' not in option and input_video is not None:
            option['input_video'] = input_video

        conf = config.SubtitleConfig(
            input, output, **option
        )
        conf.render()
        render_output = conf.save()
        results.append(render_output)

    return results
