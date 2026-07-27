from . import base
from .. import config
import dataclasses
import logging
logger = logging.getLogger(__name__)

@dataclasses.dataclass
class ContainerManager(base.BaseWrapper):

    image_name = 'n01d3a/aegisub-cli:ShaperyRoundedBorders-2.3'
    repo_name = 'n01d3a/aegisub-cli'

    @staticmethod
    def return_container(docker_conf:config.DockerConfig):
        cm = ContainerManager(docker_conf)

        if not cm.is_image_installed:
            cm.pull_docker_image()
        _container = cm.client.containers.run(
            cm.image_name,
            command='tail -f /dev/null',
            detach=True,
            network_mode='host'  # network_mode='host' to prevent an docker error
        )
        container_obj = Container(_container)
        container_obj.set_pause()
        return container_obj

    @property
    def is_image_installed(self):
        try:
            image = self.client.images.get(self.image_name)
            if image:
                return True
            return False
        except self.docker.errors.ImageNotFound:
            logger.debug('Docker Image has not been found')
            return False

    def pull_docker_image(self):
        name, tag = self.image_name.split(':')
        print('Pulling Docker Image...')
        self.client.images.pull(name, tag=tag)
        print('Pulled Docker Image.')

class Container:

    _container:None

    _status = 'init'

    @classmethod
    def return_base_container(cls, _config:config.Config):
        return ContainerManager.return_container(_config.docker_config)

    @classmethod
    def __return_base_container(cls, _config:config.DockerConfig):
        return ContainerManager.return_container(_config)

    def set_pause(self):
        self._container.pause()
        self._status = 'pause'

    def __del__(self):
        pass

