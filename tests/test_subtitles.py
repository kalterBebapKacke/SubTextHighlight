from pathlib import Path
import pytest
import SubTextHighlight
import pysubs2
import os

UPDATE_GOLDEN = os.environ.get("UPDATE_GOLDEN", "false").lower() == "true"
# Define test cases
TEST_CASES = [
    (
        "one_word_only_and_fade",
        {
            "subtitle_type": 'one_word_only',
            "fill_sub_times": True,
            "word_max": 0,
            "fade": (50, 50),
        }
    ),
    (
        "separate_on_period_and_highlighting",
        {
            "subtitle_type": 'separate_on_period',
            "fill_sub_times": False,
            "word_max": 11,
            "highlight_word_max": 0,
        }
    ),
    (
        "join_and_word_max",
        {
            "subtitle_type": 'join',
            "fill_sub_times": False,
            "word_max": 20,
        }
    ),
    (
        "appear",
        {
            "subtitle_type": 'join',
            "fill_sub_times": False,
            "word_max": 20,
            "fade": (50, 50),
            "appear": True,
        }
    ),
    (
        "rounded_borders",
        {
            "subtitle_type": 'join',
            "fill_sub_times": False,
            "word_max": 20,
            "fade": (50, 50),
            "rounded_border": True,
        }
    ),
    (
        "rounded_background_highlight",
        {
            "subtitle_type": 'separate_on_period',
            "fill_sub_times": False,
            "word_max": 11,
            "highlight_word_max":0,
            "fade": (50, 50),
            "highlight_as_borders": True,
            "height_scaling":1.0,
        }
    ),
    (
        "rounded_background_appear",
        {
            "subtitle_type": 'separate_on_period',
            "fill_sub_times": False,
            "word_max": 11,
            "rounded_border": True,
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
        options["highlight_style"] = SubTextHighlight.StyleConfig(primarycolor='00AAFF')

    config = SubTextHighlight.SubtitleConfig(
        input=str(blank_srt_path),
        output=None,
        input_video=str(video_path),
        alignment=2,
        subtitle_style=SubTextHighlight.StyleConfig(),
        force_install=True,
        **options
    )

    config.render()

    sub_file: pysubs2.SSAFile = config.save()

    sub_file.save(str(output_ass))

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
