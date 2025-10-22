import os
import logging
import pysubs2
import json

class BaseWrapper:

    def __init__(self):
        # Check for the install
        self.installed, self.docker = self.check_docker_installation()

        # Ask if package is not installed
        if not self.installed:
            self.ask_install_docker_package()

        self.logger = logging.getLogger(__name__)

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
            os.system('pip install -r docker')

            # verify docker install
            self.installed, self.docker = self.check_docker_installation()
            if not self.installed:
                raise ImportError('Docker could not be imported')

        elif answer == 'n':
            pass


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

    def __init__(self,
        offset:int = 20,
        radius:int = 20,
        transformy:int = -1,
        color:pysubs2.Color | None = None,
        fonts_path: list | str | None = None,
        packages: list[str] | None = None,
        container_run_func : None=None # container_run_func needs to take client and name as a input
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

    def __call__(self):
        return {
            "offset": self.offset,
            "radius": self.radius,
            "transformY": self.transformy,
            "borderColor": self.bordercolor,
            "borderAlpha": self.borderalpha,
        }
