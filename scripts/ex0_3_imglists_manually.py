# -*- coding: utf-8 -*-
"""
piscope introduction script 3 - manual creation of image lists  

This script gives an introduction into the creation and the handling of 
ImgList objects. Each list normally contains images of a certain type (e.g.
on, off, dark, offset). The separation by these file types is normally done
automatically within a Dataset object (see e.g. following script 
ex0_4_imglists_auto.py or example script ex01_analysis_setup.py) using a 
certain camera type (see previous script ex0_2_camera_setup.py).

In this example these features are NOT used but rather, an on and off band 
image list is created manually without previous definition of the Camera type
(i.e. file naming convention, etc.) starting off with creating an ImgList 
containing all images of type FITS in the test data image base directory. 
On and off band lists are then consecutively extracted from this list. 

Some basic features of list objects are introduced (e.g. linking of lists, dark
correction, automatic blurring, cropping, size reduction).
"""

import piscope
from matplotlib.pyplot import subplots, close, show
from datetime import datetime

from os.path import join, isfile
from os import listdir

### IMPORT GLOBAL SETTINGS
from SETTINGS import IMG_DIR, SAVEFIGS, SAVE_DIR, FORMAT, DPI, OPTPARSE

### RELEVANT DIRECTORIES AND PATHS
OFFSET_FILE = join(IMG_DIR, "EC2_1106307_1R02_2015091607064723_D0L_Etna.fts")
DARK_FILE = join(IMG_DIR, "EC2_1106307_1R02_2015091607064865_D1L_Etna.fts")

if __name__ == "__main__":
    close("all")
    
    ### Get all images in the image path which are FITS files (actually all)
    all_paths = [join(IMG_DIR, f) for f in listdir(IMG_DIR) if\
                            isfile(join(IMG_DIR, f)) and f.endswith("fts")]
                            
    ### Now put them all into an image list 
                            
    # Note that the files are not separated by filter type, or dark and offset, 
    # etc. so the list simply contains all images of type fts which were found
    # in IMG_DIR
    list_all_imgs = piscope.imagelists.ImgList(all_paths, list_id = "all")
    
    # Split the list by on band file type (which is identified by acronym
    # "F01" at 4th position in file name after splitting using delimiter "_")
    # creates two new list objects, one containing matches (i.e. on band images
    # the other containing the rest)
    on_list, rest = list_all_imgs.separate_by_substr_filename(sub_str="F01",
                                                              sub_str_pos=4,
                                                              delim="_")
    # now extract all off band images from the "rest" list                                                                      
    off_list, rest = rest.separate_by_substr_filename(sub_str="F02",
                                                      sub_str_pos=4,
                                                      delim="_")
    
    # Link the off band list to on band list (the index in the offband list is 
    # changed whenever the index is changed in the on band list based on acq.
    # time stamp). Note, that a Camera class was not defined here (see prev. 
    # script). Specify the required information in the camera (manually, not
    # required if camera was defined beforehand)
    on_list.camera.delim = "_"
    on_list.camera.time_info_pos = 3
    on_list.camera.time_info_str = "%Y%m%d%H%M%S%f"
    off_list.camera.delim = "_"
    off_list.camera.time_info_pos = 3
    off_list.camera.time_info_str = "%Y%m%d%H%M%S%f"
    
    on_list.link_imglist(off_list)
    
    ### Load dark and offset images and set them in on band image list
    dark_img = piscope.image.Img(DARK_FILE)
    offset_img = piscope.image.Img(OFFSET_FILE)
    
    on_list.add_master_dark_image(dark_img)
    on_list.add_master_offset_image(offset_img)
    
    # Go to image number 100 in on band list
    on_list.goto_img(100)
    
    ### Change image preparation settings (these are applied on image load)
    # region of interest (in abs. coords)
    on_list.roi_abs = [100, 100, 1300, 900] 
    # activate cropping in image list
    on_list.crop = 1 
    # scale down to pyramid level 2
    on_list.pyrlevel = 2 
    # activate automatic dark correction in list
    on_list.camera.DARK_CORR_OPT = 1 #see previous script
    on_list.darkcorr_mode = True 
    # blur the on band images
    on_list.add_gaussian_blurring(3) 
    
    # get current on band image (no. 100 in list), all previously set 
    # preparation settings are applied to this image
    on_img = on_list.current_img() 
    
    # get current off band image (no. 100 in list, index was automatically 
    # changed since it is linked to on band list. Note that this image is 
    # unedited
    off_img = off_list.current_img()
    
    fig, ax = subplots(1,2, figsize=(18,6))
    
    on_img.show(ax = ax[0])
    on_time_str = datetime.strftime(on_img.start_acq, "%Y-%m-%d %H:%M:%S")
    ax[0].set_title("Current img (on list): %s" %on_time_str)
    
    # show the current off band image as well (this iamge is unedited)
    off_img.show(ax = ax[1])
    off_time_str = datetime.strftime(off_img.start_acq, "%Y-%m-%d %H:%M:%S")
    ax[1].set_title("Current img (off band list): %s" %off_time_str)
        
    
    ### IMPORTANT STUFF FINISHED    
    if SAVEFIGS:
        fig.savefig(join(SAVE_DIR, "ex0_2_out_1.%s" %FORMAT),
                           format=FORMAT, dpi=DPI)
        
    
    # Display images or not    
    (options, args)   =  OPTPARSE.parse_args()
    try:
        if int(options.show) == 1:
            show()
    except:
        print "Use option --show 1 if you want the plots to be displayed"