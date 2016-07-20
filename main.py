import tkinter
import glob
import shutil
from tkinter import filedialog
from tkinter import ttk
from appdirs import *
from configparser import ConfigParser
from PIL import Image, ImageTk

'''
    The entry point for the application

    Some todo items:
    @todo: Break up into separate objects
    @todo: Figure out how to make the config panel stick to the right side and the image panel to resize accordingly with window resizes
'''
class Application:
    def __init__(self):
        self.root = tkinter.Tk()

        self.get_config()

        self.size = (800, 600)

        self.images = self.get_image_list()

        self.current_image = self.get_new_image()

        self.createWidgets()

        self.root.mainloop()

    '''
        Parse in the config and, by nature of calling the get_ methods, populate it with some default values

        I don't like the way this works, to be honest. It's modifying a variable outside of it's scope
        and basically creating the defaults by hiding it. It's creating a config, not just "getting" one. This needs
        to be cleaned up, but I'll leave it for now in the interest of time.
    '''
    def get_config(self):
        self.config = ConfigParser()
        self.config.read(self.get_config_path())
        print("Read config from " + self.get_config_path())

        self.get_file_extensions()
        self.get_source_dir()
        self.get_directory_list()

        if len(self.config['sources']) <= 0:
            self.get_initial_source()

        self.write_config()

    '''
        If there are no sources configured, request one
    '''
    def get_initial_source(self):
        directory = self.get_directory("Select Source")

        if not directory:
            sys.exit(0)

        self.config['sources'] = {self.get_filename(directory): directory}

    '''
        Build out the interface
    '''
    def createWidgets(self):

        self.image_frame = tkinter.Frame()
        self.image_frame.grid(row=0, column=0)

        self.control_frame = tkinter.Frame()
        self.control_frame.grid(row=0, column=1, padx=5, sticky="e")

        image = self.get_image()
        self.image_preview = tkinter.Label(self.image_frame, image=image, height=self.size[0], width=self.size[1])
        self.image_preview.image = image
        self.image_preview.grid(row=0, column=0, rowspan=3)

        # Add the thumbnail list here

        self.destination_label = tkinter.Label(self.control_frame)
        self.destination_label["text"] = "Destinations"
        self.destination_label.grid(row=0, column=0, columnspan=2)

        self.destination_list = tkinter.Listbox(self.control_frame)
        self.populate_listbox(self.destination_list, "destinations")
        self.destination_list.bind('<Double-Button-1>', self.move_image_handler)
        self.destination_list.grid(row=1, column=0, columnspan=2, sticky="ns")

        self.add_destination = tkinter.Button(self.control_frame)
        self.add_destination["text"] = "Add"
        self.add_destination["command"] = self.add_directory_handler
        self.add_destination.grid(row=2, column=0, sticky="ew")

        self.remove_destination = tkinter.Button(self.control_frame)
        self.remove_destination["text"] = "Remove"
        self.remove_destination["command"] = self.remove_directory_handler
        self.remove_destination.grid(row=2, column=1, sticky="ew")

        self.separator = ttk.Separator(self.control_frame)
        self.separator.grid(row=3, column=0, columnspan=2, sticky="ew", pady=5)

        self.source_label = tkinter.Label(self.control_frame)
        self.source_label["text"] = "Sources"
        self.source_label.grid(row=4, column=0, columnspan=2, sticky="ns")

        # @todo: Actually set up the source list to work properly with adding/removing
        self.source_list = tkinter.Listbox(self.control_frame)
        self.populate_listbox(self.source_list, "sources")
        self.source_list.bind('<Double-Button-1>', self.move_image_handler)
        self.source_list.grid(row=5, column=0, columnspan=2)

        self.add_source = tkinter.Button(self.control_frame)
        self.add_source["text"] = "Add"
        self.add_source["command"] = self.add_directory_handler
        self.add_source.grid(row=6, column=0, sticky="ew")

        self.remove_source = tkinter.Button(self.control_frame)
        self.remove_source["text"] = "Remove"
        self.remove_source["command"] = self.remove_directory_handler
        self.remove_source.grid(row=6, column=1, sticky="ew")

    '''
        Attempts to set an image to the image label
    '''
    def set_image(self):
        image = self.get_image()
        self.image_preview.image = image
        self.image_preview.configure(image=image)

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

        for source in self.config['sources']:
            for extension in self.config['extensions']:
                print("Scanning " + self.config['sources'][source] + '/*.' + extension)
                for file in glob.glob(self.config['sources'][source] + '/*.' + extension):
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
        Handler for moving an image
    '''
    def move_image_handler(self, event):
        # is this actually the best way to get the selected desintation directory?
        destination = self.config['destinations'][self.destination_list.get(tkinter.ACTIVE)]

        filename = self.get_filename(self.current_image)

        destination_full = os.path.join(destination, self.get_filename(self.current_image))

        shutil.move(self.current_image, destination_full)

        print("Moving " + filename + " from " + self.current_image + " to " + destination)

        self.current_image = self.get_new_image()
        self.set_image()

    '''
        Handler for adding a new directory
    '''
    def add_directory_handler(self):
        directory = self.get_directory()

        short_dir = self.get_filename(directory)

        # short circuit if there was not a directory selected
        if not directory or short_dir in self.config['destinations']:
            return

        self.config['destinations'][short_dir] = directory

        self.populate_listbox(self.destination_list)
        print("Adding " + directory + " to directory list")
        self.write_directory_list()

    '''
        Given a filepath, return the last item (the directory name, or filename perhaps)
    '''
    @staticmethod
    def get_filename(path):
        return os.path.split(path)[-1]

    '''
        Handler for removing a directory
    '''
    def remove_directory_handler(self):
        directory = self.config['destinations'][self.destination_list.get(tkinter.ACTIVE)]
        self.config['destinations'].pop(self.destination_list.get(tkinter.ACTIVE))
        print("Removing " + directory + " from the directory list")
        self.write_directory_list()
        self.populate_listbox(self.destination_list)

    '''
        Populate the listbox
    '''
    def populate_listbox(self, listbox, source):
        listbox.delete(0, tkinter.END)
        for directory in self.config[source]:
            listbox.insert(tkinter.END, directory)

    '''
        Write the current directory list to the config.ini file
    '''
    def write_directory_list(self):
        self.write_config()

    '''
        Parse out some data from the config object
    '''
    def get_config_key_formatted(self, key, defaults=None):
        if defaults is None:
            defaults = {}

        if key not in self.config:
            self.config[key] = defaults

        values = {}
        for alias in self.config[key]:
            values[alias] = self.config[key][alias]

        return values

    '''
        Write the config to the config file
    '''
    def write_config(self):
        if not os.path.exists(self.get_config_directory()):
            os.makedirs(self.get_config_directory())

        with open(self.get_config_path(), 'w') as configfile:
            self.config.write(configfile)

        print("Wrote config to " + self.get_config_path())

    '''
        Get the directory list from the config.ini
    '''
    def get_directory_list(self):
        return self.get_config_key_formatted('destinations')

    '''
        Returns a list of source destinations to look through
    '''
    def get_source_dir(self):
        return self.get_config_key_formatted('sources')

    '''
        Returns a list of file extensions to scan for
        Should be compatible with the PIL library - not sure what happens if it isn't
    '''
    def get_file_extensions(self):
        return self.get_config_key_formatted('extensions', self.get_default_file_extensions())

    '''
        Returns a list of "default" file extensions
    '''
    @staticmethod
    def get_default_file_extensions():
        return {
            'jpg': 'jpg',
            'gif': 'gif',
            'png': 'png'
        }

    '''
        Returns the full path to the config.ini file
    '''
    @staticmethod
    def get_config_path():
        return os.path.join(Application.get_config_directory(), 'config.ini')

    @staticmethod
    def get_config_directory():
        return user_data_dir("ImageMover")

    '''
        Returns a directory path
    '''
    @staticmethod
    def get_directory(message=None):
        if message is None:
            message = "Select Directory"

        directory = filedialog.askdirectory(title=message)

        if not directory:
            print("No directory selected")
            return None

        return directory


app = Application()
