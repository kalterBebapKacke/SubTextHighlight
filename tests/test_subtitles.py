from pathlib import Path
import pytest
import SubtitleFX
import pysubs2
import os
import logging
import sys

UPDATE_GOLDEN = os.environ.get("UPDATE_GOLDEN", "false").lower() == "true"
# Define test cases
TEST_CASES = [
    (
        "one_word_only_and_fade",
        {
            "subtitle_type": SubtitleFX.Formatters.one_word,
            "fill_sub_times": True,
            "char_max": 0,
            "fade": (50, 50),
        }
    ),
    (
        "separate_on_period_and_highlighting",
        {
            "subtitle_type": SubtitleFX.Formatters.sentence,
            "fill_sub_times": False,
            "char_max": 11,
            "highlight_word_max": 0,
        }
    ),
    (
        "join_and_word_max",
        {
            "subtitle_type": SubtitleFX.Formatters.joined,
            "fill_sub_times": False,
            "char_max": 20,
        }
    ),
    (
        "appear",
        {
            "subtitle_type": SubtitleFX.Formatters.joined,
            "fill_sub_times": False,
            "char_max": 20,
            "fade": (50, 50),
            "appear": True,
        }
    ),
    (
        "rounded_borders",
        {
            "subtitle_type": SubtitleFX.Formatters.joined,
            "fill_sub_times": False,
            "char_max": 20,
            "fade": (50, 50),
            "rounded_border": True,
        }
    ),
    (
        "rounded_background_highlight",
        {
            "subtitle_type": SubtitleFX.Formatters.sentence,
            "fill_sub_times": False,
            "char_max": 11,
            "highlight_word_max":0,
            "fade": (50, 50),
            "highlight_as_borders": True,
            "docker_config":SubtitleFX.BorderConfig(height_scaling=1.0),
        }
    ),
    (
        "rounded_background_appear",
        {
            "subtitle_type": SubtitleFX.Formatters.sentence,
            "fill_sub_times": False,
            "char_max": 11,
            "rounded_border": True,
            "docker_config":SubtitleFX.BorderConfig(height_scaling=1.0),
            "appear": True,
            "fade": (50, 50),
        }
    ),
]


@pytest.mark.parametrize("name, options", TEST_CASES)
def test_subtitle(tmp_path, name, options):
    # static paths for testing
    base_path = Path("")
    blank_srt_path = base_path / "input" / "blank.srt"
    video_path = base_path / "input" / "plain_video.mp4"

    # dynamic paths based on the parameters
    expected_ass = base_path / "expected" / (name + '.ass')
    output_ass = base_path / "output" / (name + '.ass')

    if name == 'separate_on_period_and_highlighting':
        options["highlight_style"] = SubtitleFX.Style(primarycolor='00AAFF')

    config = SubtitleFX.Config(
        input=str(blank_srt_path),
        output=None,
        input_video=str(video_path),
        alignment=2,
        subtitle_style=SubtitleFX.Style(),
        **options
    )

    config.docker_config.force_install = True

    logging.basicConfig(stream=sys.stdout, level=logging.INFO)

    with SubtitleFX.SubtitleBuild(config) as Builder:
        Builder.run()
        sub_file = Builder.save()

    # Assert
    if UPDATE_GOLDEN:
        sub_file.save(str(expected_ass))
        assert True
    else:
        # Verify
        actual = sub_file.to_string('ass')
        print(actual)

        expected = pysubs2.load(str(expected_ass)).to_string('ass')

        assert actual == expected
