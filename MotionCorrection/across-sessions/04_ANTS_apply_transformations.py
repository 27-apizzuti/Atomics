"""
Created on Mon 29 Aug

Apply multiple transformation matrices at once
for motion correction

@author: apizz
"""
# Import libraries
import ants
import numpy as np
import nibabel as nb
import os
import glob

print("****Apply transformation all at once****")

# Define inputs
STUDY_PATH = "/mnt/d/Pilot_MQ_VASO/MRI_MQ/"
SUBJ = ['sub-03']
SESS = ['1', '2']

for itersu, su in enumerate(SUBJ):

    for iterse, se in enumerate(SESS):
        PATH_IN = os.path.join(STUDY_PATH, su, 'derivatives', 'func', 'MQ', 'vaso_analysis', 'moco')
        os.chdir(os.path.join(PATH_IN, 'sess-{}'.format(se), 'singleRun'))
        RUNS = glob.glob("*")
        print(RUNS)

        for iterru , ru in enumerate(RUNS):
            print('Working on {}, {}, {}'.format(su, se, ru))

            if (se == '1') & (len(os.listdir(os.path.join(PATH_IN, 'sess-{}'.format(se), 'AcrossRuns', ru))) == 0):
                print('Directory empty')

            else:
                print('Directory not empty')
                os.chdir(os.path.join(PATH_IN, 'sess-{}'.format(se), 'singleRun', ru, 'orig'))
                VOLS = glob.glob("*")

                # Create output folder
                PATH_OUT = os.path.join(PATH_IN, 'sess-{}'.format(se), 'singleRun', ru, 'final_warp')
                if not os.path.exists(PATH_OUT):
                    os.mkdir(PATH_OUT)

                # // Input
                # reference (one volume)
                basename = VOLS[0].split(os.extsep, 1)[0]
                mod = basename.split('_')
                rootname = str()
                for i, k in enumerate(mod[:-2]):
                    if i > 0:
                        rootname = '{}_{}'.format(rootname, k)
                    else:
                        rootname = '{}'.format(k)
                print(rootname)

                if len(mod) > 7:  # not nulled
                    ref = os.path.join(PATH_IN, 'sess-1', 'singleRun', 'run-0', '{}_sess-1_task-ambig_acq-3dvaso_run-01_not_nulled_reference.nii.gz'.format(su))
                    aff = 'not_nulled_registered_0GenericAffine.mat'.format(se)
                    syn = 'not_nulled_registered_1Warp.nii.gz'.format(se)
                else:
                    ref = os.path.join(PATH_IN, 'sess-1', 'singleRun', 'run-1', '{}_sess-1_task-ambig_acq-3dvaso_run-01_nulled_reference.nii.gz'.format(su))
                    aff = 'nulled_registered_0GenericAffine.mat'.format(se)
                    syn = 'nulled_registered_1Warp.nii.gz'.format(se)

                # Find dimensions
                nii = nb.load(ref)
                data = nii.get_fdata()
                dims = np.shape(data)

                warped = np.zeros([dims[0], dims[1], dims[2], len(VOLS)])
                for itervol, vol in enumerate(VOLS):

                    # // reference
                    reference = ants.image_read(ref)

                    # // Input
                    # moving (one volume)
                    moving = ants.image_read(os.path.join(PATH_IN, 'sess-{}'.format(se), 'singleRun', ru, 'orig', '{}_vol_{}.nii.gz'.format(rootname, itervol)))
                    print(os.path.join(PATH_IN, 'sess-{}'.format(se), 'singleRun', ru, 'orig', '{}_vol_{}.nii.gz'.format(rootname, itervol)))

                    # TRX 1 (within run)
                    path_trx1 = os.path.join(PATH_IN, 'sess-{}'.format(se), 'singleRun',  ru, 'affine')
                    os.chdir(path_trx1)
                    filename = glob.glob('*_vol_{}_affine.mat'.format(itervol))
                    TRX1 = os.path.join(path_trx1, filename[0])
                    print(filename[0])

                    if (len(os.listdir(os.path.join(PATH_IN, 'sess-{}'.format(se), 'AcrossRuns', ru))) == 0):
                        # Apply only syn + Within
                        print('Apply within + across sess')
                        path_trx3 = os.path.join(PATH_IN, 'AcrossSess', 'sess-{}'.format(se))
                        AFF = os.path.join(path_trx3, aff)
                        SYN = os.path.join(path_trx3, syn)
                        # // Apply multiple transformation matrices
                        mywarpedimage = ants.apply_transforms(fixed=reference, moving=moving, transformlist=[SYN, AFF, TRX1], interpolator='bSpline')
                        ants.image_write(mywarpedimage, os.path.join(PATH_OUT, '{}_vol_{}_moco.nii.gz'.format(rootname, itervol)))

                    else:
                        # Find across runs matrix
                        # TRX 2 (across runs)
                        path_trx2 = os.path.join(PATH_IN, 'sess-{}'.format(se), 'AcrossRuns', ru, 'affine')
                        os.chdir(path_trx2)
                        filename = glob.glob('*affine.mat')
                        TRX2 = os.path.join(path_trx2, filename[0])
                        print(filename[0])

                        if (se == '1'):
                            # // Apply multiple transformation matrices
                            # // Apply transformation
                            print('Apply series of trx to {}'.format(itervol))
                            mywarpedimage = ants.apply_transforms(fixed=reference, moving=moving, transformlist=[TRX2, TRX1], interpolator='bSpline')
                            print('Saving {}'.format(itervol))
                            ants.image_write(mywarpedimage, os.path.join(PATH_OUT, '{}_vol_{}_moco.nii.gz'.format(rootname, itervol)))

                        else:
                            # TRX 3 (across session)
                            path_trx3 = os.path.join(PATH_IN, 'AcrossSess', 'sess-{}'.format(se))
                            AFF = os.path.join(path_trx3, aff)
                            SYN = os.path.join(path_trx3, syn)

                            # // Apply multiple transformation matrices
                            mywarpedimage = ants.apply_transforms(fixed=reference, moving=moving, transformlist=[SYN, AFF, TRX2, TRX1], interpolator='bSpline')
                            ants.image_write(mywarpedimage, os.path.join(PATH_OUT, '{}_vol_{}_moco.nii.gz'.format(rootname, itervol)))


                    # Step needed to read the warped image
                    nii2 = nb.load(os.path.join(PATH_OUT, '{}_vol_{}_moco.nii.gz'.format(rootname, itervol)))
                    mywarp = nii2.get_fdata()
                    warped[..., itervol] = mywarp

                # Save final warped time series
                img = nb.Nifti1Image(warped, header=nii2.header, affine=nii2.affine)
                warped_moco = os.path.join(PATH_IN, 'sess-{}'.format(se), 'singleRun', ru, '{}_moco.nii.gz'.format(rootname))
                nb.save(img, warped_moco)
