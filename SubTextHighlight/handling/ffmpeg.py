import os
import tempfile
import pysubs2
import subprocess

import logging
logger = logging.getLogger(__name__)

def add_subtitles_with_ffmpeg(video_path, output_path, sub_file:pysubs2.SSAFile):
    with tempfile.NamedTemporaryFile(mode='w', suffix='.ass', delete=False) as temp_file:
        temp_file.write(sub_file.to_string(format_='ass'))
        temp_filename = temp_file.name
    add_subtitles_with_ffmpeg_with_given_ass(video_path, output_path, temp_filename)
    os.unlink(temp_filename)

def add_subtitles_with_ffmpeg_with_given_ass(video_path, output_path, ass_file):
    command = [
        "ffmpeg",
        "-y",
        "-i", video_path,
        "-vf",
        f"ass={ass_file}",
        "-c:a", "copy",
        "-loglevel", "error",
        output_path
    ]
    exec_command(command)

def exec_command(command:list):
    try:
        result = subprocess.run(command, text=True, stdout=subprocess.PIPE)
        if result.returncode != 0:
            logger.debug(f"Command {command} failed with return code {result.returncode}")
            raise RuntimeError(result.stdout)
    except Exception as e:
        logger.debug(f"Command {command} failed with exception {e}")
        pass