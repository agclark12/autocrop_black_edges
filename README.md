# Autocrop_Black_Edges.py

This is a jython script for ImageJ/FIJI that automatically crops images that have black edges around the outsides.
Such black edges commonly appear after registering image stacks.

## Installation

To install this script to ImageJ or FIJI, just drop it into the plugins folder.
For OSX users, right click on the ImageJ or FIJI icon in the finder and click "Show Package Contents" to find the plugins folder.
Then restart ImageJ/FIJI and you should see "Autocrop Black Edges" at the bottom of the Plugins menu.

Alternatively, you can drag the .py file into ImageJ/FIJI and it will open it in the editor.
Then you can just run it from there.

## Using the plugin

The plugin will work on the active image.
If there are no images open, you will get an error message to that effect.
The cropped image will be labeled with "_autocrop" at the end of the filename.
You can test the plugin using the example image stack provided here. 

It may be useful to use this plugin in batch.
You can incorporate it into an ImageJ macro by calling ```run("Autocrop Black Edges");```.
For example, if you want to autocrop all of the .tif files in a directory:

    setBatchMode(true);
    dir = getDirectory("Which directory?");
    dir_list = getFileList(dir);
    extension = ".tif";
    
    for (i=0;i<lengthOf(dir_list);i++) {
        if (endsWith(dir_list[i],extension)) {
            open(dir + dir_list[i]);
            run("Autocrop Black Edges");
            saveAs(dir + replace(dir_list[i], extension, "_autocrop" + extension));
            run("Close All");
        }
    }

Please let me know if you have any trouble using this or if it is giving any unexpected results.
Thanks!