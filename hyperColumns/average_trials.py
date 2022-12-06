"""
Created on Fri Nov  4 10:31:55 2022

@author: apizz
"""

import bvbabel as bv
import nibabel as nb
import numpy as np
import pprint
import os


def my_average_trials(path_to_4D_nifti, path_to_protol_file, path_out, condition='Baseline', res='TR', TR=1000, window=1):

    # Extract basename
    filename = os.path.split(path_to_4D_nifti)[-1]
    basename = filename.split(os.extsep, 1)[0]

    # // Load input file
    nii = nb.load(path_to_4D_nifti)
    nii_data = np.asarray(nii.dataobj)
    dims = np.shape(nii_data)

    # // Load protocol
    header, data = bv.prt.read_prt(path_to_protol_file)

    # // Find the input condition in the protocol file
    my_cond = []
    for d in data:
        cond = d['NameOfCondition']
        if cond == condition:
            my_cond.append(d)
    if len(my_cond) == 0:
        print('Condition not found in the protocol file.\n')
        print('Protocol file:\n')
        pprint.pprint(data)
    else:
        pass

    # // Execute
    if (len(my_cond) > 0):
        my_cond = my_cond[0]
        nrep = my_cond['NrOfOccurances']
        print('The condition {} occurred {} times'.format(condition, nrep))

        if (res == 'TR'):
            time_start = np.int16(my_cond['Time start'])
            time_stop = np.int16(my_cond['Time stop'])
        else:
            print('Millisecond protol. Input TR: {}'.format(TR))
            time_start = np.int16(np.ceil(my_cond['Time start']/TR)) + 1    # (arrotondo per eccesso-CEIL)
            time_stop = np.int16(np.floor(my_cond['Time stop']/TR))  + 1   # (arrotondo per difetto-FLOOR)

        # Concatenate trials
        trials = []
        durations = np.zeros(nrep)

        for it in range(nrep):

            trials.append(nii_data[..., time_start[it]-1:time_stop[it]])
            durations[it] = np.shape(nii_data[..., time_start[it]-1:time_stop[it]])[-1]

        if np.all(durations == durations[0]):
            print('All trials have the same lenght')
            trials_array = np.asarray(trials)
            dims = np.shape(trials_array)

            # Find the axis where the trials are concatenated
            for it, d in enumerate(dims):
                if d == nrep:
                    conc_axis = it

            # Compute average
            trials_avg = np.mean(trials_array, axis=conc_axis)

        else:

            # // Trials have different lenghts
            idx = (durations == window) | (durations > window)
            print('Average of {} trials with lenght {} out of {} total trials.'.format(np.sum(idx), window, nrep))
            trials_array = np.zeros([np.sum(idx), dims[0], dims[1], dims[2], window])
            idx2 = np.argwhere(idx)
            for it, pos in enumerate(idx2):
                trials_array[it] = trials[pos[0]][..., 0:window]

            # Compute average
            trials_avg = np.mean(trials_array, axis=0)


        # Save output 4D nifti
        img = nb.Nifti1Image(trials_avg, header=nii.header, affine=nii.affine)
        path_out_file = os.path.join(path_out, '{}_{}_trials_avg.nii.gz'.format(basename, condition))
        nb.save(img, path_out_file)

        print('Output file is stored here: {}'.format(path_out_file))
        print('Finished.')

    else:
        pass

    return path_out_file
