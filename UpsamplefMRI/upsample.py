"""
Created on Tue Nov 29

Upsampling fMRI data

@author: apizz
"""
# Mask fMRI data to the region of interest (e.g. sphere)
# Separate volume-by-volume
# Upsample
import nibabel as nb
import numpy as np
import os
import ants
import subprocess

PATH_IN = "/mnt/c/Users/apizz/Desktop/4Kris/sub-02/fMRI/temp"
myFILE = "BOLD_interp"
NVOL = 350

# Upsampling parameters
sdelta_x = 0.820988 / 4
sdelta_y = 0.820988 / 4
sdelta_z = 0.800000 / 4

# new_data = np.zeros([648, 864, 104, NVOL], dtype=np.int8)

for itvol in range(0, NVOL):
    command = '3dresample -dxyz {} {} {} -rmode NN '.format(sdelta_x, sdelta_y, sdelta_z)
    command += '-overwrite '
    command += '-prefix {} '.format(os.path.join(PATH_IN, 'sub-02_BOLD_interp_leftMT_vol_{}_hres.nii.gz'.format(itvol)))
    command += '-input {}'.format(os.path.join(PATH_IN, 'sub-02_BOLD_interp_leftMT_vol_{}.nii.gz'.format(itvol)))
    subprocess.call(command, shell=True)

#     # Lod again
#     nii = nb.load(os.path.join(PATH_IN, 'sub-02_BOLD_interp_leftMT_vol_{}_hres.nii.gz'.format(itvol)))
#     vol = np.asarray(nii.dataobj)
#     new_data[..., itvol] = vol
#
# # Save 4D Nifti
# img = nb.Nifti1Image(new_data, header=nii.header, affine=nii.affine)
# fmri_data = os.path.join(PATH_IN, 'sub-02_BOLD_interp_leftMT_hres.nii.gz'.format(myFILE))
# nb.save(img, fmri_data)
