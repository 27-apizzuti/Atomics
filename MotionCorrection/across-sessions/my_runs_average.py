"""
Created on Mon 29 Aug

This function compute run avarages. It takes as input a list of path.

@author: apizz
"""
import os
import numpy as np
import nibabel as nb
import time

def my_runs_average(list_of_path, path_out):
    print('Intial list: {}'.format(list_of_path))
    n_files = len(list_of_path)

    basename = list_of_path[0].split(os.extsep, 1)[0]
    temp = basename.split('/')[-1]
    mod = temp.split('_')
    print(mod)
    root = '{}_{}_{}_run-avg'.format(mod[0], mod[2], mod[3])
    if len(mod) > 7:
        outputname = '{}_not_nulled_moco'.format(root)
    else:
        outputname = '{}_nulled_moco'.format(root)

    print(outputname)
    # Counting reading time
    t0 = time.time()

    for it in range(n_files):
        nii = nb.load(list_of_path[it])
        data = nii.get_fdata()
        t1 = time.time()
        print('Reading time: {}'.format(t1-t0))
        if it == 0:
            dims = np.shape(data)
            new_data = np.zeros([dims[0], dims[1], dims[2], dims[3]])

        new_data += data
        t2 = time.time()
        print('Filling 5D array time: {}'.format(t2-t1))

    data_avg = new_data / n_files
    t3 = time.time()
    print('Averag time: {}'.format(t3-t2))

    # Save average time series
    img = nb.Nifti1Image(data_avg, header=nii.header, affine=nii.affine)
    avg_moco = os.path.join(path_out, '{}.nii.gz'.format(outputname))
    nb.save(img, avg_moco)
