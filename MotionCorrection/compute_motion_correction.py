"""
Created on Tue Sep 20

This is an example script that does RIGID motion correction with ANTS.

Structure:
    my_ants_rigid_motion_correction
        my_create_moco_folders
        my_ants_affine_to_distance
    my_plot_motion

@author: apizz
"""

# Import libraries
import ants
from my_ants_rigid_motion_correction import *
from my_plot_motion import *

# // Define input and output for coregistration
mask = PATH_TO_MASK_FILE
reference = PATH_TO_REF_FILE
moving4D = PATH_TO_MOV_FILE
path_output = PATH_OUT

# // Execute
my_ants_rigid_motion_correction(PATH_OUT, mask, reference, moving4D)
path_csv1 = os.path.join(PATH_OUT, 'motion_traces', 'motion.csv')
my_plot_motion(PATH_OUT, path_csv1)
