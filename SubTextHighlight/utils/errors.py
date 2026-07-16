

class FormatterError(Exception):

    def __init__(self, formatter_name, formatters:list):
        self.formatter_name = formatter_name
        self.formatters = formatters
        super().__init__(f"Formatter {formatter_name} not found. Supported Formatters are {formatters}")