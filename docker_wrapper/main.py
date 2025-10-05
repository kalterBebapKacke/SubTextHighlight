import os
from .container import ContainerWrapper
from . import base


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
                 *args,
                 **kwargs):
        if not self.installed:
            raise ImportError('Docker needs to be installed for this section')

        try:
            container = self.client.containers.create(self.image_name)
            container_wrapper = ContainerWrapper(container)
            print(container)
            # Pre exec

            # Install fonts
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
        finally:
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
                container.remove()
