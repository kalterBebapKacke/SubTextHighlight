import os
from .container import ContainerWrapper
from . import base
import traceback


class DockerWrapper(base.BaseWrapper):

    def __init__(self):
        # Check for the install
        super().__init__()

        # Only continue if package is installed
        if self.installed:
            self.image_name = 'n01d3a/aegisub-cli:Shapery'
            self.client = self.get_client()
            self.image = self.check_image_v2()

    def __call__(self,
                 fonts_path: list | str | None = None,
                 container_run_func = None,
                 _traceback:bool = False,
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

            container_wrapper = ContainerWrapper(container)
            print(container)
            # Pre exec

            # Install fonts if they exist
            if fonts_path is not None:
                container_wrapper.install_fonts(fonts_path=fonts_path)

                # Copy input ass
                # Install packages (optional)

            # Exec
                # Execute the shapery command
                # (Show Logs when error occurred)

            # Post exec
                # Get output from the aegisub-cli

        except Exception as e:
            print(e)
            if _traceback:
                traceback.print_exc()
        finally:
            # Stop and remove the container
            if container is not None:
                if container.status == 'running':
                    container.stop()
                container.remove()

            # top and remove all other containers from the image if needed
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
