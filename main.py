from Config import Config
from Interface import Interface
from Filesystem import Filesystem
from Application import Application
import logging

if __name__ == "__main__":
    # default logging level to DEBUG for now
    logging.getLogger().setLevel(logging.DEBUG)

    config = Config()
    filesystem = Filesystem(config)
    interface = Interface(config, filesystem)
    application = Application(config, filesystem, interface)

    interface.minsize(800, 600)
    interface.mainloop()
