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

    def __call__(self):
        pass

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

            print(f"Temporary tar created at: {tmp.name}")



