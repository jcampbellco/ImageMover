import os

from PIL import Image


class File:
    """ :type path: string """
    path = ''

    """ :type image_handle: Image """
    image_handle = None

    def __init__(self, path):
        if not os.path.exists(path):
            raise FileNotFoundError('Specified file ' + path + ' not found')

        self.path = path

    def get_thumbnail(self, size):
        """
        Generate a thumbnail based on the image handle above. Make sure to call self.get_image_handle to be
        certain an image handle is available, as self.image_handle defaults to None!
        :param size:
        :rtype: PIL.PngImagePlugin.PngImageFile|PIL.JpegImagePlugin.JpegImageFile
        """
        self.get_image_handle().thumbnail(size, Image.ANTIALIAS)

        return self.image_handle

    def get_image_handle(self):
        """
        Lazy-loads an image file handle
        :rtype: PIL.PngImagePlugin.PngImageFile|PIL.JpegImagePlugin.JpegImageFile
        """
        if self.image_handle is None:
            self.image_handle = Image.open(self.path)

        return self.image_handle

    def get_filename(self):
        """
        Get the filename (not full path) of the file
        :rtype: string
        """
        return os.path.split(self.path)[-1]
