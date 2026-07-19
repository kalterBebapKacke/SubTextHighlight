from . import config
from .main import SubtitleBuild
from . import utils
from typing import Any
import stable_whisper
from .formatters import Formatters
from .utils import Style

def fast(
        input:str | dict[str, Any] | list[dict[str, Any]] | stable_whisper.result.WhisperResult,
        output: str | None,
        input_video: str | None = None
    ):
    conf = config.Config(
        input=input,
        output=output,
        input_video=input_video,
        subtitle_type=Formatters.joined,
    )
    with SubtitleBuild(conf) as build:
        build.run()
        return build.save()

def fast_subtitle_file(
        input: str | dict[str, Any] | list[dict[str, Any]] | stable_whisper.result.WhisperResult,
    ):

    conf = config.Config(
        input=input,
        output=None,
        subtitle_type=Formatters.joined,
    )
    with SubtitleBuild(conf) as build:
        build.run()
        return build.save()

def fast_highlight(
        input: str | dict[str, Any] | list[dict[str, Any]] | stable_whisper.result.WhisperResult,
        output: str | None,
        input_video: str | None = None
    ):

    conf = config.Config(
        input=input,
        output=output,
        input_video=input_video,
        subtitle_type=Formatters.joined,
        highlight_word_max=1,
        highlight_style=Style(primarycolor='00AAFF')
    )
    with SubtitleBuild(conf) as build:
        build.run()
        return build.save()

def preset_tiktok(
        input: str | dict[str, Any] | list[dict[str, Any]] | stable_whisper.result.WhisperResult,
        output: str | None,
        input_video: str | None = None
    ):
    conf = config.Config(
        input=input,
        output=output,
        input_video=input_video,
        subtitle_type=Formatters.one_word,
        rounded_border=True,
        fill_sub_times=True,
        fade=(20, 20),
        border_config=utils.BorderConfig(height_scaling=1.0),
    )
    with SubtitleBuild(conf) as build:
        build.run()
        return build.save()

def preset_youtube(
        input: str | dict[str, Any] | list[dict[str, Any]] | stable_whisper.result.WhisperResult,
        output: str | None,
        input_video: str | None = None
    ):
    conf = config.Config(
        input=input,
        output=output,
        input_video=input_video,
        subtitle_type=Formatters.sentence,
        rounded_border=True,
        fade=(50, 50),
        char_max=15,
        border_config=utils.BorderConfig(height_scaling=1.0),
    )
    with SubtitleBuild(conf) as build:
        build.run()
        return build.save()

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
        option.setdefault('subtitle_type', Formatters.joined)

        conf = config.Config(
            input=input, output=output, **option
        )
        with SubtitleBuild(conf) as build:
            build.run()
            results.append(build.save())

    return results
