import os


class DockerWrapper:

    def __init__(self):
        # Check for the install
        installed, self.docker = self.check_docker_installation()

        if not installed:
            self.ask_install_docker_package()

        self.client = self.get_client()

        #self.pull_docker_image()

        self.image = self.check_image()
        print(self.image)

    def __call__(self, *args, **kwargs):
        pass

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
            installed, self.docker = self.check_docker_installation()
            if not installed:
                raise ImportError('Docker could not be imported')

        elif answer == 'n':
            pass

    def get_client(self):
        client = self.docker.from_env()
        return client

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

    def pull_docker_image(self):
        self.client.images.pull('n01d3a/aegisub-cli', tag='Shapery')
