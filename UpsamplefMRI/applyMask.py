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

PATH_IN = "/mnt/c/Users/apizz/Desktop/4Kris/sub-02/fMRI"
PATH_OUT = "/mnt/c/Users/apizz/Desktop/4Kris/sub-02/fMRI/temp"
myFILE = "BOLD_interp"

# Load fMRI
print(os.path.join(PATH_IN, '{}.nii'.format(myFILE)))
nii = nb.load(os.path.join(PATH_IN, '{}.nii'.format(myFILE)))
data = np.asarray(nii.dataobj)

# Load Mask
nii = nb.load(os.path.join(PATH_IN, 'sub-02_leftMT_Sphere16radius.nii.gz'))
mas = np.asarray(nii.dataobj)

idx = mas == 0
data[idx, None] = 0

# Save masked fMRI
img = nb.Nifti1Image(data, header=nii.header, affine=nii.affine)
mask_data = os.path.join(PATH_IN, 'sub-02_{}_leftMT.nii.gz'.format(myFILE))
nb.save(img, mask_data)
#
# Create and save each volume separatly
VOLS = np.shape(data)[-1]
for ivol in range(VOLS):
    print("Saving vol {}".format(ivol))
    img = nb.Nifti1Image(data[..., ivol], header=nii.header, affine=nii.affine)
    mask_data = os.path.join(PATH_OUT, 'sub-02_{}_leftMT_vol_{}.nii.gz'.format(myFILE, ivol))
    nb.save(img, mask_data)
