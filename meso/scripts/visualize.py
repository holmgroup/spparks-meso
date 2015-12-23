# -*- coding: utf-8 -*-
"""
    meso.scripts.visualize
    ~~~~~~~

    Visualize dream3d microstructures.

    :copyright: (c) 2015 by Brian DeCost
    :license: MIT, see LICENSE for more details.
"""

import os
import click
import subprocess
import numpy as np
import matplotlib.pyplot as plt
from skimage.segmentation import mark_boundaries

import meso.io
from meso.binary import colors

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])
@click.command(context_settings=CONTEXT_SETTINGS)
@click.argument('infile', type=click.Path(exists=True))
@click.option('-o', '--outfile', default='', type=click.Path(), help='output file')
@click.option('-c', '--colors', default='none', type=click.Choice(['none', 'binary', 'quaternion']))
@click.option('-d', '--display', is_flag=True, help='show the microstructure in an X window')
def draw(infile, outfile, colors, display):
    """ Draw a 2D microstructure from the Dream3d INFILE"""

    grains = meso.io.load_dream3d(infile)
    quats = meso.io.load_quaternions(infile)

    if colors == 'none':
        im = grains / np.max(grains)
    elif colors == 'binary':
        im = meso.binary.colors(grains, quats)
    elif colors == 'quaternion':
        raise NotImplementedError('quaternion color scheme not yet implemented')
    
    im = mark_boundaries(im, grains, color=[0,0,0])
    plt.imshow(im, interpolation='none', origin='lower')

    if outfile is not '':
        plt.savefig(outfile)
    if display:
        plt.show()
    return

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])
@click.command(context_settings=CONTEXT_SETTINGS)
@click.argument('snapshots', nargs=-1, type=click.Path(exists=True))
@click.option('-i', '--initial', type=click.Path(exists=True))
@click.option('-o', '--outfile', default='grains.mov', type=click.Path(), help='output file')
@click.option('-c', '--colors', default='none', type=click.Choice(['none', 'binary', 'quaternion']))
def animate(snapshots, initial, outfile, colors):
    """ Animate a 2D grain growth simulation.
    Sorted file names should indicate temporal ordering. 
    """

    # get quaternions from the simulation input file
    quats = meso.io.load_quaternions(initial)

    tmpdir = 'temp'
    try:
        os.mkdir(tmpdir)
    except FileExistsError:
        pass

    padwidth = len( str(len(snapshots)) )
    snapshots = sorted(snapshots)
    
    def im_path(index, tmpdir, padwidth):
        key = str(index).zfill(padwidth)
        return os.path.join(tmpdir, 'snapshot{}.png'.format(key))

    png_paths = [im_path(idx, tmpdir, padwidth) for idx in range(len(snapshots))]
    
    for snapshot, png in zip(snapshots, png_paths):
        print('processing {}'.format(snapshot))
        grains = meso.io.load_dream3d(snapshot)
        if colors == 'none':
            im = grains / np.max(grains)
        elif colors == 'binary':
            im = meso.binary.colors(grains, quats)
        elif colors == 'quaternion':
            raise NotImplementedError('quaternion color scheme not yet implemented')
    
        im = mark_boundaries(im, grains, color=[0,0,0])
        plt.imshow(im, interpolation='none', origin='lower')
        plt.savefig(png)
        plt.clf()

    snapstring = os.path.join(tmpdir, 'snapshot%0{}d.png'.format(padwidth))
    subprocess.call(['ffmpeg', '-i', snapstring, '-codec', 'png', outfile])
    return
