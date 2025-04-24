"""
Created on Wed Aug 22

This script does RIGID motion correction with ANTS.

Run separately for Nulled and Not-nulled

'within run case'

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
import pandas as pd
from my_ants_rigid_motion_correction import *
from my_plot_motion import *


print("****Within run motion correction****")

# Define inputs
STUDY_PATH = "/mnt/d/Pilot_MQ_VASO/MRI_MQ/"
SUBJ = ['sub-08']
SESS = ['1']
# RUN = [] # can be a list filenames (temporary ordered)

for itersu, su in enumerate(SUBJ):

    PATH_MOCO = os.path.join(STUDY_PATH, su, 'derivatives', 'func', 'MQ', 'vaso_analysis', 'moco')

    if not os.path.exists(PATH_MOCO):
        os.mkdir(PATH_MOCO)

    for iterse, se in enumerate(SESS):
        PATH_IN = os.path.join(STUDY_PATH, su, 'derivatives', 'func', 'MQ', 'vaso_analysis', 'steady_state', 'sess-{}'.format(se))
        print('Working on {} session {}'.format(su, se))

        if not os.path.exists(os.path.join(PATH_MOCO, 'sess-{}'.format(se))):
            os.mkdir(os.path.join(PATH_MOCO, 'sess-{}'.format(se)))
        if not os.path.exists(os.path.join(PATH_MOCO, 'sess-{}'.format(se), 'singleRun')):
            os.mkdir(os.path.join(PATH_MOCO, 'sess-{}'.format(se), 'singleRun'))

        # // find nifti folder with all the runs ---> ...NIFTI/func/VASO
        os.chdir(PATH_IN)
        RUNS = glob.glob("{}_sess-{}*.nii.gz".format(su, se))
        print(RUNS)

        for iterru, ru in enumerate(RUNS):     # Nulled and Not-nulled are already separated here
            PATH_OUT = os.path.join(PATH_MOCO, 'sess-{}'.format(se), 'singleRun', 'run-{}'.format(iterru))
            if not os.path.exists(PATH_OUT):
                os.mkdir(PATH_OUT)

            print('Loading file: {}...'.format(ru))
            basename = ru.split(os.extsep, 1)[0]
            nii = nb.load(os.path.join(PATH_IN, ru))
            data = nii.get_fdata()

            # // Define input for coregistration
            mask = os.path.join(STUDY_PATH, su, 'derivatives', 'func', 'MQ', 'vaso_analysis', 'brainmask', 'sess-{}'.format(se), 'sess_{}_mask.nii.gz'.format(se))
            ref = np.mean(data[..., 4:6],axis=-1)
            moving4D = os.path.join(PATH_IN, ru)

            # Save reference image
            img = nb.Nifti1Image(ref, header=nii.header, affine=nii.affine)
            reference = os.path.join(PATH_OUT, '{}_reference.nii.gz'.format(basename))
            nb.save(img, reference)

            my_ants_rigid_motion_correction(PATH_OUT, mask, reference, moving4D)
            path_csv1 = os.path.join(PATH_OUT, 'motion_traces', '{}_motion.csv'.format(basename))
            my_plot_motion(PATH_OUT, path_csv1)
