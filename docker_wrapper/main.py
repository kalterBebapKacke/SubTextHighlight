import os
from .container import ContainerWrapper
from . import base
import traceback
from pysubs2 import SSAFile
import json


class DockerWrapper(base.BaseWrapper):

    def __init__(self):
        # Check for the install
        super().__init__()

        # Only continue if package is installed
        if self.installed:
            self.image_name = 'n01d3a/aegisub-cli:ShaperyRoundedBorders'
            self.client = self.get_client()
            self.image = self.check_image_v2()

    def __call__(self,
                 input_ass:str | SSAFile, # path or SAAFile, not ass in string form
                 fonts_path: list | str | None = None,
                 packages:list[str] | None = None,
                 return_pysubsSSAFile:bool = True,
                 container_run_func = None,
                 _traceback:bool = False,
                 verbose:bool = False,
                 cleanup:bool = False,
                 *args,
                 **kwargs):
        # container_run_func needs to take client and name as a input
        if not self.installed:
            raise ImportError('Docker needs to be installed for this section')
        # Init variables
        container = None
        container_wrapper = None

        try:
            if container_run_func is not None:
                container = container_run_func(self.client, self.image_name)
            else:
                container = self.client.containers.run(
                    self.image_name,
                    command='tail -f /dev/null',
                    detach=True,
                    network_mode='host' #network_mode='host' to prevent an docker error
                )

            container_wrapper = ContainerWrapper(container, verbose)

            # Pre exec

            # Install fonts if they exist and copy input ass
            container_wrapper.copy_needed_files(input_ass, fonts_path)

            # Install packages (optional)
            if packages is not None:
                container_wrapper.install_packages(packages)

            # Execute the shapery command
            # TODO: Set Settings for command
            # TODO: Write Resultion in ass file
            # TODO: Improve Install error
            # TODO: Add type checking for color
            # TODO: Verbose the install of a image
            # TODO: Ask to install docker image

            dialog_json = json.dumps(
                {"button": 0,
                 "values": {
                     "offset": 20,
                     "radius": 20,
                     "transformY": -1,
                     "borderColor": '&H000000&',
                     "borderAlpha": '&H00',
                 }}
            )

            # aegisub-cli --dialog '{"button": 0, "values": {"offset": 20, "radius": 20, "transformY": -1, "borderColor": "&H000000&", "borderAlpha": "&H00"}}' --automation jz.RoundedBorders.lua input.ass output.ass "Create Rounded Border"
            shapery_command_test = 'aegisub-cli --automation ILL.Shapery.moon --loglevel 4 input.ass output.ass ": Shapery macros :/Shape expand" || true'
            shapery_command = ['aegisub-cli', f"--dialog '{dialog_json}'",
                               '--automation', 'jz.RoundedBorders.lua',
                               'input.ass', 'output.ass',
                               '"Create Rounded Border"', '|| true'
                               ]
            container_wrapper(' '.join(shapery_command))

            # Get output from the aegisub-cli
            output : str = container_wrapper.retrieve_file('/home/output.ass', True)
            output : str = output[output.find('[Script Info]'):]

            # make output to sting if wanted and then return it
            if return_pysubsSSAFile:
                output = SSAFile.from_string(output)
            return output
        except Exception as e:
            if _traceback:
                traceback.print_exc()

            # return the output of the even if the program fails

            # convert to pysub2.SAAFile
            if type(input_ass) == str:
                output = SSAFile.load(input_ass)
            else:
                output = input_ass

            # Convert to string if necessary
            if not return_pysubsSSAFile:
                output = output.to_string()
            return output
        finally:
            # Stop and remove the container
            if container is not None:
                if container.status == 'running':
                    container.stop()
                container.remove()

            # stop and remove all other containers from the image if needed
            if cleanup:
                self.cleanup()

    def check_image(self):
        # Check for image installed by matching the tag
        found_image = self.return_docker_image()

        # pull image if not present and return the image
        if not found_image:
            self.pull_docker_image()
            return self.return_docker_image()
        else:
            return found_image

    def return_docker_image(self):
        images = self.client.images.list()
        found_image = False
        for image in [x for x in images]:
            tag = image.tags
            if 'n01d3a/aegisub-cli:Shapery' in tag:
                found_image = image
        return found_image

    def check_image_v2(self):
        try:
            image = self.client.images.get(self.image_name)
        except self.docker.errors.ImageNotFound:
            self.pull_docker_image()
            image = self.client.images.get(self.image_name)
        return image

    def pull_docker_image(self):
        name, tag = self.image_name.split(':')
        self.client.images.pull(name, tag=tag)

    def cleanup(self):
        containers = self.client.containers.list(all=True)
        for container in containers:
            if container.image == self.image:
                if container.status == 'running':
                    container.stop()
                container.remove()
