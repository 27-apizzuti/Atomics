"""
Created on Wed Aug 22

This function compute motion traces from an affine matrix only for rigid transformation.

Traslation [mm], Rotation [rad. or in deg.]

Baed on: https://github.com/ANTsX/ANTsR/blob/69d65b697b14af6f2edf9fbd096a84c5fbc4d944/R/antsrMotionCalculation.R#L171-L189

@author: apizz
"""
import ants
import numpy as np

def my_ants_affine_to_distance(affine, unit):

    dx, dy, dz = affine[9:]

    rot_x = np.arcsin(affine[6])
    cos_rot_x = np.cos(rot_x)
    rot_y = np.arctan2(affine[7] / cos_rot_x, affine[8] / cos_rot_x)
    rot_z = np.arctan2(affine[3] / cos_rot_x, affine[0] / cos_rot_x)

    if unit == 'deg':
        deg = np.degrees
        R = np.array([deg(rot_x), deg(rot_y), deg(rot_z)])
    if unit == 'rad':
        R = np.array([rot_x, rot_y, rot_z])

    T = np.array([dx, dy, dz])

    return T, R
