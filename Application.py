import atexit
from Config import Config
from Interface import Interface
from Filesystem import Filesystem


'''
    The entry point for the application

    Some todo items:
    @todo: Break up into separate objects
    @todo: Figure out how to make the config panel stick to the right side and the image panel to resize accordingly
        with window resizes
'''


class Application:

    def __init__(self, config: Config, filesystem: Filesystem, interface: Interface):
        self.config = config
        self.filesystem = filesystem
        self.interface = interface

        atexit.register(self.exit_handler)

    '''
        Write the config to disk before actually exiting
    '''
    def exit_handler(self):
        self.config.write()
