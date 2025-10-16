from . import base
import tarfile
import tempfile
from io import BytesIO
import re
from pysubs2 import SSAFile

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
            raise RuntimeError(f'Container run into the following error with exit code {exit_code}: \n{output.decode('utf-8')}')
        if self.verbose:
            if output != '' and output != '\n':
                text = output.decode("utf-8").strip()
                if text:
                    self.logger.info("\n%s\n%s\n%s", '', text,)
                    print("\n" + "-" * 20)
                    print(text)
                    print("-" * 20 + "\n")

    def container_running(self):
        # loop for waiting container to start?
        self.container.reload()

        # Check if it's running
        if self.container.status != 'running':
            raise RuntimeError('Container is not running. It needs to be started first.')

    def build_command(self, commands: list[str]):
        return ' && '.join(commands)

    def copy_needed_files(self, input_ass:str | SSAFile, fonts_path:list | str = None):

        # Add if fonts should be copied
        if fonts_path is None:
            if_copy_fonts = False
        else:
            if_copy_fonts = True
            if type(fonts_path) is str:
                fonts_path = [fonts_path]

        # Adding input ass and fonts to tar
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

                # if input is an ssafile object
                if type(input_ass) == SSAFile:
                    with tempfile.NamedTemporaryFile(suffix='.ass', delete=True) as ass:
                        input_ass.save(ass.name)
                        tar.add(ass.name, arcname='input.ass')
                else:
                    tar.add(input_ass, arcname='input.ass')

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

            # Decode safely (ignore undecodable bytes)
            content = buffer.read().decode('utf-8', errors='ignore')

            # Remove BOMs and nulls
            content = content.lstrip('\ufeff\x00').rstrip('\x00')

            # Remove only *non-printable* control characters, except \n, \r, \t
            content = re.sub(r'[^\x20-\x7E\n\r\t]+', '', content)

            # Final clean string and return
            return content.strip()

        else:
            return bits








