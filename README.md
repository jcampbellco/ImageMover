# ImageMover
A simple Python script to facilitate moving images around

I used to know of a plugin for Firefox that would save images directly to a directory by right clicking on an image, then clicking "Save To" and selecting the folder from a list.

Frustrated that Chrome didn't offer a similar plugin, I decided to whip up a little image mover to help at least bulk-save images then clean them up.

# Usage
Opening the application for the first time should show nothing, on the right hand side add some source and destination directories to get started.

Double click any of the items in the list on the right, and the image you see will be moved to that directory. It couldn't be more simple!

# Configuration
The config file is stored (on Windows) in the AppData directory. For Windows, it's located at `%appdata%\Local\ImageMover\ImageMover` in a file called `config.ini`

If you have already run the application once, that file should be created. It's structure will look like:

```
[directories]
to = C:\Path\To\Store\File

[sources]
from = C:\Path\To\Look\For\File

[extensions]
jpg = jpg
png = png
gif = gif
```

Hopefully it should be fairly self explanatory, but the three sections are configurable.

`directories` represents the destination directories. If you add a destination via the application, it will show up in the list with the lowest level folder name as the alias (`to` in the example), but this can be changed (via the config) to anything you'd like.

`sources` configures where to search for files. For a lot of people by default, this might be the Downloads directory. Currently the alias (`from` in the example) doesn't really "do" anything, so feel free to name it whatever you'd like.

`extensions` are a list of file extension types to browse for. Be careful with modifying this list, I have not tested some of the more "odd" file types. Anything in this list must be an openable and displayable file type according to the Python `PIL` (Pillow) library

# ToDo

* ~~Break up code into multiple files/classes~~
* ~~Add list of source directories~~
* Add configuration menu for file extensions
* Add prev/next buttons under image preview
* ~~Make images resize to fill the window while maintaining aspect ratio~~
* Add options for checking for duplicate images
* Handle instances where the destination path already exists (by name)

# Bugs

* When the program first opens, even if there is an image to load, it fails to load the image preview, even on subsequent file move events

# Duplicate Finder

In of itself a "duplicate checker" is an intense operation, especially if the destination directory has a large number of images in it already.

Based on this very nice article (http://www.pyimagesearch.com/2014/09/15/python-compare-two-images/) it looks easy enough to compare two images to each other (and adding this functionality to the File object would be trivial)

However, my preferred method of doing this feature would be to find a mechanism for generating a simple hash of an image, build out a database of hashes for existing images, then compare the image being moved against the existing database, a secondary (and more "accurate") check can then be made against images that seem similar.

The package https://github.com/JohannesBuchner/imagehash seems to offer functionality similar to what I'm looking for.