from .formatters import base, register
from .subtitles import event_factory, time_utils
from .handling import Input
from .subtitles import subtitles_file
from .effects import fade
import logging
logger = logging.getLogger(__name__)


class Pipeline:

    def __init__(self):
        self.steps = dict()

    def add_step(self,**kwargs):
        for key in kwargs:
            self.steps[key] = kwargs[key]

    def run(self):
        sub_file = None

        for i, key in enumerate(self.steps.keys()):
            try:
                step = self.steps[key]
                if i == 0:
                    sub_file = step()
                else:
                    sub_file = step(sub_file)

            except Exception as e:
                logger.error('Error in step {}: {}'.format(key, e))
                raise e
        return sub_file

class BuildPipeline:

    def __init__(self, config):
        self.config = config
        self.pipeline = Pipeline()

    def build(self) -> Pipeline:
        # add input to steps
        self._input()
        self.pipeline.add_step(Convert=subtitles_file.convert)

        # add Duration resolver step to the pipeline
        self._duration_resolution()

        # Add formatter step to the pipeline
        self.formatter()

        # effects
        self.pipeline.add_step(Fade=fade.Fade(self.config.fade[0], self.config.fade[1]).render)

        # Output
        self.pipeline.add_step(Render=subtitles_file.render)

        return self.pipeline

    def formatter(self):
        formatter_type = self.config.subtitle_type
        if not formatter_type in register.FormatterRegister.keys():
            raise KeyError(f"Unknown formatter type: {formatter_type}")

        # TODO: Add hightlighter
        _event_factory = event_factory.EventFactory()
        _time_resolver = time_utils.TimeResolver(self.config.fill_sub_times)

        formatter_class = register.FormatterRegister[formatter_type](_event_factory, _time_resolver, self.config.word_max)

        self.pipeline.add_step(Formatter=formatter_class.format)

    def _input(self):
        # add input to steps
        input = Input.Input(
            input=self.config.input,
            input_video=self.config.input_video,
            whisper_model=self.config.whisper_model,
            whisper_device=self.config.whisper_device,
            whisper_refine=self.config.whisper_refine
        )
        self.pipeline.add_step(Input=input.handle_input)

    def _duration_resolution(self):
        _DurationResolution = Input.DurationResolution(
            self.config.input,
            self.config.input_video,
        )
        self.pipeline.add_step(DurationResolution=_DurationResolution.handle)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return