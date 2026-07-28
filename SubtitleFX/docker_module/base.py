import dataclasses
from .. import utils
import subprocess
import logging
import questionary
logger = logging.getLogger(__name__)

@dataclasses.dataclass
class BaseWrapper:

    config:utils.DockerConfig

    _docker:None = dataclasses.field(init=False)
    _client:None = dataclasses.field(init=False, default=None)

    def __post_init__(self):
        # Check if docker is installed
        logger.debug('Starting the Docker Wrapper')
        if not self.is_installed:
            logger.debug('Docker package is not installed')
            if self.config.force_install:
                logger.debug('Installing Docker since force_install is True')
                self.install_docker()
            else:
                logger.debug('Asking User for confirmation to install')
                self.ask_installation()

    @property
    def client(self):
        if self._client:
            return self._client
        self._client = self.docker.from_env()
        return self._client

    @property
    def docker(self):
        if self._docker:
            return self._docker

        self.check_installation(True)
        return self._docker

    def check_installation(self, _raise:bool=False):
        try:
            import docker
            self._docker = docker
            return True
        except ImportError:
            if _raise:
                raise utils.DockerNotInstalled()
            return False

    @property
    def is_installed(self):
        return self.check_installation()

    @staticmethod
    def install_docker():
        try:
            subprocess.run(['pip', 'install', 'docker'], encoding='utf-8')
        except Exception as e:
            logger.error('Error while downloading the docker package: {}'.format(e))

    @staticmethod
    def ask_installation():
        confirmation = questionary.confirm('Do you want to install the docker package (the program needs it to execute properly)?').ask()
        if confirmation:
            logger.debug('User has agreed to install the docker package')
            BaseWrapper.install_docker()
        else:
            logger.debug('User has refused to install the docker package')