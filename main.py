import tkinter as tk
import glob as glob
import shutil
from tkinter import filedialog
from tkinter import *
from appdirs import *
from configparser import ConfigParser
from PIL import Image, ImageTk


class Application:
    def __init__(self):
        self.root = Tk()

        self.config = ConfigParser()
        self.config.read(self.get_config_path())
        print("Read config from " + self.get_config_path())

        self.size = (800, 600)

        self.images = self.get_image_list()

        self.current_image = self.get_new_image()

        self.createWidgets()

        self.root.mainloop()

    '''
        Build out the interface
    '''
    def createWidgets(self):
        image = self.get_image()
        self.image_preview = tk.Label(self.root, image=image, height=self.size[0], width=self.size[1])
        self.image_preview.image = image
        self.image_preview.grid(row=0, column=0, rowspan=3)

        self.add_directory = tk.Button(self.root)
        self.add_directory["text"] = "Add Directory"
        self.add_directory["command"] = self.add_directory_handler
        self.add_directory.grid(row=0, column=1)

        self.remove_directory = tk.Button(self.root)
        self.remove_directory["text"] = "Remove Directory"
        self.remove_directory["command"] = self.remove_directory_handler
        self.remove_directory.grid(row=0, column=2)

        self.directory_list = tk.Listbox(self.root)
        self.populate_listbox(self.directory_list)
        self.directory_list.bind('<Double-Button-1>', self.move_image_handler)
        self.directory_list.grid(row=1, column=1, columnspan=2)

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
        destination = self.config['directories'][self.directory_list.get(ACTIVE)]

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
        if not directory or short_dir in self.config['directories']:
            return

        self.config['directories'][short_dir] = directory

        self.populate_listbox(self.directory_list)
        print("Adding " + directory + " to directory list")
        self.write_directory_list()

    '''
        Given a filepath, return the last item (the directory name, or filename perhaps)
    '''
    def get_filename(self, path):
        return os.path.split(path)[-1]

    '''
        Handler for removing a directory
    '''
    def remove_directory_handler(self):
        directory = self.config['directories'][self.directory_list.get(ACTIVE)]
        self.config['directories'].pop(self.directory_list.get(ACTIVE))
        print("Removing " + directory + " from the directory list")
        self.write_directory_list()
        self.populate_listbox(self.directory_list)

    '''
        Populate the listbox
    '''
    def populate_listbox(self, listbox):
        listbox.delete(0, END)
        for directory in self.config['directories']:
            listbox.insert(END, directory)

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
            print(defaults)
            self.config[key] = defaults

        values = {}
        for alias in self.config[key]:
            values[alias] = self.config[key][alias]

        return values

    '''
        Write the config to the config file
    '''
    def write_config(self):
        with open(self.get_config_path(), 'w') as configfile:
            self.config.write(configfile)
        print("Wrote config to " + self.get_config_path())

    '''
        Get the directory list from the config.ini
    '''
    def read_directory_list(self):
        return self.get_config_key_formatted('directories')

    '''
        Returns a list of source directories to look through
    '''
    def get_source_dir(self):
        sources = self.get_config_key_formatted('sources')

        if len(sources) <= 0:
            directory = ""
            while directory == "":
                directory = self.get_directory()
            sources = {directory}

        return sources

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
        return os.path.join(user_data_dir("ImageMover", "reddeth"), 'config.ini')

    '''
        Get the source directory
        @todo Store in the config.ini
    '''
    @staticmethod
    def get_source_path():
        return os.path.join('C:', 'Users', 'reddeth', 'Downloads')

    '''
        Returns a directory path
    '''
    @staticmethod
    def get_directory():
        directory = filedialog.askdirectory()

        if not directory:
            print("No directory selected")
            return None

        return directory


app = Application()
