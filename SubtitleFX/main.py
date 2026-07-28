from .config import Config
from .pipeline import BuildPipeline, Pipeline
from .docker_module import Container
from . import utils
import dataclasses
import pysubs2
from .handling import Output

@dataclasses.dataclass
class SubtitleBuild:

    config:Config

    _pipeline_build:BuildPipeline = dataclasses.field(init=False)
    _pipeline: Pipeline = dataclasses.field(init=False)
    _sub_file:pysubs2.SSAFile = dataclasses.field(init=False, default=None)

    def __enter__(self):
        self._pipeline_build = BuildPipeline(self.config)
        self._pipeline = self._pipeline_build.build()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return

    def change(self, **kwargs):
        for key, value in kwargs.items():
            if key not in type(self.config).model_fields:
                raise AttributeError(f"Config has no field {key!r}")
            setattr(self.config, key, value)

        # the pipeline is built eagerly from a snapshot of the config values,
        # so it has to be rebuilt for a post-__enter__ change to take effect
        if hasattr(self, '_pipeline_build'):
            self._pipeline_build = BuildPipeline(self.config)
            self._pipeline = self._pipeline_build.build()

        return self

    def set_container(self, container:Container):
        return self.change(container=container)

    def run(self):
        self._sub_file = self._pipeline.run()
        return self

    def save(self):
        if not self._sub_file:
            raise utils.SubtitleFileNotExisting
        _obj = Output.Output(self.config.output, self.config.input_video)
        return _obj.handle_output(self._sub_file)
