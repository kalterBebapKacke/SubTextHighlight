from . import base
from .. import config
import dataclasses
import logging
import tempfile
import tarfile
from io import BytesIO
from pathlib import Path
from contextlib import contextmanager
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
        container_obj = Container(docker_conf, _container)
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

@dataclasses.dataclass
class Container:

    _config:config.DockerConfig
    _container:None

    @classmethod
    def return_base_container(cls, _config:config.Config):
        return ContainerManager.return_container(_config.docker_config)

    @classmethod
    def __return_base_container(cls, _config:config.DockerConfig):
        return ContainerManager.return_container(_config)

    @contextmanager
    def archive_writer(self, dest_path='/home'):
        with tempfile.NamedTemporaryFile(suffix='.tar.gz', delete=True) as tmp:
            with tarfile.open(fileobj=tmp, mode='w:gz') as tar:
                yield tar
            tmp.flush()
            tmp.seek(0)
            self._container.put_archive(dest_path, tmp)

    def __post_init__(self):
        # Install packages
        if self._config.packages:
            self.install_packages(self._config.packages)

        # Install fonts
        if self._config.fonts_path:
            fonts = self._config.fonts_path if isinstance(self._config.fonts_path, list) else [self._config.fonts_path]
            fonts = [Path(x) for x in fonts]
            with self.archive_writer('/root/.local/share/fonts/') as tar:
                for font in fonts:
                    if font.suffix != '.tff':
                        logger.error('{} is not a Font file'.format(font))
                        continue
                    tar.add(str(font), arcname=font.name)

    @property
    def status(self):
        return self._container.status

    def set_pause(self):
        self._container.pause()

    def set_unpause(self):
        self._container.unpause()

    def start_if_not_running(self):
        self._container.reload()
        if self._container.status != 'running':
            self.set_unpause()

    def __call__(self, command: list | str, workdir:str='/home'):
        self.start_if_not_running()

        if isinstance(command, list):
            command = self.build_command(command)

        command = ['bash', '-c', command]
        exit_code, output = self._container.exec_run(command, workdir=workdir)
        if exit_code != 0:
            logger.error(f'Container run into the following error with exit code {exit_code}: \n{output.decode('utf-8')}')
        if output != '' and output != '\n':
            text = output.decode("utf-8").strip()
            if text:
                logger.debug(f'Docker Output:\n{text}')

    def get_output(self, path:str) -> str:
        bits, stat = self._container.get_archive(path)

        buffer = BytesIO()
        for chunk in bits:
            buffer.write(chunk)
        buffer.seek(0)

        with tarfile.open(fileobj=buffer, mode='r:*') as tar:
            member = tar.getmembers()[0]
            content = tar.extractfile(member).read()

        return content.decode('utf-8')

    @staticmethod
    def build_command(commands: list[str]):
        return ' && '.join(commands)

    def install_packages(self, packages:list[str]):
        command = ['apt-get update', f'apt-get install -y --no-install-recommends {' '.join(packages)}', 'rm -rf /var/lib/apt/lists/*']
        self(command)

    def __del__(self):
        container = getattr(self, '_container', None)
        if container is None:
            return
        try:
            container.remove(force=True)
        except Exception:
            pass

