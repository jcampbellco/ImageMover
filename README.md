# ImageMover
A simple Python script to facilitate moving images around

I used to know of a plugin for Firefox that would save images directly to a directory by right clicking on an image, then clicking "Save To" and selecting the folder from a list.

Frustrated that Chrome didn't offer a similar plugin, I decided to whip up a little image mover to help at least bulk-save images then clean them up.

# Usage
Make sure you have the appropriate paths configured as seen below

Once that's done, you should be able to open the application and see an image to the left hand side. On the right, will be your sources, along with an Add or Remove directory button.

Double click any of the items in the list on the right, and the image you see will be moved to that directory. It couldn't be more simple!

# Configuration
The config file is stored (on Windows) in the AppData directory. For Windows, it's located at `%appdata%\Local\reddeth\ImageMover` in a file called `config.ini`

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