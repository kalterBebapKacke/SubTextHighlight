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
            "highlight_args": None,
            "effect_args": SubTextHighlight.effects_args(fade=(50, 50)),
        }
    ),
    (
        "separate_on_period_and_highlighting",
        {
            "subtitle_type": 'separate_on_period',
            "fill_sub_times": False,
            "word_max": 11,
            "highlight_args": SubTextHighlight.highlight_args(
                highlight_word_max=0,
                primarycolor='00AAFF'
            ),
            "effect_args": None,
        }
    ),
    (
        "join_and_word_max",
        {
            "subtitle_type": 'join',
            "fill_sub_times": False,
            "word_max": 20,
            "highlight_args": None,
            "effect_args": None,
        }
    ),
    (
        "appear",
        {
            "subtitle_type": 'join',
            "fill_sub_times": False,
            "word_max": 20,
            "highlight_args": None,
            "effect_args": SubTextHighlight.effects_args(fade=(50, 50), appear=True),
        }
    ),
    (
        "rounded_borders",
        {
            "subtitle_type": 'join',
            "fill_sub_times": False,
            "word_max": 20,
            "highlight_args": None,
            "effect_args": SubTextHighlight.effects_args(
                fade=(50, 50),
                args_border=SubTextHighlight.args_border()
            ),
        }
    ),
    (
        "rounded_background_highlight",
        {
            "subtitle_type": 'separate_on_period',
            "fill_sub_times": False,
            "word_max": 11,
            "highlight_args": SubTextHighlight.highlight_args(
                highlight_word_max=0,
            ),
            "effect_args": SubTextHighlight.effects_args(
                fade=(50, 50),
                args_border=SubTextHighlight.args_border(use_borders_as_highlight=True, height_scaling=1.0)
            )
        }
    ),
    (
        "rounded_background_appear",
        {
            "subtitle_type": 'separate_on_period',
            "fill_sub_times": False,
            "word_max": 11,
            "highlight_args": None,
            "effect_args": SubTextHighlight.effects_args(
                fade=(50, 50),
                args_border=SubTextHighlight.args_border(),
                appear=True
            )
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

    sub_args = SubTextHighlight.sub_args(
        input=str(blank_srt_path),
        output=None,
        subtitle_type=options["subtitle_type"],
        fill_sub_times=options["fill_sub_times"],
        alignment=2,
        input_video=str(video_path),
    )

    if options['word_max'] is not None:
        sub_args.word_max = options['word_max']

    sub_edit = SubTextHighlight.Subtitle_Edit(sub_args, options['highlight_args'], options['effect_args'])
    sub_file: pysubs2.SSAFile = sub_edit()

    sub_file.save(str(output_ass))

    # Assert
    if UPDATE_GOLDEN:
        sub_file.save(str(expected_ass))
        assert True
    else:
        # Verify
        actual = sub_file.to_string('ass')
        expected = pysubs2.load(str(expected_ass)).to_string('ass')

        assert actual == expected
