import tkinter
import shutil
import os
import logging
from tkinter import Tk
from tkinter import ttk
from tkinter import filedialog
from Config import Config
from Filesystem import Filesystem
from PIL import ImageTk
from File import File
import sys


class Interface(Tk):
    size = (640, 480)
    image = None
    thumb = None

    def __init__(self, config: Config, filesystem: Filesystem):
        Tk.__init__(self)

        self.config = config
        self.filesystem = filesystem

        self.bind("<Configure>", self.on_resize)

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

        self.image_preview = tkinter.Label(self.image_frame)
        self.image_preview.pack(fill="both", expand=True)

        # Add the thumbnail list here

        self.destination_label = tkinter.Label(self.destinations_frame, text="Destinations")
        self.destination_label.grid(row=0, column=0, columnspan=2)

        self.destination_list = tkinter.Listbox(self.destinations_frame)
        self.populate_listbox(self.destination_list, "destinations")
        self.destination_list.bind('<Double-Button-1>', self.move_image_handler)
        self.destination_list.grid(row=1, column=0, columnspan=2, sticky="ns")

        self.add_destination = tkinter.Button(self.destinations_frame, text="Add", command=self.add_destination_handler)
        self.add_destination.grid(row=2, column=0, sticky="ew")

        self.remove_destination = tkinter.Button(self.destinations_frame, text="Remove",
                                                 command=self.remove_destination_handler)
        self.remove_destination.grid(row=2, column=1, sticky="ew", pady=5)

        self.source_label = tkinter.Label(self.sources_frame, text="Sources")
        self.source_label.grid(row=0, column=0, columnspan=2, sticky="ns", pady=5)

        # @todo: Actually set up the source list to work properly with adding/removing
        self.source_list = tkinter.Listbox(self.sources_frame)
        self.populate_listbox(self.source_list, "sources")
        self.source_list.grid(row=1, column=0, columnspan=2, sticky="ns")

        self.add_source = tkinter.Button(self.sources_frame, text="Add", command=self.add_source_handler)
        self.add_source.grid(row=2, column=0, sticky="ew", pady=5)

        self.remove_source = tkinter.Button(self.sources_frame, text="Remove", command=self.remove_source_handler)
        self.remove_source.grid(row=2, column=1, sticky="ew", pady=5)

        self.sources_frame.rowconfigure(1, weight=1)
        self.destinations_frame.rowconfigure(1, weight=1)

        self.menubar = tkinter.Menu(self)

        self.filemenu = tkinter.Menu(self.menubar, tearoff=0)
        self.filemenu.add_command(label="Quit", command=self.quit)
        self.menubar.add_cascade(label="File", menu=self.filemenu)

        self.helpmenu = tkinter.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Help", menu=self.helpmenu)

        self.debuglevel = tkinter.IntVar()
        self.debuglevel.set(logging.getLogger().level)

        self.debugmenu = tkinter.Menu(self.helpmenu, tearoff=0)
        self.debugmenu.add_radiobutton(label="OFF", command=self.set_logging, variable=self.debuglevel,
                                       value=logging.NOTSET)
        self.debugmenu.add_radiobutton(label="DEBUG", command=self.set_logging, variable=self.debuglevel,
                                       value=logging.DEBUG)
        self.debugmenu.add_radiobutton(label="INFO", command=self.set_logging, variable=self.debuglevel,
                                       value=logging.INFO)
        self.debugmenu.add_radiobutton(label="WARNING", command=self.set_logging, variable=self.debuglevel,
                                       value=logging.WARNING)
        self.debugmenu.add_radiobutton(label="ERROR", command=self.set_logging, variable=self.debuglevel,
                                       value=logging.ERROR)
        self.debugmenu.add_radiobutton(label="CRITICAL", command=self.set_logging, variable=self.debuglevel,
                                       value=logging.CRITICAL)

        self.helpmenu.add_cascade(label="Set Debug Level", menu=self.debugmenu)

        self.configure(menu=self.menubar)

        self.update()

        self.set_image(filesystem.get_next_image())

    def set_logging(self):
        logging.getLogger().setLevel(self.debuglevel.get())
        return

    def populate_listbox(self, listbox, source):
        """Populate a provided listbox"""
        listbox.delete(0, tkinter.END)
        for directory in self.config[source]:
            listbox.insert(tkinter.END, directory)

    def add_source_handler(self):
        self.add_directory(self.source_list, Config.SOURCES)

    def add_destination_handler(self):
        self.add_directory(self.destination_list, Config.DESTINATIONS)

    def add_directory(self, listbox, config_source):
        """Handler for adding a new directory"""
        directory = self.get_directory()

        short_dir = Filesystem.get_filename(directory)

        # short circuit if there was not a directory selected
        if not directory or short_dir in self.config[config_source]:
            return

        self.config[config_source][short_dir] = directory

        self.populate_listbox(listbox, config_source)
        logging.info("Adding " + directory + " to " + config_source + " list")

    def remove_source_handler(self):
        directory = self.config[Config.SOURCES][self.source_list.get(tkinter.ACTIVE)]
        self.remove_directory(Config.SOURCES, directory, self.source_list)

    def remove_destination_handler(self):
        directory = self.config[Config.DESTINATIONS][self.destination_list.get(tkinter.ACTIVE)]
        self.remove_directory(Config.DESTINATIONS, directory, self.destination_list)

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
            logging.info("Removing " + directory + " from the " + config_source + " list")
            self.populate_listbox(listbox, config_source)
        else:
            logging.warning("Unable to find directory " + directory + " to remove")

    def move_image_handler(self, event):
        # is this actually the best way to get the selected destination directory?
        destination = self.config[Config.DESTINATIONS][self.destination_list.get(tkinter.ACTIVE)]

        filename = self.filesystem.get_filename(self.filesystem.current_filename)

        destination_full = os.path.join(destination, self.filesystem.get_filename(self.filesystem.current_filename))

        shutil.move(self.filesystem.current_filename, destination_full)

        logging.info("Moving " + filename + " from " + self.filesystem.current_filename + " to " + destination)

        self.set_image(self.filesystem.get_next_image(self.filesystem.current_filename))

        self.filesystem.remove_image_resource(self.filesystem.current_filename)

    def on_resize(self, event):
        if self.image is not None:
            self.set_image(self.image)
        else:
            self.set_image(self.filesystem.get_next_image())

    def set_image(self, file: File):
        if file is None:
            self.clear_image()
            return

        size = (self.image_preview.winfo_width(), self.image_preview.winfo_height())

        image = file.get_thumbnail(size)
        thumb = ImageTk.PhotoImage(image)

        self.image = file
        self.thumb = thumb
        self.image_preview.configure(image=thumb)

        self.wm_title(self.filesystem.get_filename(self.filesystem.current_filename))

    def clear_image(self):
        self.image = None
        self.thumb = None
        self.image_preview.configure(image="")

        self.wm_title('No images')

    def get_imageframe_size(self):
        return self.image_preview.winfo_width(), self.image_preview.winfo_height()

    @staticmethod
    def get_directory(message=None):
        if message is None:
            message = "Select Directory"

        directory = filedialog.askdirectory(title=message)

        if not directory:
            logging.info("No directory selected")
            return None

        return directory
