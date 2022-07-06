#!/usr/bin/env python

import click
import numpy as np
from tvdiff import TVRegDiff as tvdiff


@click.command()
@click.option('-i', '--infile', help='numpy array to differentiate (first axis)')
@click.option('-a', '--alpha', default=0.1, help='regularization parameter')
@click.option('--dx', default=1.0, help='spacing between input array elements')
@click.option('--maxiter', default=100, help='max iterations')
@click.option('--plotflag', default=False, is_flag=True, help='show matplotlib plot')
@click.option('--diagflag', default=False, is_flag=True, help='show diagnostic on each iteration')
def diff(infile, alpha, dx, maxiter, plotflag, diagflag):
    in_arr = np.load(infile)
    deriv_arr = np.zeros_like(in_arr)
    nsamples = in_arr.shape[0]
    disp = np.arange(0, nsamples, 100)

    print('differentiating {} samples...'.format(nsamples))
    for ids in range(nsamples):
        deriv_arr[ids] = tvdiff(in_arr[ids], maxiter, alpha, dx=dx, 
                                plotflag=plotflag, diagflag=diagflag, scale='large')
        if ids in disp:
            print('iteration {}'.format(ids))

    np.save('data/size_deriv.npy', deriv_arr)
                               

if __name__ == '__main__':
    diff()
