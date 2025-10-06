from . import base
import tarfile
import tempfile

class ContainerWrapper(base.BaseWrapper):

    def __init__(self, container, verbose:bool=False):
        # Check for the install
        super().__init__()

        # Only continue if package is installed
        if self.installed:
            self.client = self.get_client()
            self.verbose = verbose
            self.container = container

    def __call__(self, command: list | str):
        # Check if container is running
        self.container_running()
        # Check if the command is in the right format
        if type(command) is not str:
            command = self.build_command(command)
        # add exec to command
        command = ['bash', '-c', command]
        print(command)
        exit_code, output = self.container.exec_run(command, workdir='/home')
        if exit_code != 0:
            raise RuntimeError(f'Container run into the following error with exit code {exit_code}: {output}')
        if self.verbose:
            print(output)

    def container_running(self):
        # loop for waiting container to start?
        self.container.reload()

        # Check if it's running
        print(self.container.status)
        if self.container.status != 'running':
            raise RuntimeError('Container is not running. It needs to be started first.')

    def build_command(self, commands: list[str]):
        return ' && '.join(commands)

    def install_fonts(self, fonts_path:list | str,):
        if type(fonts_path) is str:
            fonts_path = [fonts_path]

        # Build tar for attaching in the container
        # Tmp file
        with tempfile.NamedTemporaryFile(suffix='.tar.gz', delete=True) as tmp:
            # Create actual tar dir
            with tarfile.open(fileobj=tmp, mode='w:gz') as tar:
                for font in fonts_path:
                    if not font.endswith(".ttf"):
                        print(f'Font "{font}" is not a ttf file')
                    else:
                        tar.add(font, recursive=False)

            # Flush and seek back to the beginning
            tmp.flush()
            tmp.seek(0)

            self.container.put_archive('/home', tmp)

            print(tmp)
            print(tmp.name)

            command = [
                'mkdir -p /fonts',
                f'tar -xf archive.tar.gz -C /home/fonts',
                'mv /home/fonts/* /root/.local/share/fonts/',
                ''
            ]
            print(self.build_command(command))
            self(['ls'])



