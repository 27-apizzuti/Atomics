"""
Created on Tue Nov 29

Create hypercolumns and plot time-dependent layer profiles

@author: apizz
"""
import bvbabel as bv
import nibabel as nb
import numpy as np
import os
from average_trials import my_average_trials
import matplotlib.pyplot as plt

PATH_IN = "/mnt/c/Users/apizz/Desktop/4Kris/sub-02/CUT_DATA"
PATH_OUT = "/mnt/c/Users/apizz/Desktop/4Kris/sub-02/CUT_DATA/derivatives"
CONDITIONS = ["Horizontal", "Vertical", "Diag45", "Diag135"]
WINN_COND = "Diag135"

# Create output folder
if not os.path.exists(PATH_OUT):
    os.mkdir(PATH_OUT)

# Compute trials average
fmri_avg_trial = []
for itcond in CONDITIONS:
    print("Computing trial average for condition: {}...".format(itcond))
    path_nii_data = os.path.join(PATH_IN, 'sub-02_BOLD_interp_leftMT_hres_CUT.nii.gz')
    path_to_protocol = os.path.join(PATH_IN, 'sub-02_Pilot_AOM_run01.prt')
    my_average_trials(path_nii_data, path_to_protocol, PATH_OUT, condition=itcond, res='TR', TR=1000, window=1)

    # Loading trials average file
    nii = nb.load(os.path.join(PATH_OUT, 'sub-02_BOLD_interp_leftMT_hres_CUT_{}_trials_avg.nii.gz'.format(itcond)))
    fmri_avg_trial.append(np.asarray(nii.dataobj))
print(fmri_avg_trial)

# Load Winner Map (1: Horizontal, 2: Vertical, 3: Diag45, 4: Diag135)
print("Load winner map...")
nii = nb.load(os.path.join(PATH_IN, 'sub-02_leftMT_Sphere16radius_BOLD_winner_map_scaled_4_gm_CUT.nii.gz'))
win_map = np.asarray(nii.dataobj)

if WINN_COND == "Horizontal":
    idx_win_map = (win_map == 1)
elif WINN_COND == "Vertical":
    idx_win_map = (win_map == 2)
elif WINN_COND == "Diag45":
    idx_win_map = (win_map == 3)
else:
    idx_win_map = (win_map == 4)

# Load statistical mask: BOLD FDR threshold (or BOLD FDR + cross-validation: sub-02_leftMT_Sphere16radius_BOLD_CV_AVG_mask_scaled_4_gm_CUT.nii.gz)
print("Load statistical mask...")
nii = nb.load(os.path.join(PATH_IN, 'binary_masks', 'sub-02_leftMT_Sphere16radius_BOLD_FDR_mask_scaled_4_gm_CUT.nii.gz'))
stat_mask = np.asarray(nii.dataobj)
idx_stat = stat_mask > 0

# Load layers
print("Load statistical mask...")
nii = nb.load(os.path.join(PATH_IN, 'sub-02_laynii_layers_equivol_CUT.nii.gz'))
layers = np.asarray(nii.dataobj)
idx_lay1 = layers == 1
idx_lay2 = layers == 2
idx_lay3 = layers == 3

# // TODO: Here we can load and add other mask or map to guide our voxel selection
# eg. sub-02_leftMT_Sphere16radius_BOLD_sensitivity_map_scaled_4_gm_CUT.nii.gz,
# sub-02_leftMT_Sphere16radius_BOLD_specificity_map_scaled_4_gm_CUT.nii.gz,
# sub-02_leftMT_Sphere16radius_BOLD_FDR_BOLD_columns_full_depth_UVD_columns_mode_filter_CUT.nii.gz

# Voxel selection per layer
fmri_condition_layers = []
for itcond, cond in enumerate(CONDITIONS):
    fmri_layers = []
    fmri_layers.append(fmri_avg_trial[itcond][idx_win_map * idx_stat * idx_lay1])
    fmri_layers.append(fmri_avg_trial[itcond][idx_win_map * idx_stat * idx_lay2])
    fmri_layers.append(fmri_avg_trial[itcond][idx_win_map * idx_stat * idx_lay3])
    fmri_condition_layers.append(fmri_layers)

print("Number of voxels for layer 1: {}".format(np.sum(idx_win_map * idx_stat * idx_lay1)))
print("Number of voxels for layer 2: {}".format(np.sum(idx_win_map * idx_stat * idx_lay2)))
print("Number of voxels for layer 3: {}".format(np.sum(idx_win_map * idx_stat * idx_lay3)))

# Plot results
my_dpi = 96
fig, axes = plt.subplots(nrows=4, ncols=3, figsize=(1920/my_dpi, 1080/my_dpi),
                    dpi=my_dpi)
for itcond, cond in enumerate(CONDITIONS):
    for itlay in range(0,3):
        if cond == WINN_COND:
            axes[itcond, itlay].plot(np.mean(fmri_condition_layers[itcond][itlay], axis=0), 'r')
            axes[itcond, itlay].set_ylabel('fMRI time course')
            axes[itcond, itlay].set_xlabel('Repetition Time')
            axes[itcond, itlay].set_title('Layer: {}, Winn Cond: {}'.format(itlay+1, cond))
        else:
            axes[itcond, itlay].plot(np.mean(fmri_condition_layers[itcond][itlay], axis=0))
            axes[itcond, itlay].set_ylabel('fMRI time course')
            axes[itcond, itlay].set_xlabel('Repetition Time')
            axes[itcond, itlay].set_title('Layer: {}, Cond: {}'.format(itlay+1, cond))

# plt.suptitle('Winning condition: {}'.format(WINN_COND))
plt.tight_layout()
plt.savefig(os.path.join(PATH_OUT, 'plot_layers_time_{}.jpg'.format(WINN_COND)), bbox_inches = 'tight', dpi=my_dpi)

# Save numpy
np.save(os.path.join(PATH_OUT, 'layer_condition_fmr'), fmri_condition_layers, allow_pickle=True)
