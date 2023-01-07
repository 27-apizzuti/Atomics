"""
Created on Sat 07-01-23
!!! FLAT
NB: Heatmap for vessel detection (n. of vox shown same labes/n. of voxels I have along the depth)

@author: apizz
"""

import glob
import numpy as np
import nibabel as nb
import os
import matplotlib.pyplot as plt

PATH_IN = "/mnt/c/Users/apizz/Desktop/testing_AHEAD/AHEAD_codes/test-data/bigbrain/05_patch_flatten"
FILE1 = "sub-bigbrain_full16_100um_optbal_roi_HG_LH_seg_multilaterate_perimeter_chunk_histology_flat_800x800_voronoi.nii.gz"

# Parameters
START_Z = 28    # to not include flattening artifact
END_Z = 165     # to not include flattening artifact
THR = 0.85      # Intensity threshold, above it is a vessel
THR_HEAT = 10   # Threshold heatmap (0-100%)
# ------------------------------------------------------------------------------

# Load flatten map
nii = nb.load(os.path.join(PATH_IN, FILE1))
data = np.asarray(nii.dataobj)
dims = np.shape(data)

# Intensity normalization
data_max = np.max(data)
data = np.divide(data, data_max)

# Save
basename, ext = nii.get_filename().split(os.extsep, 1)
cort = nb.Nifti1Image(data, header=nii.header, affine=nii.affine)
nb.save(cort, "{}_norm.nii.gz".format(basename))

# Create output matrix
CI_heatmap = np.zeros(dims)  # vascular index
temp = data[:,:,START_Z:END_Z] > THR
tot_vox = END_Z-START_Z

# Inspect each voxel and compute heatmap
for i in range(0, dims[0]):
    for j in range(0, dims[0]):
        n_vox = np.sum(temp[i, j, START_Z:END_Z])  # number of voxels showing same value across depths
        if (n_vox > 0):
            CI_heatmap[i, j, START_Z:END_Z] = (n_vox / tot_vox) * 100  # percentage with respect the whole depth

# Save heatmap
out_name = '{}_heatmap.nii.gz'.format(basename)
out = nb.Nifti1Image(CI_heatmap, header=nii.header, affine=nii.affine)
nb.save(out, out_name)

# Plot heatmap histogram
fig1, axs = plt.subplots(1, 1)
img = axs.hist(CI_heatmap[..., 100])
axs.set_xlabel("Vessel detection index", fontsize=20)
axs.set_ylabel("Frequency", fontsize=20)
axs.set_title('Histogram for vessel detection index', fontsize=22, pad=20)
axs.set_xlim(5, 40)
axs.set_ylim(0, 25)
fig1.savefig('{}_Histogram'.format(basename), bbox_inches='tight')
fig1.show()

# Save thresholded heatmap
CI_heatmap = CI_heatmap > THR_HEAT
out_name = '{}_heatmap_bin_{}.nii.gz'.format(basename, THR_HEAT)
out = nb.Nifti1Image(CI_heatmap, header=nii.header, affine=nii.affine)
nb.save(out, out_name)
