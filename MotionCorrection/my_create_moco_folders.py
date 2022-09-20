"""
Created on Wed Aug 22

This function create folder structure for moco output.

@author: apizz
"""
import os

def my_create_moco_folders(path_in_session):
    if not os.path.exists(os.path.join(path_in_session, 'orig')):
        os.mkdir(os.path.join(path_in_session, 'orig'))
        os.mkdir(os.path.join(path_in_session, 'warped'))
        os.mkdir(os.path.join(path_in_session, 'affine'))
        os.mkdir(os.path.join(path_in_session, 'motion_traces'))
