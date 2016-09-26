import atexit
from Config import Config
from Interface import Interface
from Filesystem import Filesystem


class Application:
    """
    Entry point for the application
    """
    def __init__(self, config: Config, filesystem: Filesystem, interface: Interface):
        self.config = config
        self.filesystem = filesystem
        self.interface = interface

        atexit.register(self.exit_handler)

    def exit_handler(self):
        """ Write the config to disk before actually exiting """
        self.config.write()
