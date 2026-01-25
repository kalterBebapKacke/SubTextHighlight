import pysubs2
import fleep
from . import utils
import pathlib
import os

class Input_Output_Handler:

    def __init__(self, args_sub_edit):
        self.whisper = self.handle_whisper_import()

        self.model = args_sub_edit.whisper_model
        self.device = args_sub_edit.whisper_device
        self.refine = args_sub_edit.whisper_refine

        self.data_input = args_sub_edit.input
        self.data_output = args_sub_edit.output
        self.video = args_sub_edit.input_video

        self.duration, self.resolution = self.handle_duration_resolution()

    def handle_input(self):
        sub_file = None

        # 1. Handle Whisper Objects
        if isinstance(self.data_input, self.whisper.result.WhisperResult):
            subs_str = self.data_input.to_srt_vtt(None, segment_level=False, word_level=True)
            sub_file = pysubs2.SSAFile.from_string(subs_str)

        # 2. Handle Dictionaries/Lists (Whisper JSON)
        if isinstance(self.data_input, (dict, list)):
            sub_file = pysubs2.load_from_whisper(self.data_input)

        # 3. Handle Strings (Paths or Raw Text)
        if isinstance(self.data_input, str):
            if not os.path.isfile(self.data_input):
                raise FileNotFoundError(f'{self.data_input} is not a file')

            if self.data_input.endswith(('.srt', '.ass')):
                sub_file = pysubs2.load(self.data_input)

            if self.is_media_file(self.data_input):
                subs_str = self.whisper_transcribe(self.data_input)
                sub_file = pysubs2.SSAFile.from_string(subs_str)

        # Handle video and resolution logic
        # for some parts of the effects the PlayResX and Y has to be set in the ass file
        if self.video is not None:
            sub_file = self.handle_subfile_resolution(sub_file)

        if sub_file is not None:
            return sub_file
        else:
            raise TypeError('Invalid input type')

    def handle_output(self, sub_file:pysubs2.SSAFile):

        # 1. Handle Strings
        if isinstance(self.data_output, str):
            if self.data_output.endswith('ass'):
                sub_file.save(self.data_output)
                return None

            if self.video is not None and self.is_output_video_file(self.video):
                utils.add_subtitles_with_ffmpeg(self.video, self.data_output, sub_file)
                return None

            raise TypeError('Output format has to be a either ".ass" or a video type')

        # 2. Return subfile
        if self.data_output is None:
            return sub_file

        raise TypeError('Invalid Output type')

    def handle_whisper_import(self):
        try:
            import stable_whisper
            return stable_whisper
        except ImportError as e:
            print('Import error:', e)
            return None

    def is_media_file(self, file_path):
        try:
            with open(file_path, "rb") as f:
                info = fleep.get(f.read(128))
                return any(t in info.type for t in ['audio', 'video'])
        except (FileNotFoundError, IsADirectoryError):
            return False

    def is_video_file(self, file_path):
        try:
            with open(file_path, "rb") as f:
                info = fleep.get(f.read(128))
                return any(t in info.type for t in ['video'])
        except (FileNotFoundError, IsADirectoryError):
            return False

    def is_output_video_file(self, file_path):
        # Define a set of common video extensions
        video_extensions = ('.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv', '.webm', '.m4v', '.m4p', '.ogv')
        extension = pathlib.Path(file_path).suffix.lower()

        return extension in video_extensions

    def whisper_transcribe(self, path):
        model = self.whisper.load_model(self.model, device=self.device)
        result = model.transcribe(audio=path, verbose=None)
        if self.refine:
            model.refine(path, result, word_level=False, only_voice_freq=True, precision=0.05)
        r = result.to_srt_vtt(None, segment_level=False, word_level=True)
        return r

    def handle_duration_resolution(self):
        # 1. Audio or Video from input
        if self.is_media_file(self.data_input):
            return utils.get_duration_resolution(self.data_input)

        # 2. Resolution and duration from extra input video
        if self.video is not None:
            if self.is_video_file(self.video):
                return utils.get_duration_resolution(self.video)

        return None, None

    def handle_subfile_resolution(self, subfile:pysubs2.SSAFile):
        info = subfile.info

        # check if resolution is set
        if utils.is_subfile_resolution_set(subfile):
            # check if resolution matches
            if self.resolution == (info['PlayResX'], info['PlayResY']):
                return subfile

        # if it is not or wrongly set, just add them to the file
        subfile.info['PlayResX'] = self.resolution[0]
        subfile.info['PlayResY'] = self.resolution[1]
        return subfile

    def build_full_sub_file(self, string_subs: str, script_info: str):
        segments = string_subs.split('[')
        segments[1] = script_info[1:]
        segments = '['.join(segments)
        return pysubs2.SSAFile.from_string(segments)