def build_pipeline_check_conflicts(config):

    if config.highlight_as_borders and config.rounded_border:
        raise ValueError("highlight_as_borders and rounded_border cannot both be True.")

    if config.rounded_border or config.highlight_as_borders:
        if config.offset <= 0:
            raise ValueError("offset must be greater than 0 for borders.")
        if config.radius <= 0:
            raise ValueError("radius must be greater than 0 for borders.")
        if config.transformy <= 0:
            raise ValueError("transformy must be greater than 0 for borders.")
        if config.height_scaling <= 0:
            raise ValueError("height_scaling must be greater than 0 for borders.")

class PipelineConflictChecker:

    def __init__(self, config):
        self.config = config

    def check_conflicts(self, sub_file):
        if self.config.rounded_border or self.config.highlight_as_borders:
            if sub_file.resolution is None:
                raise RuntimeError('The subtitle file does not contain a Resolution. For the right scaling of the subtitles a input with a video resolution has to be set.')

        return sub_file
