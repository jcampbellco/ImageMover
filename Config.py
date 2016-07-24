from configparser import ConfigParser
from appdirs import *


class Config(ConfigParser):
    SOURCES = 'sources'
    DESTINATIONS = 'destinations'
    EXTENSIONS = 'extensions'

    def __init__(self):
        ConfigParser.__init__(self)

        self['sources'] = {}
        self['destinations'] = {}
        self['extensions'] = {}

        self.read(self.get_config_path())

        print("Read config from " + self.get_config_path())

    '''
        Write the config file
    '''
    def write(self):
        if not os.path.exists(self.get_config_directory()):
            os.makedirs(self.get_config_directory())

        with open(self.get_config_path(), 'w') as configfile:
            super(Config, self).write(configfile)

        print("Wrote config to " + self.get_config_path())

    '''
        Returns the full path to the config.ini file
    '''
    @staticmethod
    def get_config_path():
        return os.path.join(Config.get_config_directory(), 'config.ini')

    @staticmethod
    def get_config_directory():
        return user_data_dir("ImageMover")
