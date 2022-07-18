# SPPARKS-meso

This project implements the python portion of the *candidate grain* simulations as seen in DeCost & Holm [[1]](#1). It assigns grain 'types' to initial microstructures generated from MC Potts simulations, and provides tools for post-processing abnormal grain growth simulations. The modified SPPARKS code that does the heavy lifting of the Monte Carlo simulations is available in a separate repository: https://github.com/holmgroup/spparks.

--------------------------------------------------------------------------

#  Installation 

[Docker](https://www.docker.com/) is the preferred method of installation. Note that the *spparks-candidate-grains* image is the single dependency of this project. To build and test the *spparks-candidate-grains* image, follow the installation instructions in https://github.com/holmgroup/spparks. 
Afterwards, the meso utility can be built by simply running:

```bash
$ docker build -t meso .
```

Many HPC systems use [Singularity](https://docs.sylabs.io/guides/3.5/user-guide/introduction.html) instead of Docker. (NOTE: The image is currently incompatible with singularity and can currently only be used with Docker. See "Known issues" section below.) The most straightforward way to build the singularity image is to build and export the image from a machine that has Docker, and then use singularity to convert it to the correct format. After building the image with the above command, export the container to a file:
```bash
$ docker save -o meso.tar meso:latest
```
Next, copy the image to a machine with singularity. The image can be converted to a singularity **.sif** file with the following command:

```bash
$ singularity build meso.sif docker-archive:./meso.tar
```

# Generating simulations.

*Meso* provides a simple CLI for running sets of simulations. The following parameters can be controlled:
  - Length of square simulation box in pixels
  - Fraction of 'red grains' in each initial microstructure
  - Number of initial microstructures to generate
  - Number of repeated grain growth simulations for each initial microstructure with a unique random seed to run
  - MC Temperature of grain growth simulations
  - Number of iterations to run each growth simulaiton 
  - Number of iterations between 'checkpoints' where grain size statistics are saved
  - Whether to generate 'grains.mov' animations of the growth trajectory of each simulation 

The default entrypoint of the container calls the required binaries required to run and process simulations. Thus, you only need to pass the desired arguments to the container. A list of arguments, along with their syntax, descriptions, and default values, can be obtained by running the container with the -h or --help options. For example:

```bash
$ docker run --rm meso -h
```
The outputs are saved in a directory in the container (/home/meso/finished) and can be transferred from the container to the host machine.

The output is a directory named 'run-XXXXXX', where XXXXXX is a zero-padded integer corresponding to the run ID (i.e. the first output is run-000001). The run ID is incremented for each new initial state run in the same job. To ensnure that running a new job won't overwrite existing simulations, you can either create a new results file for each batch of runs, or use the `--start-id` argument to offset the run id. Using `--start-id=$(( $(ls -1 results | wc -l) + 1 ))` will ensure that the job ID starts at 1 greater than the total number of files in the `results` directory, preventing any collisions.

The output contains the spparks input deck (including random seed) used for each simulation, the results/outputs of each simulation, and some additional logs.

## Run with Docker
First, create a directory that the docker container has sufficient write permissions to. This is where the results will be saved. 
```bash
$ mkdir results && chmod 777 results
```

To generate simulations:
```bash
$ docker run --rm \
         -v $(pwd)/results:/home/meso/finished:rw \
         meso [args]
```
Summary of `docker run` arguments:
  - `--rm`: removes container after it executes, preventing clutter
  - `-v $(pwd)/results:/home/meso/finished:rw`: mounts the directory for saving the results.
  - `meso`: name of the docker image to run.
  - `[args]`: optional arguments for changing the run parameters, see `$ docker run --rm meso -h` for more info.

## Run with Singularity
NOTE: The image is currently incompatible with singularity and can currently only be used with Docker. See "Known issues" section below.

Running with Singularity is very straightforward:
```bash
$ singularity run meso.sif [args]
```
Note that Singularity bind mounts `/home/$USER`, `/tmp`, and `$PWD` into the container at runtime, so no explicit mount commands are needed, unlike with Docker. 

# Known issues
 
 |Issue                                           |     Description              |
 |------------------------------------------------|------------------------------|
 | Segfault after initial microstructure creation | After generating the initial microstructures, SPPARKS will throw a segfault error. However, this appears to be with some unused post-processing routine, as the simulations still run and the outputs still contain all of the expected data.                                                  
 |Singularity incompatibility                     | the image will build without error, but raise "file not found" or "read only file system" errors when run. The issue appears to be related to how Singularity treats (or, more precisely, doesn't treat) the "workdir" and "user" directives. Because singularity executes in the current directory on the host machine, it will not find local files in the workdir of the docker image without absolute paths. Similarly, the container appears to run as the user on the host machine instead of the user specified in the Dockerfile. Thus, file permissions do not work correctly. Both of these issues can be corrected, but require fixing all the paths and changing permissions, so we will hold off on this for now. If you need this functionality feel free to put a request in the issue tracker to bump up the priority.                   |

# References 
<a id="1">[1]</a>
DeCost, B.L., Holm, E.A. Phenomenology of Abnormal Grain Growth in Systems with Nonuniform Grain Boundary Mobility. *Metall Mater Trans A* 48, 2771–2780 (2017).  [doi:10.1007/s11661-016-3673-6](https://doi.org/10.1007/s11661-016-3673-6)
