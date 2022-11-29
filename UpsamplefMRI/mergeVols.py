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
from copy import copy

PATH_IN = "/mnt/c/Users/apizz/Desktop/4Kris/sub-02/fMRI/temp"
myFILE = "BOLD_interp"
NVOL = 350

new_data = np.zeros([648, 864, 104, NVOL], dtype=np.int8)

for itvol in range(0, NVOL):
    print('Filling wiht vol {}'.format(itvol))
    # Lod again
    nii = nb.load(os.path.join(PATH_IN, 'sub-02_BOLD_interp_leftMT_vol_{}_hres.nii.gz'.format(itvol)))
    vol = np.asarray(nii.dataobj)
    new_data[..., itvol] = vol

# Save 4D Nifti
new_header = copy(nii.header)
new_header.set_data_dtype(datatype=np.int8)
img = nb.Nifti1Image(new_data, header=new_header, affine=nii.affine)
fmri_data = os.path.join(PATH_IN, 'sub-02_BOLD_interp_leftMT_hres.nii.gz'.format(myFILE))
nb.save(img, fmri_data)
