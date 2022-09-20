"""
Created on Wed Aug 22

This function plots motion traces.

@author: apizz
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import ants

def my_plot_motion(OUT_PATH, path_csv1):
    motion = pd.read_csv(path_csv1)
    filename = path_csv1.split('/')[-1]
    basename = filename.split(os.extsep, 1)[0]

    my_dpi = 96
    fig, axes = plt.subplots(nrows=3, ncols=1, figsize=(1920/my_dpi, 1080/my_dpi),
                        dpi=my_dpi)

    axes[0].plot(motion['Tx'], label='Tx')
    axes[0].plot(motion['Ty'], label='Ty')
    axes[0].plot(motion['Tz'], label='Tz')
    axes[0].set_ylabel('Traslation [mm]')
    axes[0].set_xlabel('Volumes')
    axes[0].legend(loc="upper right")


    axes[1].plot(motion['Rx'], label='Rx')
    axes[1].plot(motion['Ry'], label='Ry')
    axes[1].plot(motion['Rz'], label='Rz')
    axes[1].set_ylabel('Rotation [rad]')
    axes[1].set_xlabel('Volumes')
    axes[1].legend(loc="upper right")

    axes[2].plot(motion['FD'], label='FD')
    axes[2].axhline(y=0.3, xmin=0, xmax=3, c="red",linewidth=0.5,zorder=0)
    axes[2].set_ylabel('Frame-wise displacement')
    axes[2].set_xlabel('Volumes')
    axes[2].legend(loc="upper right")

    plt.suptitle('{}'.format(basename))
    plt.tight_layout()
    plt.savefig(os.path.join(OUT_PATH, 'plot_motion.jpg'), bbox_inches = 'tight', dpi=my_dpi)

    print('Plot done.')
