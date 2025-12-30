import os
from .container import ContainerWrapper
from . import base
import traceback
from pysubs2 import SSAFile
import json


class DockerWrapper(base.BaseWrapper):

    def __init__(self, force_install:bool = False):
        # Check for the install
        super().__init__(force_install)
        self.docker_installed = False

        # Only continue if package is installed
        if self.installed:
            self.image_name = 'n01d3a/aegisub-cli:ShaperyRoundedBorders-2.3'
            self.rep_name = 'n01d3a/aegisub-cli'
            self.client = self.get_client()
            self.image = self.check_image_v2()

    def __call__(self,
                 input_ass:str | SSAFile, # path or SAAFile, not ass in string form
                 args_border:base.args_border, # settings for the args border
                 return_pysubsSSAFile:bool = True, # container_run_func needs to take client and name as a input
                 _traceback:bool = False,
                 verbose:bool = False,
                 cleanup:bool = False
                 ):

        if not self.installed and not self.docker_installed:
            raise ImportError('The Docker Package and Image needs to be installed for this section.')
        # Init variables
        container = None
        container_wrapper = None

        try:
            if args_border.container_run_func is not None:
                container = args_border.container_run_func(self.client, self.image_name)
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
            container_wrapper.copy_needed_files(input_ass, args_border.fonts_path)

            # Install packages (optional)
            if args_border.packages is not None:
                container_wrapper.install_packages(args_border.packages)

            # Execute the shapery command

            dialog_json = json.dumps(
                {"button": 0,
                 "values": args_border()
                 }
            )

            # aegisub-cli --dialog '{"button": 0, "values": {"offset": 20, "radius": 20, "transformY": -1, "heightscaling": 1.3, "borderColor": "&H000000&", "borderAlpha": "&H00"}}' --automation jz.RoundedBorders.lua input.ass output.ass "Create Rounded Border"
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


    def return_docker_image(self):
        images = self.client.images.list()
        found_image = False
        for image in [x for x in images]:
            tag = image.tags
            if 'n01d3a/aegisub-cli:Shapery' in tag:
                found_image = image
        return found_image

    def ask_install_docker_image(self):

        # Ask for confirmation to download the package
        print('For this Part of the script a specific docker image must be installed')
        answer = ''
        while answer not in ['y', 'n']:
            answer = input('y/n:').lower()

        # Review answer
        if answer == 'y':
            return True
        else:
            return False

    def check_image_v2(self):
        try:
            image = self.client.images.get(self.image_name)
            self.docker_installed = True
        except self.docker.errors.ImageNotFound:

            # ask to install the docker image
            if self.force_install:
                answer = True
            else:
                answer = self.ask_install_docker_image()

            # if yes install docker image and set variable
            if answer:
                self.pull_docker_image()
                image = self.client.images.get(self.image_name)
                self.docker_installed = True
            else:
                # if not, return None Image
                image = None
        return image

    def pull_docker_image(self):
        name, tag = self.image_name.split(':')
        print('Pulling Docker Image...')
        self.client.images.pull(name, tag=tag)
        print('Pulled Docker Image.')

    def cleanup(self):
        containers = self.client.containers.list(all=True)

        # check if image of container can be opened, else delete container
        new_containers = list()
        for container in containers:
            try:
                image = container.image
                new_containers.append(container)
            except self.docker.errors.ImageNotFound:
                container.remove(force=True)
        containers = new_containers

        # stop and remove containers
        for container in containers:
            if container.image == self.image:
                if container.status == 'running':
                    container.stop()
                # try stopping the container just in case
                try:
                    container.stop()
                except Exception:
                    pass
                container.remove()

    def cleanup_old_images(self):
        images = self.client.images.list(self.rep_name)

        # delete all images with different tags
        for image in images:
            tag = image.attrs['RepoTags'][0]
            if not tag == self.image_name:
                self.client.images.remove(tag, force=True)