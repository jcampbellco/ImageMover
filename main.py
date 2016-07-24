import glob
import atexit
from appdirs import *
from PIL import Image, ImageTk
from Config import Config
from Interface import Interface


'''
    The entry point for the application

    Some todo items:
    @todo: Break up into separate objects
    @todo: Figure out how to make the config panel stick to the right side and the image panel to resize accordingly
        with window resizes
'''


class Application:

    config = None
    interface = None

    def __init__(self):
        self.config = Config()

        self.size = (800, 600)

        self.images = self.get_image_list()

        self.current_image = self.get_new_image()

        self.interface = Interface(self)

        self.interface.minsize(640, 480)

        atexit.register(self.exit_handler)

        self.interface.mainloop()

    '''
        Write the config to disk before actually exiting
    '''
    def exit_handler(self):
        self.config.write()

    '''
        If there are no sources configured, request one
    '''
    def get_initial_source(self):
        directory = self.interface.get_directory("Select Source")

        if not directory:
            sys.exit(0)

        self.config["sources"] = {self.get_filename(directory): directory}

    '''
        Attempts to set an image to the image label
    '''
    def set_image(self):
        image = self.get_image()
        self.interface.image_preview.image = image
        self.interface.image_preview.configure(image=image)

    '''
        If there are images available in the self.images dictionary, get the first one and put it into current_image
    '''
    def get_new_image(self):
        return self.images.popitem()[1] if len(self.images) > 0 else None

    '''
        Returns a list of the files to be sorted
    '''
    def get_image_list(self):
        file_list = {}
        i = 0

        for source in self.config[Config.SOURCES]:
            for extension in self.config[Config.EXTENSIONS]:
                print("Scanning " + self.config[Config.SOURCES][source] + '/*.' + extension)
                for file in glob.glob(self.config[Config.SOURCES][source] + '/*.' + extension):
                    file_list[i] = file
                    i += 1

        return file_list

    '''
        Fetches an image resource to be used by the TK label
    '''
    def get_image(self):
        if self.current_image is None:
            return

        original = Image.open(self.current_image)

        original.thumbnail(self.size, Image.ANTIALIAS)

        return ImageTk.PhotoImage(original)

    '''
        Given a file path, return the last item (the directory name, or filename perhaps)
    '''
    @staticmethod
    def get_filename(path):
        return os.path.split(path)[-1]


app = Application()
