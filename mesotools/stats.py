# -*- coding: utf-8 -*-
"""
    mesotools.stats
    ~~~~~~~~~~~~~~~~~

    This module provides tools for analyzing grain growth simulations.

    :copyright: (c) 2015 by Brian DeCost
    :license: MIT, see LICENSE for more details.
"""

import h5py
import numpy as np

def grainvolume(stats_path):
    """ Get time and volume dataset from a stats files """
    with h5py.File(stats_path, 'r') as f:
        time = f['time'][...]
        volume = f['grainsize'][...]
        return time, volume

        
def normalized_size(stats_path, ndim=2, recompute=False):
    """ Get normalized grain size dataset """
    try:
        if recompute:
            raise KeyError
        with h5py.File(stats_path) as f:
            return f['time'][...], f['normgrainsize'][...]
    except KeyError:
        time, volume = grainvolume(stats_path)
        radius = np.power(volume, 1.0/ndim)

        # compute mean across rows, excluding zero entries:
        mean_radius = np.sum(radius, axis=1) / np.sum(radius != 0, axis=1)
        normed_radius = radius / mean_radius[:,np.newaxis]
        
        with h5py.File(stats_path) as f:
            try:
                del f['normgrainsize']
            except KeyError:
                pass
            f['normgrainsize'] = normed_radius
        return time, normed_radius
