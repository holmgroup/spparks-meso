# -*- coding: utf-8 -*-
"""
    meso.scripts.candidate
    ~~~~~~~

    Set up a dream3d microstructure for a binary texture AGG simulation.

    :copyright: (c) 2015 by Brian DeCost
    :license: MIT, see LICENSE for more details.
"""

import click
import numpy as np

import meso.io
from meso.binary import random_binary_texture


def equivalent_grain_radius(grains):
    """ calculate average grain size by summing over unique grain_id values """
    ids = np.unique(grains) # np.unique returns sorted values
    d = grains.ndim
    f = 1/np.pi if d == 2 else 3/(4*np.pi)
    r = [np.power(f*np.sum(grains==id),1/d) for id in ids]
    return np.mean(r)

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])
@click.command(context_settings=CONTEXT_SETTINGS)
@click.argument('infile', type=click.Path(exists=True))
@click.option('-o', '--outfile', default='initial_candidate.dream3d', type=click.Path(), help='output file')
@click.option('-s', '--size', default=0, type=float, help='specify relative candidate grain size')
@click.option('-r', '--redprob', default=0.3, type=float, help='fraction of red type grains')
@click.option('--randomize', is_flag=True,
              help='randomly choose the fraction of red type grains on the interval Uniform(0,redprob)')
def bigcandidate(infile, outfile, size, redprob, randomize):
    """ embed a candidate grain of size greater than size_cutoff
        in a matrix with red_probability fraction of red-type matrix grains """

    grain_ids = meso.io.load_dream3d(infile)

    #renumber grains, leaving 1 for the candidate grain
    candidate_grain_id = 1
    grain_ids = meso.io.renumber(grain_ids, start_from=2)


    # make the candidate grain ${size} times bigger than the average grain
    candidate_radius = size * equivalent_grain_radius(grain_ids)
    print(candidate_radius)
    
    # create a spherical mask...
    s = np.array(grain_ids.shape) / 2
    if grain_ids.ndim == 3:        
        z,y,x = np.ogrid[-s[0]:s[0], -s[1]:s[1], -s[2]:s[2]]
        mask = z*z + y*y + x*x < candidate_radius*candidate_radius
    if grain_ids.ndim == 2:        
        y,x = np.ogrid[-s[0]:s[0], -s[1]:s[1]]
        mask = y*y + x*x < candidate_radius*candidate_radius
        
    # special grain gets spin == 1
    grain_ids[mask] = candidate_grain_id
    
    # assign 'orientations' to matrix grains according to red_probability
    if redprob < 0 or redprob > 1:
        import sys; sys.exit('invalid texture probability argument')
    if randomize:    
        # choose a random red probability from Uniform(0,redprob)
        redprob = redprob * np.random.random()
    quaternions = random_binary_texture(grain_ids, candidates=[candidate_grain_id],
                                        red_probability=redprob)
    meso.io.save_dream3d(outfile, grain_ids, quaternions)
    meso.io.add_attribute(outfile, 'redprob', redprob)
    return
