from . import base
import tarfile
import tempfile

class ContainerWrapper(base.BaseWrapper):

    def __init__(self, container):
        # Check for the install
        super().__init__()

        # Only continue if package is installed
        if self.installed:
            self.client = self.get_client()
            self.container = container

    def __call__(self, command: list | str):
        self.container_running()
        exit_code, output = self.container.exec_run(command, workdir='/home')
        print(output)
        print(exit_code)

    def container_running(self):
        # loop for waiting container to start?
        self.container.reload()

        # Check if it's running
        print(self.container.status)
        if self.container.status != 'running':
            raise RuntimeError('Container is not running. It needs to be started first.')

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
                        tar.add(font)

            # Flush and seek back to the beginning
            tmp.flush()
            tmp.seek(0)

            self.container.put_archive('/home', tmp)
            self(['ls -a'])



