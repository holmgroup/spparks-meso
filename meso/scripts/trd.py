# -*- coding: utf-8 -*-
"""
    meso.scripts.trd
    ~~~~~~~

    Set up a dream3d microstructure for a discrete texture simulation with model "twinning related domains".

    :copyright: (c) 2016 by Brian DeCost
    :license: MIT, see LICENSE for more details.
"""

import click
import numpy as np
from collections import deque

import meso.io
import meso.network


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])
@click.command(context_settings=CONTEXT_SETTINGS)
@click.argument('infile', type=click.Path(exists=True))
@click.option('-o', '--outfile', default='initial_trd.dream3d', type=click.Path(), help='output file')
@click.option('-s', '--size', default=0, type=float, help='specify minimum relative candidate grain size')
@click.option('-c', '--count', default=1, type=int, help='number of TRDs to generate')
@click.option('-p', '--prob', default=0.15, type=float, help='edge probability for growing TRD')
@click.option('--shuffle/--no-shuffle', default=True, help='shuffle grain IDs, starting from 1')
def trd(infile, outfile, size, count, prob, shuffle):
    """ Set up twinning-related domain model microstructure for a discrete texture components """

    # assign 'orientations' to matrix grains according to red_probability
    if prob < 0 or prob > 1:
        import sys; sys.exit('invalid texture probability argument')
        
    grain_ids = meso.io.load_dream3d(infile)
    grain_ids = meso.io.renumber(grain_ids, start_from=1)
    network = meso.network.transgranular_network(grain_ids)
    
    # colors should have a leading zero (in keeping with DREAM3D memory conventions)
    colors = np.zeros(1 + network.number_of_nodes(), dtype=int)

    # start labeling TRDs at 1
    for id_trd in range(1, 1+count):
        seed = np.random.choice(np.unique(grain_ids))
        colors[seed] = id_trd
        visited = set([seed])
        queue = deque(network.neighbors(seed))
        while len(queue) > 0:
            candidate = queue.popleft()
            if colors[candidate] != 0:
                # sometimes skip grains that are already part of a different TRD
                if np.random.uniform() < 0.5:
                    continue
            visited.add(candidate)
            if np.random.uniform() < prob:
                colors[candidate] = id_trd
                for neigh in network.neighbors(candidate):
                    if neigh not in visited:
                        visited.add(neigh)
                        queue.append(neigh)
                
    meso.io.save_dream3d(outfile, grain_ids, colors=colors)
    meso.io.add_attribute(outfile, 'prob', prob)
    return
