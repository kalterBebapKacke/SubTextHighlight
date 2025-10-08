from . import base
import tarfile
import tempfile
from io import BytesIO

class ContainerWrapper(base.BaseWrapper):

    def __init__(self, container, verbose:bool=False):
        # Check for the install
        super().__init__()

        # Only continue if package is installed
        if self.installed:
            self.client = self.get_client()
            self.verbose = verbose
            self.container = container

    def __call__(self, command: list | str, workdir:str='/home'):
        # Check if container is running
        self.container_running()
        # Check if the command is in the right format
        if type(command) is not str:
            command = self.build_command(command)
        # add exec to command
        command = ['bash', '-c', command]
        exit_code, output = self.container.exec_run(command, workdir=workdir)
        if exit_code != 0:
            raise RuntimeError(f'Container run into the following error with exit code {exit_code}: {output}')
        if self.verbose:
            if output != '' or output != '\n':
                print('-------------------')
                print(output.decode("utf-8"))
                print('-------------------')

    def container_running(self):
        # loop for waiting container to start?
        self.container.reload()

        # Check if it's running
        if self.container.status != 'running':
            raise RuntimeError('Container is not running. It needs to be started first.')

    def build_command(self, commands: list[str]):
        return ' && '.join(commands)

    def copy_needed_files(self, input_ass_path:str, fonts_path:list | str = None):
        # Add if fonts should be copied
        if fonts_path is None:
            if_copy_fonts = False
        else:
            if_copy_fonts = True
            if type(fonts_path) is str:
                fonts_path = [fonts_path]

        with tempfile.NamedTemporaryFile(suffix='.tar.gz', delete=True) as tmp:

            with tarfile.open(fileobj=tmp, mode='w:gz') as tar:
                # Only add fonts if they are wanted
                if if_copy_fonts:
                    for font in fonts_path:
                        if not font.endswith(".ttf"):
                            print(f'Font "{font}" is not a ttf file')
                        else:
                            tar.add(font, arcname=f'fonts/{font.split("/")[-1]}')
                # Add input ass
                tar.add(input_ass_path, arcname='input.ass')

            # Flush and seek back to the beginning
            tmp.flush()
            tmp.seek(0)

            # import tar in docker
            self.container.put_archive('/home', tmp)
        # Put fonts in the right directory if they are needed
        if if_copy_fonts:
            command = [
                'mv /home/fonts/* /root/.local/share/fonts/',
                'rm -rf /home/fonts'
            ]
            self(command)

    def install_packages(self, packages:list[str]):
        command = ['apt-get update', f'apt-get install -y --no-install-recommends {' '.join(packages)}', 'rm -rf /var/lib/apt/lists/*']
        self(command)

    def retrieve_file(self, path:str, return_content:bool=False):
        bits, stat= self.container.get_archive(path)
        if return_content:
            buffer = BytesIO()
            for chunk in bits:
                buffer.write(chunk)
            buffer.seek(0)
            return buffer.read().decode('utf-8-sig').strip().lstrip('\x00\ufeff')
        else:
            return bits








