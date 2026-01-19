import pysubs2
import fleep

class Input_Output_Handler:

    def __init__(self, args_sub_edit):
        self.whisper = self.handle_whisper_import()

        self.model = args_sub_edit.whisper_model
        self.device = args_sub_edit.whisper_device
        self.refine = args_sub_edit.whisper_refine

        self.data_input = args_sub_edit.input
        self.data_output = args_sub_edit.output
        self.video = args_sub_edit.input_video

        #TODO:Handle colors

    def __call__(self, type:str):
        if type == 'input':
            return self.handle_input()
            #TODO:Handle PlayRes
        elif type == 'output':
            return self.handle_output()

    def handle_input(self):
        # 1. Handle Whisper Objects
        if isinstance(self.data_input, self.whisper.result.WhisperResult):
            subs_str = self.data_input.to_srt_vtt(None, segment_level=False, word_level=True)
            return pysubs2.SSAFile.from_string(subs_str)

        # 2. Handle Dictionaries/Lists (Whisper JSON)
        if isinstance(self.data_input, (dict, list)):
            return pysubs2.load_from_whisper(self.data_input)

        # 3. Handle Strings (Paths or Raw Text)
        if isinstance(self.data_input, str):
            if self.data_input.endswith(('.srt', '.ass')):
                return pysubs2.load(self.data_input)

            if self._is_media_file(self.data_input):
                subs_str = self.whisper_transcribe(self.data_input)
                return pysubs2.SSAFile.from_string(subs_str)
        raise TypeError('Invalid input type')

    def handle_output(self):
        #TODO: Output logic
        #TODO: fix ffmpeg usage
        raise TypeError('Invalid Output type')

    def handle_whisper_import(self):
        try:
            import stable_whisper
            return stable_whisper
        except ImportError as e:
            print('Import error:', e)
            return None

    def _is_media_file(self, file_path):
        try:
            with open(file_path, "rb") as f:
                info = fleep.get(f.read(128))
                return any(t in info.type for t in ['audio', 'video'])
        except (FileNotFoundError, IsADirectoryError):
            return False

    def whisper_transcribe(self, path):
        model = self.whisper.load_model(self.model, device=self.device)
        result = model.transcribe(audio=path, verbose=None)
        if self.refine:
            model.refine(path, result, word_level=False, only_voice_freq=True, precision=0.05)
        r = result.to_srt_vtt(None, segment_level=False, word_level=True)
        return r



