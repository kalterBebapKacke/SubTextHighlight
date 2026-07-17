
class WhisperError(Exception):

    def __init__(self):
        super().__init__("Whisper has not been configured to transcribe the Input")

class FormatterError(Exception):

    def __init__(self, formatter_name, formatters:list):
        self.formatter_name = formatter_name
        self.formatters = formatters
        super().__init__(f"Formatter {formatter_name} not found. Supported Formatters are {formatters}")