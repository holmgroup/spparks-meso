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
from skimage.segmentation import mark_boundaries, find_boundaries

import meso.io
from meso.binary import colors


def render_microstructure(infile, initial=None, colorscheme='none'):
    grains = meso.io.load_dream3d(infile)
    if colorscheme == 'none':
        im = grains / np.max(grains)
        im = mark_boundaries(im, grains, color=[0,0,0])
    elif colorscheme == 'boundaries':
        plt.gray()
        im = np.ones_like(grains)
        boundaries = find_boundaries(grains)
        im[boundaries] = 0
    elif colorscheme == 'binary':
        quats = meso.io.load_quaternions(initial)
        im = meso.binary.colors(grains, quats)
        im = mark_boundaries(im, grains, color=[0,0,0])
    elif colorscheme == 'quaternion':
        quats = meso.io.load_quaternions(initial)
        raise NotImplementedError('quaternion color scheme not yet implemented')
    elif colorscheme == 'discrete':
        texture_components = meso.io.load_colors(initial)
        cmap = {idx: c for idx, c in enumerate(np.unique(texture_components))}
        im = np.zeros_like(grains)
        for grain_idx in np.unique(grains):
            im[grains == grain_idx] = cmap[texture_components[grain_idx]]
        boundaries = find_boundaries(grains)
        im[boundaries] = -6

    return im

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])
@click.command(context_settings=CONTEXT_SETTINGS)
@click.argument('infile', type=click.Path(exists=True))
@click.option('-i', '--initial', type=click.Path(exists=True), default=None)
@click.option('-o', '--outfile', default='', type=click.Path(), help='output file')
@click.option('-c', '--colorscheme', default='none', type=click.Choice(['none', 'boundaries', 'binary', 'quaternion', 'discrete']))
@click.option('--display/--no-display', default=True, help='show the microstructure in an X window')
def draw(infile, initial, outfile, colorscheme, display):
    """ Draw a 2D microstructure from the Dream3d INFILE"""

    if initial is None:
        initial = infile
    
    im = render_microstructure(infile, initial=initial, colorscheme=colorscheme)
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
@click.option('-c', '--colorscheme', default='none', type=click.Choice(['none', 'boundaries', 'binary', 'quaternion', 'discrete']))
def animate(snapshots, initial, outfile, colorscheme):
    """ Animate a 2D grain growth simulation.
    Sorted file names should indicate temporal ordering. 
    """
    # keep consistent color scheme across frames during animation
    vmin, vmax = None, None

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
        im = render_microstructure(snapshot, initial=initial, colorscheme=colorscheme)
        
        if colorscheme == 'discrete' or colorscheme == 'none' and vmin is None:
            vmin = np.min(im)
            vmax = np.max(im)
        
        plt.imshow(im, interpolation='none', origin='lower', vmin=vmin, vmax=vmax)
        plt.savefig(png)
        plt.clf()

    snapstring = os.path.join(tmpdir, 'snapshot%0{}d.png'.format(padwidth))
    subprocess.call(['ffmpeg', '-i', snapstring, '-codec', 'png', outfile])
    return
