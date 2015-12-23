# -*- coding: utf-8 -*-
"""
    meso.scripts.cli
    ~~~~~~~

    Command line tools for working with the meso library

    :copyright: (c) 2015 by Brian DeCost
    :license: MIT, see LICENSE for more details.
"""

    
import click

from meso.scripts import candidate, visualize

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])
@click.group(context_settings=CONTEXT_SETTINGS)
def cli():
    """ Command line tool for working with the meso library """
    pass

cli.add_command(candidate.candidate)
cli.add_command(visualize.draw)
cli.add_command(visualize.animate)
