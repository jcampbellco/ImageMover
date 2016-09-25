import glob
from appdirs import *
from Config import Config
from PIL import Image, ImageTk


class Filesystem:

    images = {}

    image_resources = {}

    current_filename = None

    def __init__(self, config: Config):
        self.config = config
        self.get_image_list()

    def get_new_image(self):
        self.current_filename = self.images.popitem()[1] if len(self.images) > 0 else None
        print("Fetching " + str(self.current_filename))
        return self.current_filename

    def get_image_list(self):
        i = 0

        for source in self.config[Config.SOURCES]:
            for extension in self.config[Config.EXTENSIONS]:
                print("Scanning " + self.config[Config.SOURCES][source] + '/*.' + extension)
                for file in glob.glob(self.config[Config.SOURCES][source] + '/*.' + extension):
                    self.images[i] = file
                    i += 1

                    if file not in self.image_resources:
                        self.image_resources[file] = None

        print("Found " + str(len(self.image_resources)) + " images in " + str(len(self.config[Config.SOURCES])) +
              " directories")

        return self.images

    def get_image(self, size):
        if self.images.__len__() <= 0:
            return

        original = Image.open(self.get_new_image())

        original.thumbnail(size, Image.ANTIALIAS)

        # @todo get rid of the dependency on ImageTk - filesystem shouldn't have knowledge of the interface
        return ImageTk.PhotoImage(original)

    def get_image_resource(self, path):
        """ Will fetch an image resource and save it to the resources dictionary """
        if path not in self.image_resources:
            raise KeyError("The requested path " + path + " is not present in the image dictionary")

        if self.image_resources[path] is None:
            self.image_resources[path] = Image.open(path)

        self.current_filename = path

        return self.image_resources[path]

    def get_next_image(self, path=None):
        if len(self.image_resources) <= 0:
            return "test"

        paths = list(self.image_resources.keys())

        if path is None or len(self.image_resources) is 1:
            return self.get_image_resource(paths[0])

        key_list = sorted(self.image_resources.keys())
        for i, v in enumerate(key_list):
            if v == path:
                # If the specified path is the last item, return the first
                if i + 1 == len(self.image_resources):
                    return self.get_image_resource(paths[0])

                return self.get_image_resource(paths[i + 1])

    @staticmethod
    def get_filename(path):
        return os.path.split(path)[-1]
