import tkinter
import shutil
import os
from tkinter import Tk
from tkinter import ttk
from tkinter import filedialog
from Config import Config


class Interface(Tk):
    size = (640, 480)

    def __init__(self, application):
        Tk.__init__(self)

        self.application = application

        self.image_frame = tkinter.Frame(self)
        self.image_frame.pack(side="left", fill="both", expand=True, padx=5)

        self.control_frame = tkinter.Frame(self)
        self.control_frame.pack(side="right", fill="both", expand=False, padx=5)

        self.destinations_frame = tkinter.Frame(self.control_frame)
        self.destinations_frame.pack(fill="y", expand=1)

        self.separator = ttk.Separator(self.control_frame)
        self.separator.pack(fill="x", expand=0, pady=5)

        self.sources_frame = tkinter.Frame(self.control_frame)
        self.sources_frame.pack(fill="y", expand=1)

        image = application.get_image()
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
        Populate the listbox
    '''

    def populate_listbox(self, listbox, source):
        listbox.delete(0, tkinter.END)
        for directory in self.application.config[source]:
            listbox.insert(tkinter.END, directory)

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
        if not directory or short_dir in self.application.config[config_source]:
            return

        self.application.config[config_source][short_dir] = directory

        self.populate_listbox(listbox, config_source)
        print("Adding " + directory + " to " + config_source + " list")

    def remove_source_handler(self):
        directory = self.application.config[Config.SOURCES][self.source_list.get(tkinter.ACTIVE)]
        self.remove_directory(Config.SOURCES, directory, self.source_list)

    def remove_destination_handler(self):
        directory = self.application.config[Config.DESTINATIONS][self.destination_list.get(tkinter.ACTIVE)]
        self.remove_directory(Config.DESTINATIONS, directory, self.destination_list)

    '''
        Handler for removing a directory
    '''

    def remove_directory(self, config_source, directory, listbox):
        # This feels a bit dirty, but I'm not sure how to handle the directory coming in as the full path, but needing
        # the key to access it... @todo Get the key from the listbox, not the item?
        if directory not in self.application.config[config_source]:
            for alias in self.application.config[config_source]:
                if directory == self.application.config[config_source][alias]:
                    directory = alias
                    break

        removed = self.application.config[config_source].pop(directory, 0)

        if removed != 0:
            print("Removing " + directory + " from the " + config_source + " list")
            self.populate_listbox(listbox, config_source)
        else:
            print("Unable to find directory " + directory + " to remove")

    '''
        Handler for moving an image
        The event param isn't used, but is passed in.
    '''

    def move_image_handler(self, event):
        # is this actually the best way to get the selected destination directory?
        destination = self.application.config[Config.DESTINATIONS][self.destination_list.get(tkinter.ACTIVE)]

        filename = self.application.get_filename(self.application.current_image)

        destination_full = os.path.join(destination, self.application.get_filename(self.application.current_image))

        shutil.move(self.application.current_image, destination_full)

        print("Moving " + filename + " from " + self.application.current_image + " to " + destination)

        self.application.current_image = self.application.get_new_image()
        self.application.set_image()

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
