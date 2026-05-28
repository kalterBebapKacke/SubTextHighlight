import pysubs2
from .video import *
import os
import stable_whisper
from dataclasses import dataclass, field

import logging
logger = logging.getLogger(__name__)

@dataclass
class Input:
    input: str | dict[str, any] | list[dict[str, any]] | stable_whisper.result.WhisperResult
    input_video: str | None = None
    whisper_model: str = 'medium.en'
    whisper_device: str = 'cpu'
    whisper_refine: bool = False

    def __post_init__(self):
        self.whisper = self.handle_whisper_import()

    def handle_input(self):
        sub_file = None
        logger.debug(f"Handling input {self.input}")
        # 1. Handle Whisper Objects
        if isinstance(self.input, self.whisper.result.WhisperResult):
            subs_str = self.input.to_srt_vtt(None, segment_level=False, word_level=True)
            sub_file = pysubs2.SSAFile.from_string(subs_str)

        # 2. Handle Dictionaries/Lists (Whisper JSON)
        if isinstance(self.input, (dict, list)):
            sub_file = pysubs2.load_from_whisper(self.input)

        # 3. Handle Strings (Paths or Raw Text)
        if isinstance(self.input, str):
            if not os.path.isfile(self.input):
                raise FileNotFoundError(f'{self.input} is not a file')

            if self.input.endswith(('.srt', '.ass')):
                sub_file = pysubs2.load(self.input)

            if is_media_file(self.input):
                subs_str = self.whisper_transcribe(self.input)
                sub_file = pysubs2.SSAFile.from_string(subs_str)
                #self.duration, self.resolution = self.handle_duration_resolution()

        # Handle video and resolution logic
        # for some parts of the effects the PlayResX and Y has to be set in the ass file
        #if self.input_video is not None:
            #sub_file = self.handle_subfile_resolution(sub_file)

        logger.debug(f"Exporting input {self.input}")
        if sub_file is not None:
            return sub_file
        else:
            raise TypeError('Invalid input type')

    def handle_whisper_import(self):
        try:
            import stable_whisper
            return stable_whisper
        except ImportError as e:
            print('Import error:', e)
            return None

    def whisper_transcribe(self, path):
        model = self.whisper.load_model(self.whisper_model, device=self.whisper_device)
        result = model.transcribe(audio=path, verbose=None)
        if self.whisper_refine:
            model.refine(path, result, word_level=False, only_voice_freq=True, precision=0.05)
        r = result.to_srt_vtt(None, segment_level=False, word_level=True)
        return r


@dataclass
class DurationResolution:
    input: str | dict[str, any] | list[dict[str, any]] | stable_whisper.result.WhisperResult
    input_video: str | None = None

    def handle(self, sub_file):
        duration, resolution = self.handle_duration_resolution()

        # set duration
        sub_file.set_duration(duration)

        # set resolution
        sub_file = self.handle_subfile_resolution(sub_file, resolution)
        sub_file.set_resolution(resolution)

        return sub_file

    def handle_duration_resolution(self):
        # 1. Audio or Video from input
        if is_media_file(self.input):
            return self.get_duration_resolution(self.input)

        # 2. Resolution and duration from extra input video
        if self.input_video is not None:
            if is_video_file(self.input_video):
                return self.get_duration_resolution(self.input_video)

        return None, None

    def get_duration_resolution(self, file_path):
        cmd = [
            'ffprobe', '-v', 'error', '-print_format', 'json',
            '-show_format', '-show_streams', file_path
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            data = json.loads(result.stdout)
        except (subprocess.CalledProcessError, json.JSONDecodeError):
            return 0.0, None

        # 1. Handle Duration
        # Try getting duration from format first, fallback to 0.0
        duration_str = data.get('format', {}).get('duration', 0)
        duration = float(duration_str)

        # 2. Handle Resolution (Video Only)
        resolution = None
        streams = data.get('streams', [])
        for stream in streams:
            if stream.get('codec_type') == 'video':
                width = stream.get('width')
                height = stream.get('height')
                if width and height:
                    resolution = (width, height)
                break

        return duration, resolution

    def handle_subfile_resolution(self, subfile, resolution):
        info = subfile.sub_file.info

        # check if resolution is set
        if subfile.is_subfile_resolution_set():
            # check if resolution matches
            if subfile.resolution == (info['PlayResX'], info['PlayResY']):
                return subfile

        # if it is not or wrongly set, just add them to the file
        subfile.sub_file.info['PlayResX'] = resolution[0]
        subfile.sub_file.info['PlayResY'] = resolution[1]
        return subfile


