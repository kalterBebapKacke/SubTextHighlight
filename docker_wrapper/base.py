import os

class BaseWrapper:

    def __init__(self):
        # Check for the install
        self.installed, self.docker = self.check_docker_installation()

        # Ask if package is not installed
        if not self.installed:
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