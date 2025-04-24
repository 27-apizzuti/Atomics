"""
Created on Wed Aug 22

This script does RIGID motion correction with ANTS.

Run separately for Nulled and Not-nulled
'across runs'

NB: Remember to insert the inputs correctly

@author: apizz
"""
# Import libraries
import ants
import numpy as np
import nibabel as nb
import os
import glob
import nipype.interfaces.fsl as fsl
import itertools
from my_ants_rigid_motion_correction import *
from my_plot_motion import *
import pandas as pd

print("****Across runs motion correction****")

# Define inputs
STUDY_PATH = "/mnt/d/Pilot_MQ_VASO/MRI_MQ/"
SUBJ = ['sub-04']
SESS = ['2']
TASK_REF = ['unamb']  # Which was the first functional run acquired in the current session? This will be the reference?
GLOB_REF = ['8']   # insert the folder number from sess-X/singleRun that refers to the global reference (not-nulled case)
# ------------------------------

for itersu, su in enumerate(SUBJ):
    for iterse, se in enumerate(SESS):
        PATH_IN = os.path.join(STUDY_PATH, su, 'derivatives', 'func', 'MQ', 'vaso_analysis', 'steady_state', 'sess-{}'.format(se))

        PATH_MOCO = os.path.join(STUDY_PATH, su, 'derivatives', 'func', 'MQ', 'vaso_analysis', 'moco')
        if not os.path.exists(PATH_MOCO):
            os.mkdir(PATH_MOCO)
            os.mkdir(os.path.join(PATH_MOCO, 'sess-{}'.format(se)))
        if not os.path.exists(os.path.join(PATH_MOCO, 'sess-{}'.format(se), 'acrossRuns')):
            os.mkdir(os.path.join(PATH_MOCO, 'sess-{}'.format(se), 'acrossRuns'))

        # // find nifti folder with all the runs ---> ...NIFTI/func/VASO
        os.chdir(PATH_IN)
        RUNS = glob.glob("*.nii.gz")

        # Prepare Global Reference (interim): first run, first session
        # // Check carefully here
        path_reference_not_nulled = os.path.join(STUDY_PATH, su, 'derivatives', 'func', 'MQ', 'vaso_analysis', 'moco', 'sess-{}'.format(se), 'singleRun', 'run-{}'.format(GLOB_REF[itersu]))
        path_reference_nulled = os.path.join(STUDY_PATH, su, 'derivatives', 'func', 'MQ', 'vaso_analysis', 'moco', 'sess-{}'.format(se), 'singleRun', 'run-{}'.format(int(GLOB_REF[itersu]) + 1))

        filename_not_nulled = '{}_sess-{}_task-{}_acq-3dvaso_run-01_not_nulled_reference.nii.gz'.format(su, se, TASK_REF[itersu])
        filename_nulled = '{}_sess-{}_task-{}_acq-3dvaso_run-01_nulled_reference.nii.gz'.format(su, se, TASK_REF[itersu])
        # //
        for iterru, ru in enumerate(RUNS):     # Nulled and Not-nulled are already separated here

            # Define Path_out (input) where folder structure will be created
            PATH_OUT = os.path.join(PATH_MOCO, 'sess-{}'.format(se), 'acrossRuns', 'run-{}'.format(iterru))
            if not os.path.exists(PATH_OUT):
                os.mkdir(PATH_OUT)

            # Define Global Reference (input)
            basename = ru.split(os.extsep, 1)[0]
            mod = basename.split('_')

            print(mod)

            if len(mod) > 6:
                reference = os.path.join(path_reference_not_nulled, filename_not_nulled)
            else:
                reference = os.path.join(path_reference_nulled, filename_nulled)

            # Define mask (input)
            mask = os.path.join(STUDY_PATH, su, 'derivatives', 'func', 'MQ', 'vaso_analysis', 'brainmask', 'sess-{}'.format(se), 'sess_{}_mask.nii.gz'.format(se))

            # Define Moving (input)
            PATH_MOV = os.path.join(PATH_MOCO, 'sess-{}'.format(se), 'singleRun', 'run-{}'.format(iterru))
            os.chdir(PATH_MOV)
            mov_file = glob.glob("*reference.nii.gz")
            # filename_WARP = '{}_warped.nii.gz'.format(basename)
            moving4D = os.path.join(PATH_MOV, mov_file[0])
            if (moving4D ==  reference):
                print('Registration not needed.')
            else:
                print('Here registration from {} to {}'.format(moving4D, reference))

                # // Run co-registration
                my_ants_rigid_motion_correction(PATH_OUT, mask, reference, moving4D)
                path_csv = os.path.join(PATH_OUT, 'motion_traces', '{}_motion.csv'.format(basename))
                # my_plot_motion(PATH_OUT, path_csv)
