import SubtitleFX
from SubtitleFX import docker_module
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

    docker_config = SubtitleFX.DockerConfig(
        force_install=True,
        fonts_path=[arial_path, petemoss_path]
    )

    dw = docker_module.DockerWrapper(docker_config)


    input_ass = pysubs2.load(str(ass_path))
    output_file = dw(
        input_ass,
        SubtitleFX.BorderConfig()
    )
    if UPDATE_GOLDEN:
        output_file.save(str(expected_file))
        assert True
    else:
        expected_sub_file = pysubs2.load(str(expected_file))
        print(output_file.to_string('ass'))
        assert expected_sub_file.to_string('ass') == output_file.to_string('ass')

def test_docker_container():
    base_path = Path("")
    arial_path = base_path / "input" / "Arial-Rounded-MT-Bold-Bold.ttf"
    petemoss_path = base_path / "input" / "Petemoss-Regular.ttf"
    ass_path = base_path / "input" / "docker_sub_file.ass"
    expected_file = base_path / "expected" / "docker_sub_file.ass"

    docker_config = SubtitleFX.DockerConfig(
        force_install=True,
        fonts_path=[arial_path, petemoss_path]
    )

    container = SubtitleFX.docker_module.Container.return_base_container(docker_config)

    dw = docker_module.DockerWrapper(docker_config, container=container)


    input_ass = pysubs2.load(str(ass_path))
    output_file = dw(
        input_ass,
        SubtitleFX.BorderConfig()
    )
    if UPDATE_GOLDEN:
        output_file.save(str(expected_file))
        assert True
    else:
        expected_sub_file = pysubs2.load(str(expected_file))
        print(output_file.to_string('ass'))
        assert expected_sub_file.to_string('ass') == output_file.to_string('ass')

