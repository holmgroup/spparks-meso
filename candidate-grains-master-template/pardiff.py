#!/usr/bin/env python

import click
import numpy as np
from tvdiff import TVRegDiff as tvdiff

import ipyparallel as ipp

def do_diff(in_arr):
    maxiter = 250
    alpha = 0.1
    dx = 1.0
    deriv_arr = TVRegDiff(in_arr, maxiter, alpha, dx=dx, 
                          plotflag=False, diagflag=False, scale='large')
    return deriv_arr

@click.command()
@click.option('-i', '--infile', help='numpy array to differentiate (first axis)')
@click.option('-a', '--alpha', default=0.1, help='regularization parameter')
@click.option('--dx', default=1.0, help='spacing between input array elements')
@click.option('--maxiter', default=100, help='max iterations')
@click.option('--plotflag', default=False, is_flag=True, help='show matplotlib plot')
@click.option('--diagflag', default=False, is_flag=True, help='show diagnostic on each iteration')
@click.option('--profile', default='default', help='ipython profile to use')
def diff(infile, alpha, dx, maxiter, plotflag, diagflag, profile):
    in_arr = np.load(infile)
    deriv_arr = np.zeros_like(in_arr)
    nsamples = in_arr.shape[0]
    print('differentiating {} samples...'.format(nsamples))

    rc = ipp.Client(profile=profile)
    view = rc[:]
    with view.sync_imports():
        from tvdiff import TVRegDiff

    in_arrs = [in_arr[i] for i in range(nsamples)]
    deriv = view.map_sync(do_diff, in_arrs)

    try:
        deriv = np.array(deriv)
        np.save('data/size_deriv_parallel.npy', deriv)
    except:
        pass
        

if __name__ == '__main__':
    diff()
