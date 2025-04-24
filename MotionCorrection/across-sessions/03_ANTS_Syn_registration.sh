#!/bin/bash
# Non Linear Coregistration (Syn, by ANTs)
#
# Input files: 1. Target, 2. Source 3. initial_matrix_ITK.txt (manual+rigid+affine, by ITK-SNAP) 4. mask.nii around ROI
# # No mask option used for P04 and P03, P02
echo "I expect 2 filed: target file (e.g. high-res T1w from VASO) and a moving (or source) file"
echo " Co-registration-part II: Source to Target ----> Syn [ANTs]"

ITK_GLOBAL_DEFAULT_NUMBER_OF_THREADS=8
export ITK_GLOBAL_DEFAULT_NUMBER_OF_THREADS

# Define input
SUBJ=sub-03
STUDY_PATH=/mnt/d/Pilot_MQ_VASO/MRI_MQ
SESS=3
MOD=not_nulled

PATH_OUT=${STUDY_PATH}/${SUBJ}/derivatives/func/MQ/vaso_analysis/moco/AcrossSess/sess-${SESS}
if [ ! -d ${PATH_OUT} ]; then
  mkdir -p ${PATH_OUT};
fi

# Not-nulled
# Reference session-1
TASK_REF=ambig
SESS_1_REF=0   # For P-04, P-05, P-06, P-07 ref. 2; Only for P-03 is 0 (AMB)
# Reference session-n (moving)
TASK_REF_SE=unamb
GLOB_REF=10  # session to co-register

# // Reference for session 1
myTarget=${STUDY_PATH}/${SUBJ}/derivatives/func/MQ/vaso_analysis/moco/sess-1/singleRun/run-${SESS_1_REF}/${SUBJ}_sess-1_task-${TASK_REF}_acq-3dvaso_run-01_not_nulled_reference.nii.gz
# // Insert global reference for the session 2 (or 3, 4)
myMoving=${STUDY_PATH}/${SUBJ}/derivatives/func/MQ/vaso_analysis/moco/sess-${SESS}/singleRun/run-${GLOB_REF}/${SUBJ}_sess-${SESS}_task-${TASK_REF_SE}_acq-3dvaso_run-01_not_nulled_reference.nii.gz
# //
myMatrix=${STUDY_PATH}/${SUBJ}/derivatives/func/MQ/vaso_analysis/moco/sess-${SESS}/initial_matrix_ITK.txt
#
# Coregistration done in 2 steps
echo "*****************************************"
echo "************* starting with ANTS ********"
echo "*****************************************"

antsRegistration \
--verbose 1 \
--dimensionality 3 \
--float 1 \
--output [${PATH_OUT}/${MOD}_registered_,${PATH_OUT}/${MOD}_registered_Warped.nii.gz,${PATH_OUT}/${MOD}_registered_InverseWarped.nii.gz] \
--interpolation BSpline[5] \
--use-histogram-matching 0 \
--winsorize-image-intensities [0.005,0.995] \
--transform Rigid[0.05] \
--metric MI[${myTarget},${myMoving},0.7,32,Regular,0.1] \
--convergence [1000x500,1e-6,10] \
--shrink-factors 2x1 \
--smoothing-sigmas 1x0vox \
--transform Affine[0.1] \
--metric MI[${myTarget},${myMoving},0.7,32,Regular,0.1] \
--convergence [1000x500,1e-6,10] \
--shrink-factors 2x1 \
--smoothing-sigmas 1x0vox \
--initial-moving-transform ${myMatrix} \
--transform SyN[0.1,2,0] \
--metric CC[${myTarget},${myMoving},1,2] \
--convergence [500x100,1e-6,10] \
--shrink-factors 2x1 \
--smoothing-sigmas 1x0vox


# Apply trx
antsApplyTransforms -d 3 -i ${myMoving} \
-o $PATH_OUT/${SUBJ}_${MOD}_sess${SESS}_to_sess1_warped.nii -r ${myTarget} -t ${PATH_OUT}/${MOD}_registered_1Warp.nii.gz -t ${PATH_OUT}/${MOD}_registered_0GenericAffine.mat
# -----------------------------------------------------------------------------
# Nulled
MOD=nulled
TASK_REF=ambig
SESS_1_REF=1
TASK_REF_SE=unamb
GLOB_REF=11

# // Reference for session 1
myTarget=${STUDY_PATH}/${SUBJ}/derivatives/func/MQ/vaso_analysis/moco/sess-1/singleRun/run-${SESS_1_REF}/${SUBJ}_sess-1_task-${TASK_REF}_acq-3dvaso_run-01_nulled_reference.nii.gz
# // Insert global reference for the session that has to be registered to the first session
myMoving=${STUDY_PATH}/${SUBJ}/derivatives/func/MQ/vaso_analysis/moco/sess-${SESS}/singleRun/run-${GLOB_REF}/${SUBJ}_sess-${SESS}_task-${TASK_REF_SE}_acq-3dvaso_run-01_nulled_reference.nii.gz
# //
myMatrix=${STUDY_PATH}/${SUBJ}/derivatives/func/MQ/vaso_analysis/moco/sess-${SESS}/initial_matrix_ITK.txt

# Coregistration done in 2 steps
echo "*****************************************"
echo "************* starting with ANTS ********"
echo "*****************************************"

antsRegistration \
--verbose 1 \
--dimensionality 3 \
--float 1 \
--output [${PATH_OUT}/${MOD}_registered_,${PATH_OUT}/${MOD}_registered_Warped.nii.gz,${PATH_OUT}/${MOD}_registered_InverseWarped.nii.gz] \
--interpolation BSpline[5] \
--use-histogram-matching 0 \
--winsorize-image-intensities [0.005,0.995] \
--transform Rigid[0.05] \
--metric MI[${myTarget},${myMoving},0.7,32,Regular,0.1] \
--convergence [1000x500,1e-6,10] \
--shrink-factors 2x1 \
--smoothing-sigmas 1x0vox \
--transform Affine[0.1] \
--metric MI[${myTarget},${myMoving},0.7,32,Regular,0.1] \
--convergence [1000x500,1e-6,10] \
--shrink-factors 2x1 \
--smoothing-sigmas 1x0vox \
--initial-moving-transform ${myMatrix} \
--transform SyN[0.1,2,0] \
--metric CC[${myTarget},${myMoving},1,2] \
--convergence [500x100,1e-6,10] \
--shrink-factors 2x1 \
--smoothing-sigmas 1x0vox

# Apply trx
antsApplyTransforms -d 3 -i ${myMoving} \
-o $PATH_OUT/${SUBJ}_${MOD}_sess${SESS}_to_sess1_warped.nii -r ${myTarget} -t ${PATH_OUT}/${MOD}_registered_1Warp.nii.gz -t ${PATH_OUT}/${MOD}_registered_0GenericAffine.mat
