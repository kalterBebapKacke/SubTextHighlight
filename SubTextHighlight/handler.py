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

    def handle_subfile_resolution(self, subfile):
        #Convert to string and find the right section
        string_subtitles = subfile.to_string('ass')
        script_info = string_subtitles[string_subtitles.find('[Script Info]'):string_subtitles.find('[V4+ Styles]')]


        # check if playres is set
        if script_info.__contains__('PlayResX:') and script_info.__contains__('PlayResY:'):
            # if playres is set, confirm it is the right one
            playresx = script_info[script_info.find('PlayResX:') + len('PlayResX:'):]
            playresx = int(playresx[:playresx.find('\n')])
            playresy = script_info[script_info.find('PlayResY:') + len('PlayResY:'):]
            playresy = int(playresy[:playresy.find('\n')])
            if (playresx, playresy) == self.resolution:
                return subfile

        # if it is not or wrongly set, just add them to the file
        script_info = self.update_playres(script_info, self.resolution[0], self.resolution[1])
        return self.build_full_sub_file(string_subtitles, script_info)

    def build_full_sub_file(self, string_subs: str, script_info: str):
        segments = string_subs.split('[')
        segments[1] = script_info[1:]
        segments = '['.join(segments)
        return pysubs2.SSAFile.from_string(segments)

    def update_playres(self, ass_content, playres_x, playres_y):
        """
        Update or add PlayResX and PlayResY values in ASS subtitle file content.

        Args:
            ass_content (str): The content of the ASS file as a string
            playres_x (int): The new PlayResX value
            playres_y (int): The new PlayResY value

        Returns:
            str: Updated ASS file content
        """
        lines = ass_content.split('\n')
        playres_x_found = False
        playres_y_found = False
        script_info_idx = -1

        # Find [Script Info] section and existing PlayRes values
        for i, line in enumerate(lines):
            stripped = line.strip()

            if stripped == '[Script Info]':
                script_info_idx = i
            elif stripped.startswith('PlayResX:'):
                lines[i] = f'PlayResX: {playres_x}'
                playres_x_found = True
            elif stripped.startswith('PlayResY:'):
                lines[i] = f'PlayResY: {playres_y}'
                playres_y_found = True
            elif stripped.startswith('[') and script_info_idx != -1 and i > script_info_idx:
                # We've reached the next section
                break

        # If PlayRes values weren't found, add them after [Script Info]
        if script_info_idx != -1:
            insert_idx = script_info_idx + 1

            if not playres_y_found:
                lines.insert(insert_idx, f'PlayResY: {playres_y}')
            if not playres_x_found:
                lines.insert(insert_idx, f'PlayResX: {playres_x}')

        return '\n'.join(lines)