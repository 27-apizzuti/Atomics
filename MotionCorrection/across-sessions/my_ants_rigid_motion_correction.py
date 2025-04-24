"""
Created on Wed Aug 22

This function does rigid motion with ANTS.
It calls the following function:
    my_create_moco_folders.py
    my_ants_affine_to_distance.py


Run separately for Nulled and Not-nulled
e.g. path_out = 'MOCO/S1/single_run/runX'
Create output folder with subfolders.

Output:
    Folder structure:
        -orig (.nii.gz)
        -warped (.nii.gz)
        -matrix (.mat)
        -motion_traces (.csv)
    4D warped (.nii.gz)
    plot motion traces (.png)
    Frame-wise displacement (based on: https://github.com/ANTsX/ANTsPy/blob/c3986e269f5c6430922665a9c37930d454b44beb/ants/registration/interface.py#L846-L852)


@author: apizz
"""

import ants
import numpy as np
import nibabel as nb
import pandas as pd
import itertools
import nipype.interfaces.fsl as fsl
from my_create_moco_folders import *
from my_ants_affine_to_distance import *

def my_ants_rigid_motion_correction(path_out, path_mask, path_reference, path_moving4D):

    filename = path_moving4D.split('/')[-1]
    basename = filename.split(os.extsep, 1)[0]

    # // Create output folder structure
    print('...Create output folders')
    my_create_moco_folders(path_out)

    # // Loading files
    mask = ants.image_read(path_mask)
    reference = ants.image_read(path_reference)
    nii = nb.load(path_moving4D)
    mov = nii.get_fdata()
    print('...Loading done correctly')
    if len(np.shape(mov)) > 3:
        VOLS = np.shape(mov)[-1]

        # Define coordinates for FD
        coord = np.argwhere(mask > 0)  # (n. of voxels, 3 coordinates)
        x = coord[:, 0]
        y = coord[:, 1]
        z = coord[:, 2]
        d = {'x': x.transpose(), 'y': y.transpose(), 'z': z.transpose()}
        pts = pd.DataFrame(data=d)

        # Initiate output
        S_Tr = []; S_Rt = []
        Tr = []; Rt = []; data_warped = np.zeros(np.shape(mov));
        PTW = np.zeros([np.shape(x)[0], 3, VOLS])

        for itervol in range(VOLS):
            print('Volume {}'.format(itervol))
            myvol = mov[..., itervol]

            # Save individual volumes: this step is needed since ANTS registration input must be both ANTs object.
            img = nb.Nifti1Image(myvol, header=nii.header, affine=nii.affine)
            nb.save(img, os.path.join(path_out, 'orig', '{}_vol_{}.nii.gz'.format(basename, itervol)))
            print('...Save {} in {}'.format('{}_vol_{}.nii.gz'.format(basename, itervol), os.path.join(path_out, 'orig')))
            moving = ants.image_read(os.path.join(path_out, 'orig', '{}_vol_{}.nii.gz'.format(basename, itervol)))

            print('...Find trasformation matrix for {}, vol {}'.format(basename, itervol))
            mytx = ants.registration(fixed=reference, moving=moving, type_of_transform = 'Rigid', mask=mask)
            print('...Save transformation matrix')
            os.system(f"cp {mytx['fwdtransforms'][0]} {path_out}/affine/{basename}_vol_{itervol}_affine.mat")

            # // Find motion regressors (Tx, Ty, Tz [mm]; Rx, Ry, Rz [rad])
            localtxp = ants.read_transform(os.path.join(path_out, 'affine', '{}_vol_{}_affine.mat'.format(basename, itervol)))
            affine = localtxp.parameters
            print('...From affine to regression parameters')
            T, R = my_ants_affine_to_distance(affine, 'rad')
            Tr.append(T)
            Rt.append(R)

            # Store for FD
            ptsw = ants.apply_transforms_to_points(3, pts, mytx['fwdtransforms'])
            PTW[..., itervol] = ptsw

            # // Apply transformation
            mywarpedimage = ants.apply_transforms(fixed=reference, moving=moving, transformlist=mytx['fwdtransforms'], interpolator='bSpline')
            ants.image_write(mywarpedimage, os.path.join(path_out, 'warped', '{}_vol_{}_warped.nii.gz'.format(basename, itervol)))
            # Step needed to read the warped image
            nii2 = nb.load(os.path.join(path_out, 'warped', '{}_vol_{}_warped.nii.gz'.format(basename, itervol)))
            mywarp = nii2.get_fdata()
            data_warped[..., itervol] = mywarp

        # // Compute and save FD
        FDdiff = np.diff(PTW, axis=-1)
        FD = np.abs(FDdiff)
        FD = np.mean(FD, axis=0)
        FD = np.sum(FD, axis=0)

        # // Save motion traces intra-run as .csv
        Tr = np.asarray(Tr)
        Rt = np.asarray(Rt)
        FD = np.hstack((0, FD))

        print('...Save motion traces')
        data_dict = {
        'Tx': Tr[:, 0],
        'Ty': Tr[:, 1],
        'Tz': Tr[:, 2],
        'Rx': Rt[:, 0],
        'Ry': Rt[:, 1],
        'Rz': Rt[:, 2],
        'FD': FD}

        pd_ses = pd.DataFrame(data=data_dict)
        pd_ses.to_csv(os.path.join(path_out, 'motion_traces', '{}_motion.csv'.format(basename)), index=False)

        # // Save warped images as 4D array
        print('...Save Warped images')
        img = nb.Nifti1Image(data_warped, header=nii.header, affine=nii.affine)
        nb.save(img, os.path.join(path_out, '{}_warped.nii.gz'.format(basename)))
        print('Exit.')

        return(Tr, Rt, FD)
    else:
        moving = ants.image_read(path_moving4D)
        print('...Find trasformation matrix for {}'.format(basename))

        mytx = ants.registration(fixed=reference, moving=moving, type_of_transform = 'Rigid')
        print('...Save transformation matrix')
        os.system(f"cp {mytx['fwdtransforms'][0]} {path_out}/affine/{basename}_affine.mat")
        # // Find motion regressors (Tx, Ty, Tz [mm]; Rx, Ry, Rz [rad])
        localtxp = ants.read_transform(os.path.join(path_out, 'affine', '{}_affine.mat'.format(basename)))
        affine = localtxp.parameters
        print('...From affine to regression parameters')
        T, R = my_ants_affine_to_distance(affine, 'rad')

        print('...Save motion traces')
        data_dict = {
        'Tx': [T[0], 0],
        'Ty': [T[1], 0],
        'Tz': [T[2], 0],
        'Rx': [R[0], 0],
        'Ry': [R[1], 0],
        'Rz': [R[2], 0]}

        pd_ses = pd.DataFrame(data=data_dict)
        pd_ses.to_csv(os.path.join(path_out, 'motion_traces', '{}_motion.csv'.format(basename)), index=False)

        # // Apply transformation
        mywarpedimage = ants.apply_transforms(fixed=reference, moving=moving, transformlist=mytx['fwdtransforms'], interpolator='bSpline')
        ants.image_write(mywarpedimage, os.path.join(path_out, 'warped', '{}_warped.nii.gz'.format(basename)))
