import glob
import logging
from appdirs import *
from Config import Config
from File import File


class Filesystem:

    image_resources = {}

    current_filename = None

    def __init__(self, config: Config):
        self.config = config
        self.get_image_list()

    def get_image_list(self):
        i = 0

        for source in self.config[Config.SOURCES]:
            for extension in self.config[Config.EXTENSIONS]:
                logging.info("Scanning " + self.config[Config.SOURCES][source] + '/*.' + extension)
                for file in glob.glob(self.config[Config.SOURCES][source] + '/*.' + extension):
                    i += 1

                    if file not in self.image_resources:
                        self.image_resources[file] = File(file)

        logging.info("Found " + str(len(self.image_resources)) + " images in " + str(len(self.config[Config.SOURCES])) +
                     " directories")

        return self.image_resources

    def remove_image_resource(self, path):
        if path in self.image_resources:
            del self.image_resources[path]

    def get_image_resource(self, path):
        """ Will fetch an image resource and save it to the resources dictionary """
        if path not in self.image_resources:
            raise KeyError("The requested path " + path + " is not present in the image dictionary")

        self.current_filename = path

        return self.image_resources[path]

    def get_next_image(self, path=None):
        """
        Gets the next image based on the provided path
        i.e.: Given a dictionary of images A, B, and C, if B is given as path, C will be returned
        :param path:
        :rtype: File
        """
        if len(self.image_resources) <= 0:
            return

        paths = list(self.image_resources.keys())

        offset = 0

        if path is not None:
            key_list = sorted(self.image_resources.keys())
            for i, v in enumerate(key_list):
                if v == path and ((i + 1) != len(self.image_resources)):
                    offset = i + 1

        return self.get_image_resource(paths[offset])

    @staticmethod
    def get_filename(path):
        return os.path.split(path)[-1]
