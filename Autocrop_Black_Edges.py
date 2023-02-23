"""Automatically crops an image or stack to cut off black edges and corners.
It will work on the active image, whether there it is a single image or a stack.
This is especially useful for registered images with non-straight, moving black edges.
"""

from __future__ import print_function, division
from os.path import join, splitext
from operator import mul

from ij import IJ, ImagePlus
from ij.process import ImageProcessor, ByteProcessor, ShortProcessor
from ij.plugin import ZProjector
from ij.gui import Roi

def find_largest_rectangle_2D(array):
    """Gets the coordinates of the largest rectangle of 1s in a 2D binary array"""

    #gets the sums of successive vertical pixels
    # vert_sums = (np.zeros_like(array)).astype('float')
    vert_sums = [[0] * len(array[0]) for _ in range(len(array))]
    vert_sums[0] = array[0]
    for i in range(1,len(array)):
        for j in range(len(array[i])):
            vert_sums[i][j] = (vert_sums[i-1][j] + array[i][j]) * array[i][j]

    #declare some variables for keeping track of the largest rectangle
    max_area = -1
    pos_at_max_area = (0,0)
    height_at_max_area = -1
    x_end = 0
    
    #go through each row of vertical sums and find the largest rectangle
    for i in range(len(vert_sums)):
        positions = []  # a stack
        heights = []  # a stack
        for j in range(len(vert_sums[i])):
            h = vert_sums[i][j]
            if len(positions)==0 or h > heights[-1]:
                heights.append(h)
                positions.append(j)
            elif h < heights[-1]:
                while len(heights) > 0 and h < heights[-1]:
                    h_tmp = heights.pop(-1)
                    pos_tmp = positions.pop(-1)
                    area_tmp = h_tmp * (j - pos_tmp)
                    if area_tmp > max_area:
                        max_area = area_tmp
                        pos_at_max_area = (pos_tmp,i) #this is the bottom left
                        height_at_max_area = h_tmp
                        x_end = j
                heights.append(h)
                positions.append(pos_tmp)
        while len(heights) > 0:
            h_tmp = heights.pop(-1)
            pos_tmp = positions.pop(-1)
            area_tmp = h_tmp * (j - pos_tmp)
            if area_tmp > max_area:
                max_area = area_tmp
                pos_at_max_area = (pos_tmp,i) #this is the bottom left
                height_at_max_area = h_tmp
                x_end = j

    top_left = (int(pos_at_max_area[0]),int(pos_at_max_area[1] - height_at_max_area) + 1)
    width = int(x_end - pos_at_max_area[0])
    height = int(height_at_max_area - 1)

    # need to add 1 to the width and height for imagej
    width += 1
    height += 1

    return top_left,width,height

def reshape(lst, shape):
    if len(shape) == 1:
        return lst
    n = reduce(mul, shape[1:])
    return [reshape(lst[i*n:(i+1)*n], shape[1:]) for i in range(len(lst)//n)]

def open_test_img():
    """Opens the test image. This is mostly for debugging."""

    #gets the directory and stack name
    data_dir = "."
    filename = "stk_adj_reg.tif"
    img_path = join(data_dir,filename)
    img = IJ.openImage(img_path)

    return(img)

def main():

    # ensures black background for binary images
    IJ.run("Options...", "black")
	
    # opens the image and gets its name
    # imp = open_test_img()
    # imp.show()
    imp = IJ.getImage()
    title = imp.getTitle()
    basename, extension = splitext(title)

    # does a minimum projection and makes a mask
    imp_min = ZProjector.run(imp, 'min')
    if imp_min.getBitDepth()==24:
    	IJ.run(imp_min, "8-bit", "")
    ip = imp_min.getProcessor()
    ip.setThreshold(1,99999,1)
    mask = ip.createMask()
    mask = ImagePlus("mask",mask)
    IJ.run(mask, "Fill Holes", "")     

    # converts to list and then finds the crop coordinates
    px = mask.getProcessor().getPixels()
    px = [-int(_) for _ in px] #for some reason the 1s are -1 here
    px = reshape(px, (imp.height,imp.width))
    crop_top_left,crop_width,crop_height = find_largest_rectangle_2D(px)

    # crops the original image
    imp.setRoi(crop_top_left[0], crop_top_left[1], crop_width, crop_height)
    imp_cropped = imp.resize(crop_width, crop_height, "bilinear")
    IJ.run(imp, "Select None", "")
    imp_cropped.setTitle(basename + "_autocrop" + extension)
    imp_cropped.show()

if __name__ in ["__builtin__","__main__"]:
    main()