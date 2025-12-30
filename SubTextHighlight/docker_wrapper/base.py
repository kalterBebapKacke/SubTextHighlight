import os
import logging
import pysubs2
import json

class BaseWrapper:

    def __init__(self,
                 force_install:bool = False):
        # Check for the install
        self.installed, self.docker = self.check_docker_installation()
        self.force_install = force_install
        self.logger = logging.getLogger("__main__")

        # Ask if package is not installed
        if force_install and not self.installed:
            self.install_docker_package()
        elif not self.installed:
            self.ask_install_docker_package()

    def check_docker_installation(self):
        try:
            import docker
            return True, docker
        except ImportError:
            return False, None

    def ask_install_docker_package(self):

        # Ask for confirmation to download the package
        print('For this Part of the script the Docker package must be installed')
        answer = ''
        while answer not in ['y', 'n']:
            answer = input('y/n:').lower()

        # Review answer
        if answer == 'y':
            self.install_docker_package()

        elif answer == 'n':
            pass

    def install_docker_package(self):
        os.system('pip install -r docker')

        # verify docker install
        self.installed, self.docker = self.check_docker_installation()
        if not self.installed:
            raise ImportError('Docker could not be imported')


    def get_client(self):
        client = self.docker.from_env()
        return client


def pysub2_color_to_hex(color:pysubs2.Color):
    """
    Convert pysub2.Color object to hex format with separate alpha.

    Args:
        color: pysub2.Color object with r, g, b, a properties

    Returns:
        Tuple of (hex_color, alpha) where:
        - hex_color is a string in format #RRGGBB
        - alpha is the alpha value as an integer (0-255)
    """
    # Access the color properties from the Color object
    red = color.r
    green = color.g
    blue = color.b
    alpha = color.a

    # Convert to hex format (RGB only)
    hex_color = f"#{red:02X}{green:02X}{blue:02X}"

    return hex_color, alpha

class args_border:

    # container_run_func needs to take client and name as a input
    def __init__(self,
        offset:int = 6,
        radius:int = 6,
        transformy:int = 1,
        height_scaling:float = 1.2,
        color:pysubs2.Color | None = None,
        use_borders_as_highlight:bool = False,
        fonts_path: list | str | None = None,
        packages: list[str] | None = None,
        container_run_func : None=None
                 ):
        self.offset:int = offset
        self.radius:int = radius
        self.transformy:int = transformy
        if color is not None:
            self.bordercolor, self.borderalpha = pysub2_color_to_hex(color)
        else:
            self.bordercolor = "#FFFFFF"
            self.borderalpha = 0
        self.packages:list[str] = packages
        self.fonts_path:list[str] = fonts_path
        self.container_run_func = container_run_func
        self.use_borders_as_highlight = use_borders_as_highlight
        self.height_scaling:float = height_scaling

    def __call__(self):
        return {
            "offset": self.offset,
            "radius": self.radius,
            "transformY": self.transformy,
            "heightscaling": self.height_scaling,
            "borderColor": self.bordercolor,
            "borderAlpha": self.borderalpha,
        }
