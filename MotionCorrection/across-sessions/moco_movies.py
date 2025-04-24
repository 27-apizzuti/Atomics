"""
Created on Mon Oct 17 12:41:45 2022

Credit to Sebastian Dresbach
# execute with python3 videoThroughSlicesRenzo.py 'BOLD.nii' 6

from here: https://raw.githubusercontent.com/layerfMRI/repository/master/videoThroughSlicesRenzo.py

@author: apizz
"""
import nibabel as nb
import numpy as np
import imageio
import scipy
from scipy import ndimage
import os
import sys
import glob

STUDY_PATH = "D:\\Pilot_MQ_VASO\\MRI_MQ"
SUB = "sub-07"
PATH_IN = "D:\\Pilot_MQ_VASO\\MRI_MQ\\sub-07\\derivatives\\func\\MQ\\vaso_analysis\\Physical\\boco\\AllSessions"
FILE_IN = "{}_task-unamb_acq-3dvaso_run-avg_BOLD_interp".format(SUB)

dumpFolder = os.path.join(PATH_IN, 'moco_movie')

if not os.path.exists(dumpFolder):
    os.mkdir(dumpFolder)

dataArr = nb.load(os.path.join(PATH_IN, '{}.nii.gz'.format(FILE_IN))).get_fdata()
sliceNr = 16
globalMax = 300
globalMin = 0

for frame in range(dataArr.shape[3]):
    imgData = dataArr[:,:,int(sliceNr),frame]
    rotated_img = ndimage.rotate(imgData, 90)

    # if np.amin(rotated_img) <= globalMin:
    #     globalMin = np.amin(rotated_img)
    # if np.amax(rotated_img) >= globalMax:
    #     globalMax = np.amax(rotated_img)
        # // change the maxium with 75 percentile

for frame in range(dataArr.shape[3]):
    imgData = dataArr[:,:,int(sliceNr),frame]
    rotated_img = ndimage.rotate(imgData, 90)


    rotated_img[0,0] = globalMax
    rotated_img[0,1] = globalMin

    rotated_img = (rotated_img - globalMin)/ (globalMax-globalMin)
    rotated_img = rotated_img.astype(np.float64)  # normalize the data to 0 - 1
    rotated_img = 255 * rotated_img # Now scale by 255
    img = rotated_img.astype(np.uint8)

    imageio.imwrite(os.path.join('{}'.format(dumpFolder), 'frame{}.png'.format(frame)), img)


files = sorted(glob.glob(dumpFolder + '/*.png'))
print('Creating gif from {} images'.format(len(files)))
images = []
for file in files:
    filedata = imageio.imread(file)
    images.append(filedata)

imageio.mimsave(os.path.join(PATH_IN, '{}_movie.gif'.format(FILE_IN)), images, duration = 1/10)

writer = imageio.get_writer(os.path.join(PATH_IN, '{}_movie.mp4'.format(FILE_IN)), fps=10)
# Increase the fps to 24 or 30 or 60

for file in files:
    filedata = imageio.imread(file)
    writer.append_data(filedata)
writer.close()
print('Deleting dump directory')
os.system(f'rm -r {dumpFolder}')
print('Done.')
