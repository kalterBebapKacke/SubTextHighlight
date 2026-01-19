from SubTextHighlight import docker_wrapper
import pysubs2
from pathlib import Path
import os

UPDATE_GOLDEN = os.environ.get("UPDATE_GOLDEN", "false").lower() == "true"

def test_docker():
    base_path = Path("")
    arial_path = base_path / "input" / "Arial-Rounded-MT-Bold-Bold.ttf"
    petemoss_path = base_path / "input" / "Petemoss-Regular.ttf"
    ass_path = base_path / "input" / "docker_sub_file.ass"
    expected_file = base_path / "expected" / "docker_sub_file.ass"

    dw = docker_wrapper.main.DockerWrapper()
    args_border = docker_wrapper.base.args_border(
        fonts_path=[str(arial_path), str(petemoss_path)],
    )

    input_ass = pysubs2.load(str(ass_path))
    output_file = dw(
        input_ass=input_ass,
        _traceback=True,
        cleanup=True,
        verbose=True,
        args_border=args_border,
    )
    if UPDATE_GOLDEN:
        output_file.save(str(expected_file))
        assert True
    else:
        expected_sub_file = pysubs2.load(str(expected_file))
        assert expected_sub_file.to_string('ass') == output_file.to_string('ass')


