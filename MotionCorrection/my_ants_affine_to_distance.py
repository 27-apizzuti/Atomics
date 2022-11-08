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
    
    #according to https://itk.org/Doxygen/html/classitk_1_1AffineTransform.html
    #the first 9 elementes are stored in row major order. This is the same
    #order used in C/C++ and Python (while R and MATLAB follow colmajor order)
    
    #See "Rigid Body Registration" (John Ashburner & Karl J. Friston) to have 
    #an explanation of how to select the parameters in the rotation matrix
    
    rot_y = np.arcsin(affine[2])
    cos_rot_y = np.cos(rot_y)
    rot_x = np.arctan2(affine[8] / cos_rot_y, affine[8] / cos_rot_y)
    rot_z = np.arctan2(affine[2] / cos_rot_y, affine[0] / cos_rot_y)

    if unit == 'deg':
        deg = np.degrees
        R = np.array([deg(rot_x), deg(rot_y), deg(rot_z)])
    if unit == 'rad':
        R = np.array([rot_x, rot_y, rot_z])

    T = np.array([dx, dy, dz])

    return T, R
