from . import base
from .. import utils
from .container import Container
from typing import Optional
import logging
import pysubs2
import dataclasses
import json
import tempfile
logger = logging.getLogger(__name__)

@dataclasses.dataclass
class DockerWrapper(base.BaseWrapper):

    input_path = 'input.ass'
    output_path = 'output.ass'

    container:Optional[Container] = None

    def __call__(self, sub_file:pysubs2.SSAFile, border_config:utils.BorderConfig):
        if not self.container:
            container = Container.return_base_container(self.config)
        else:
            container = self.container

        if not isinstance(container, Container):
            raise utils.NotAContainer

        # cleanup of maybe old files
        logger.debug('Cleaning up old files')
        cleanup = [
            f'rm -rf {self.input_path}',
            f'rm -rf {self.output_path}',
        ]
        container(cleanup)

        # place the sub_file
        logger.debug('Placign the subfiles')
        with container.archive_writer() as tar:
            with tempfile.NamedTemporaryFile(suffix='.ass', delete=True) as ass:
                sub_file.save(ass.name)
                tar.add(ass.name, arcname=self.input_path)

        dialog_json = (
            json.dumps(
                {
                    "button": 0,
                    "values": border_config.json_info()
                }
            )
        )

        shapery_command = [
            'aegisub-cli',
            f"--dialog '{dialog_json}'",
            '--automation',
            'jz.RoundedBorders.lua',
            self.input_path,
            self.output_path,
            '"Create Rounded Border"',
            '|| true'
        ]

        logger.debug('Executing Shapery Command')
        container(' '.join(shapery_command))
        logger.debug('Executing Shapery Finished')

        output: str = container.get_output(f'/home/{self.output_path}')
        output: str = output[output.find('[Script Info]'):]

        output_subfile = pysubs2.SSAFile.from_string(output)

        logger.debug(f'Output from the Docker:\n{output_subfile.to_string('ass')}')

        container.set_pause()

        return output_subfile





