import tkinter
import glob
import shutil
import atexit
from tkinter import filedialog
from tkinter import ttk
from appdirs import *
from PIL import Image, ImageTk
from Config import Config


'''
    The entry point for the application

    Some todo items:
    @todo: Break up into separate objects
    @todo: Figure out how to make the config panel stick to the right side and the image panel to resize accordingly
        with window resizes
'''


class Application:

    config = None

    def __init__(self):
        self.config = Config()

        self.root = tkinter.Tk()

        self.size = (800, 600)

        self.images = self.get_image_list()

        self.current_image = self.get_new_image()

        self.create_widgets()

        self.root.minsize(640, 480)

        atexit.register(self.exit_handler)

        self.root.mainloop()

    '''
        Write the config to disk before actually exiting
    '''
    def exit_handler(self):
        self.config.write()

    '''
        If there are no sources configured, request one
    '''
    def get_initial_source(self):
        directory = self.get_directory("Select Source")

        if not directory:
            sys.exit(0)

        self.config["sources"] = {self.get_filename(directory): directory}

    '''
        Build out the interface
    '''
    def create_widgets(self):

        self.image_frame = tkinter.Frame(self.root)
        self.image_frame.pack(side="left", fill="both", expand=True, padx=5)

        self.control_frame = tkinter.Frame(self.root)
        self.control_frame.pack(side="right", fill="both", expand=False, padx=5)

        self.destinations_frame = tkinter.Frame(self.control_frame)
        self.destinations_frame.pack(fill="y", expand=1)

        self.separator = ttk.Separator(self.control_frame)
        self.separator.pack(fill="x", expand=0, pady=5)

        self.sources_frame = tkinter.Frame(self.control_frame)
        self.sources_frame.pack(fill="y", expand=1)

        image = self.get_image()
        self.image_preview = tkinter.Label(self.image_frame, image=image, height=self.size[0], width=self.size[1])
        self.image_preview.image = image
        self.image_preview.grid(row=0, column=0, rowspan=3, padx=5, pady=5)

        # Add the thumbnail list here

        self.destination_label = tkinter.Label(self.destinations_frame)
        self.destination_label["text"] = "Destinations"
        self.destination_label.grid(row=0, column=0, columnspan=2)

        self.destination_list = tkinter.Listbox(self.destinations_frame)
        self.populate_listbox(self.destination_list, "destinations")
        self.destination_list.bind('<Double-Button-1>', self.move_image_handler)
        self.destination_list.grid(row=1, column=0, columnspan=2, sticky="ns")

        self.add_destination = tkinter.Button(self.destinations_frame)
        self.add_destination["text"] = "Add"
        self.add_destination["command"] = self.add_destination_handler
        self.add_destination.grid(row=2, column=0, sticky="ew")

        self.remove_destination = tkinter.Button(self.destinations_frame)
        self.remove_destination["text"] = "Remove"
        self.remove_destination["command"] = self.remove_destination_handler
        self.remove_destination.grid(row=2, column=1, sticky="ew", pady=5)

        self.source_label = tkinter.Label(self.sources_frame)
        self.source_label["text"] = "Sources"
        self.source_label.grid(row=0, column=0, columnspan=2, sticky="ns", pady=5)

        # @todo: Actually set up the source list to work properly with adding/removing
        self.source_list = tkinter.Listbox(self.sources_frame)
        self.populate_listbox(self.source_list, "sources")
        self.source_list.bind('<Double-Button-1>', self.move_image_handler)
        self.source_list.grid(row=1, column=0, columnspan=2, sticky="ns")

        self.add_source = tkinter.Button(self.sources_frame)
        self.add_source["text"] = "Add"
        self.add_source["command"] = self.add_source_handler
        self.add_source.grid(row=2, column=0, sticky="ew", pady=5)

        self.remove_source = tkinter.Button(self.sources_frame)
        self.remove_source["text"] = "Remove"
        self.remove_source["command"] = self.remove_source_handler
        self.remove_source.grid(row=2, column=1, sticky="ew", pady=5)

        self.sources_frame.rowconfigure(1, weight=1)
        self.destinations_frame.rowconfigure(1, weight=1)

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
        Handler for moving an image
    '''
    def move_image_handler(self, event):
        # is this actually the best way to get the selected destination directory?
        destination = self.config[Config.DESTINATIONS][self.destination_list.get(tkinter.ACTIVE)]

        filename = self.get_filename(self.current_image)

        destination_full = os.path.join(destination, self.get_filename(self.current_image))

        shutil.move(self.current_image, destination_full)

        print("Moving " + filename + " from " + self.current_image + " to " + destination)

        self.current_image = self.get_new_image()
        self.set_image()

    def add_source_handler(self):
        self.add_directory(self.source_list, Config.SOURCES)

    def add_destination_handler(self):
        self.add_directory(self.destination_list, Config.DESTINATIONS)

    '''
        Handler for adding a new directory
    '''
    def add_directory(self, listbox, config_source):
        directory = self.get_directory()

        short_dir = self.get_filename(directory)

        # short circuit if there was not a directory selected
        if not directory or short_dir in self.config[config_source]:
            return

        self.config[config_source][short_dir] = directory

        self.populate_listbox(listbox, config_source)
        print("Adding " + directory + " to " + config_source + " list")

    '''
        Given a file path, return the last item (the directory name, or filename perhaps)
    '''
    @staticmethod
    def get_filename(path):
        return os.path.split(path)[-1]

    def remove_source_handler(self):
        directory = self.config[Config.SOURCES][self.source_list.get(tkinter.ACTIVE)]
        self.remove_directory(Config.SOURCES, directory, self.source_list)

    def remove_destination_handler(self):
        directory = self.config[Config.DESTINATIONS][self.destination_list.get(tkinter.ACTIVE)]
        self.remove_directory(Config.DESTINATIONS, directory, self.destination_list)

    '''
        Handler for removing a directory
    '''
    def remove_directory(self, config_source, directory, listbox):
        # This feels a bit dirty, but I'm not sure how to handle the directory coming in as the full path, but needing
        # the key to access it... @todo Get the key from the listbox, not the item?
        if directory not in self.config[config_source]:
            for alias in self.config[config_source]:
                if directory == self.config[config_source][alias]:
                    directory = alias
                    break

        removed = self.config[config_source].pop(directory, 0)

        if removed != 0:
            print("Removing " + directory + " from the " + config_source + " list")
            self.populate_listbox(listbox, config_source)
        else:
            print("Unable to find directory " + directory + " to remove")

    '''
        Populate the listbox
    '''
    def populate_listbox(self, listbox, source):
        listbox.delete(0, tkinter.END)
        for directory in self.config[source]:
            listbox.insert(tkinter.END, directory)

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
        Get the directory list from the config.ini
    '''
    def get_directory_list(self):
        return self.get_config_key_formatted(Config.DESTINATIONS)

    '''
        Returns a list of source destinations to look through
    '''
    def get_source_dir(self):
        return self.get_config_key_formatted(Config.SOURCES)

    '''
        Returns a list of file extensions to scan for
        Should be compatible with the PIL library - not sure what happens if it isn't
    '''
    def get_file_extensions(self):
        return self.get_config_key_formatted('extensions')

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
