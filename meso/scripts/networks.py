# -*- coding: utf-8 -*-
"""
    meso.scripts.visualize
    ~~~~~~~

    Visualize dream3d microstructures.

    :copyright: (c) 2015 by Brian DeCost
    :license: MIT, see LICENSE for more details.
"""

import os
import h5py
import click
import numpy as np

import meso.io
import meso.network

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])
@click.command(context_settings=CONTEXT_SETTINGS)
@click.argument('snapshots', nargs=-1, type=click.Path(exists=True))
@click.option('-o', '--outfile', default='networks.h5', type=click.Path(exists=False), help='output file')
def networks(snapshots, outfile):
    """ Collect temporal network dataset.
    Store adjacency list in hdf5 datasets.
    """
    
    # touch file to ensure it exists, and is empty
    open(outfile, 'w').close()
    
    padwidth = len( str(len(snapshots)) )
    snapshots = sorted(snapshots)
    keys = ['snapshot{}'.format(str(i).zfill(padwidth)) for i in range(len(snapshots))]
    
    for key, snapshot in zip(keys, snapshots):
        grains = meso.io.load_dream3d(snapshot)
        network = meso.network.transgranular_network(grains)
        edges = np.array([list(edge) for edge in network.edges_iter()])
        with h5py.File(outfile, 'r+') as f:
            f[key] = edges

    return
