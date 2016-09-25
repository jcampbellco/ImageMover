from Config import Config
from Interface import Interface
from Filesystem import Filesystem
from Application import Application

if __name__ == "__main__":
    config = Config()
    filesystem = Filesystem(config)
    interface = Interface(config, filesystem)
    application = Application(config, filesystem, interface)

    interface.minsize(800, 600)
    interface.mainloop()
