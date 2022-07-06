candidate-grains
----------------

Run batches of abnormal grain growth simulations.

`submit_loop.sh` for the main entry point for this project. This script basically exists because the version of `slurm` we were using (or just our config) was limited to array jobs of max size 1000.
Currently you need to set the `JOBSCRIPT` variable (lines 6 and 7) to switch between growing initial grain structures and running abnormal grain growth simulations.
The two job scripts should really be merged into a single job...

## structure initialization
Initial structures are grown by running `submit_loop.sh` after setting `JOBSCRIPT=agg_model_initial.submit`.

`agg_model_initial.submit` first grows initial grain structures with SPPARKS KMC potts model runs, and then assigns texture using the `meso candidate` command.
Edit `init_template.spkin` for the KMC settings (simulation size, Monte Carlo temperature, etc).
Change the texture of the initial microstructure by editing the commandline arguments to `meso candidate` on line 67 of the job script.... (run `meso candidate --help` for details).


## abnormal grain growth simulations
Abnormal grain growth simulations are run by executing `submit_loop.sh` after setting `JOBSCRIPT=agg_model_grow.submit`.

`agg_model_grow.submit` runs SPPARKS `potts/ori` simulations using the starting structure generated in the previous script.
Edit `agg_model_template.spkin` to change KMC settings (e.g. the energy and mobility ratios used in the `potts/ori` solver).
Finally, the job script runs `meso animate` and `meso networks` to draw movies and construct and serialize the transgranular networks.


