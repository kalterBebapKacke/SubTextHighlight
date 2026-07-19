from .subtitles import event_factory, time_utils
from .handling import Input
from .subtitles import subtitles_file, Highlight
from .effects import fade, appear, border, docker_wrapper
from . import formatters
import traceback
import logging
logger = logging.getLogger(__name__)
from . import config, utils


class Pipeline:

    def __init__(self):
        self.steps = dict()

    def add_step(self,**kwargs):
        for key in kwargs:
            self.steps[key] = kwargs[key]

    def run(self):
        sub_file = None
        max_iterations = len(self.steps)

        for i, key in enumerate(self.steps.keys()):
            logger.debug(f'\n============================================================================')
            logger.info('Step {}/{} starting: {} '.format(i+1,max_iterations,key))
            try:
                step = self.steps[key]
                if i == 0:
                    sub_file = step()
                else:
                    sub_file = step(sub_file)

            except Exception as e:
                logger.error('Error in step {}: {} \n {}'.format(key, e, traceback.format_exc()))
                raise e
            finally:
                logger.info('Step {} finished'.format(key))
                logger.debug('Sub File after Step: \n{}'.format(str(sub_file)))
        return sub_file

class BuildPipeline:

    def __init__(self, _config):
        self.config:config.Config = _config
        self.pipeline = Pipeline()
        self.steps = {
            "Input": self._input,
            "Convert": self._convert,
            "DurationResolution": self._duration_resolution,
            "Styles": self._styles,
            "Formatter": self.formatter,
            "Fade": self._fade,
            "Appear": self._appear,
            "Border": self._border,
            "Render": self._render
        }

    @property
    def highlighter_needed(self):
        return  self.config.highlight_as_borders or self.config.highlight_word_max is not None or self.config.highlight_style is not None

    def build(self) -> Pipeline:
        logger.debug('Building pipeline')
        for step in self.steps:
            logger.debug('Step {}'.format(step))
            self.steps[step]()

        logger.debug('Finished building pipeline')
        return self.pipeline

    def formatter(self):
        formatter = self.config.subtitle_type

        _event_factory = event_factory.EventFactory(self._highlighter_logic())
        _time_resolver = time_utils.TimeResolver(self.config.fill_sub_times)

        formatter_class = formatters.FORMATTER_REGISTER.get(formatter)
        formatter_instance = formatter_class(_event_factory, _time_resolver, self.config.char_max)

        self.pipeline.add_step(Formatter=formatter_instance.format)


    def _input(self):
        # add input to steps
        input = Input.Input(
            input=self.config.input,
            input_video=self.config.input_video,
            WhisperConfig=self.config.whisper_config
        )
        self.pipeline.add_step(Input=input.handle_input)

    def _convert(self):
        self.pipeline.add_step(Convert=subtitles_file.convert)

    def _duration_resolution(self):
        _DurationResolution = Input.DurationResolution(
            self.config.input,
            self.config.input_video,
            self.config.resolution,
        )
        self.pipeline.add_step(DurationResolution=_DurationResolution.handle)

    def _styles(self):
        self.pipeline.add_step(Styles=
                               utils.StyleSetup(
                                   self.config.subtitle_style,
                                   self.config.highlight_style,
                                   self.config.alignment,
                                   self.highlighter_needed
                               ).render
        )

    def _highlighter_logic(self):

        if self.config.highlight_word_max is None:
            highlight_word_max = 0
        else:
            highlight_word_max = self.config.highlight_word_max

        logger.debug("Build Step: Highlighter needed = {}".format(self.highlighter_needed))

        if not self.highlighter_needed:
            if self.config.appear:
                return Highlight.Highlighter(highlight_word_max)
            return None
        return Highlight.Highlighter(highlight_word_max)

    def _appear(self):
        if self.config.appear:
            self.pipeline.add_step(Appear=appear.Appear().render)

    def _border(self):
        if self.config.rounded_border or self.config.highlight_as_borders:

            self.pipeline.add_step(Border=border.Border(
                border_as_highlight=self.config.highlight_as_borders,
                force_install=self.config.docker_config.force_install,
                args_border=self._args_border(),
                traceback=self.config.docker_config.traceback,
                verbose=self.config.docker_config.verbose,
            ).render)

    def _fade(self):
        self.pipeline.add_step(Fade=fade.Fade(self.config.fade[0], self.config.fade[1]).render)

    def _args_border(self):
        return docker_wrapper.base.args_border(
                offset=self.config.border_config.offset,
                radius=self.config.border_config.radius,
                transformy=self.config.border_config.transformy,
                height_scaling=self.config.border_config.height_scaling,
                color=self.config.border_config.color.to_pysubs2(),
                use_borders_as_highlight=self.config.highlight_as_borders,
                fonts_path=self.config.docker_config.fonts_path,
                packages=self.config.docker_config.packages,
                container_run_func=self.config.docker_config.container_run_func,
                force_install=self.config.docker_config.force_install,
            )

    def _render(self):
        self.pipeline.add_step(Render=subtitles_file.render)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return