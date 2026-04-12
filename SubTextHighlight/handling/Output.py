import pathlib
from dataclasses import dataclass
from .ffmpeg import *

import logging
logger = logging.getLogger(__name__)

@dataclass
class Output:
    output: str | None
    input_video: str | None = None

    def handle_output(self, sub_file:pysubs2.SSAFile):

        # 1. Handle Strings
        if isinstance(self.output, str):
            if self.output.endswith('ass'):
                sub_file.save(self.output)
                return None

            if self.input_video is not None and self.is_output_video_file(self.input_video):
                add_subtitles_with_ffmpeg(self.input_video, self.output, sub_file)
                return None

            raise TypeError('Output format has to be a either ".ass" or a video type')

        # 2. Return subfile
        if self.output is None:
            return sub_file

        raise TypeError('Invalid Output type')

    def is_output_video_file(self, file_path):
        # Define a set of common video extensions
        video_extensions = ('.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv', '.webm', '.m4v', '.m4p', '.ogv')
        extension = pathlib.Path(file_path).suffix.lower()

        return extension in video_extensions