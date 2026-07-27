from . import base
from .. import utils
from .container import Container
from typing import Optional
import logging
import pysubs2
import dataclasses

logger = logging.getLogger(__name__)

@dataclasses.dataclass
class DockerWrapper(base.BaseWrapper):

    container: Optional[Container] = None

    def __call__(self, sub_file:pysubs2.SSAFile, border_config:utils.BorderConfig):
        if not self.container:
            self.container = Container.__return_base_container(self.config)

