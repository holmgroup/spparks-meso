# -*- coding: utf-8 -*-
"""
    meso.io
    ~~~~~~~

    This module provides simple HDF5 i/o routines for DREAM3D microstructures

    :copyright: (c) 2015 by Brian DeCost
    :license: MIT, see LICENSE for more details.
"""

import numpy as np
import h5py

DATA_PATH = 'DataContainers/SyntheticVolume'
GRAIN_ID_PATH = DATA_PATH + '/CellData/FeatureIds'
QUAT_PATH = DATA_PATH + '/CellFeatureData/AvgQuats'
DIM_PATH = DATA_PATH+'/DIMENSIONS'

def load_dream3d(path, renumber_grains=False):
    with h5py.File(path, 'r') as f:
        grain_ids = np.array(f[GRAIN_ID_PATH], dtype=np.int)
    shape = tuple([s for s in grain_ids.shape if s > 1])
    if renumber_grains:
        grain_ids = renumber(grain_ids)
    return grain_ids.reshape(shape)


def renumber(grains, start_from=1):
    grain_ids = np.unique(grains)
    new_grains = np.zeros_like(grains)
    for idx, grain_id in enumerate(grain_ids):
        new_grains[grains == grain_id] = idx+start_from
    return new_grains


def save_dream3d(path, grains, quaternions):
    with h5py.File(path, 'w') as f:
        f.attrs['FileVersion'] = np.string_('6.0\x00')
        f[GRAIN_ID_PATH] = grains
        f[QUAT_PATH] = quaternions
        f[DIM_PATH] = np.array([s for s in grains.shape])
    return


def add_attribute(path, attr_name, attr):
    with h5py.File(path, 'r+') as f:
        f.attrs[attr_name] = attr
    return


def load_quaternions(path):
    with h5py.File(path, 'r') as f:
        quaternions = np.array(f[QUAT_PATH], dtype=np.float32)
    return quaternions

def get_dimensionality(path):
    with h5py.File(path, 'r') as f:
        shape = f[GRAIN_ID_PATH].shape
        return len(shape)

def dream3d_to_sites(dream3d_path, sites_path):
    """ convert DREAM3D microstructure to SPPARKS sites format """
    grains = load_dream3d(dream3d_path)
    with open(sites_path, 'w') as f:
        print('# SPPARKS sites file', file=f)
        print('{} dimension'.format(grains.ndim), file=f)
        print('{} sites'.format(grains.size), file=f)
        print('0 {} xlo xhi'.format(grains.shape[0]), file=f)
        print('0 {} ylo yhi'.format(grains.shape[1]), file=f)
        print('-.5 .5 zlo zhi', file=f)
        print('', file=f)
        print('Values', file=f)
        print('', file=f) # empty line is not optional
        for (index,), site in np.ndenumerate(grains.flatten()):
            print('{} {}'.format(index+1, site), file=f)
        return
