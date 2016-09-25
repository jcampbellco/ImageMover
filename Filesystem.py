import glob
from appdirs import *
from Config import Config
from PIL import Image, ImageTk


class Filesystem:

    images = {}

    current_filename = None

    def __init__(self, config: Config):
        self.config = config
        self.get_image_list()

    '''
        If there are images available in the self.images dictionary, get the first one and put it into current_image
    '''

    def get_new_image(self):
        self.current_filename = self.images.popitem()[1] if len(self.images) > 0 else None
        print("Fetching " + str(self.current_filename))
        return self.current_filename

    '''
        Returns a list of the files to be sorted
    '''

    def get_image_list(self):
        self.images = {}
        i = 0

        for source in self.config[Config.SOURCES]:
            for extension in self.config[Config.EXTENSIONS]:
                print("Scanning " + self.config[Config.SOURCES][source] + '/*.' + extension)
                for file in glob.glob(self.config[Config.SOURCES][source] + '/*.' + extension):
                    self.images[i] = file
                    i += 1

        print("Found " + str(len(self.images)) + " images in " + str(len(self.config[Config.SOURCES])) + " directories")

        return self.images

    '''
        Fetches an image resource to be used by the TK label
    '''

    def get_image(self, size):
        if self.images.__len__() <= 0:
            return

        original = Image.open(self.get_new_image())

        original.thumbnail(size, Image.ANTIALIAS)

        # @todo get rid of the dependency on ImageTk - filesystem shouldn't have knowledge of the interface
        return ImageTk.PhotoImage(original)

    '''
        Given a file path, return the last item (the directory name, or filename perhaps)
    '''

    @staticmethod
    def get_filename(path):
        return os.path.split(path)[-1]
