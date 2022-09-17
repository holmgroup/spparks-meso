# SPPARKS-meso

This project implements the python portion of the *candidate grain* simulations as seen in DeCost & Holm [[1]](#1). It assigns grain 'types' to initial microstructures generated from MC Potts simulations, and provides tools for post-processing abnormal grain growth simulations. The modified SPPARKS code that does the heavy lifting of the Monte Carlo simulations is available in a separate repository: https://github.com/holmgroup/spparks.

--------------------------------------------------------------------------

#  Installation 

[Docker](https://www.docker.com/) is the preferred method of installation. The meso utility can be built by simply running:

```bash
$ docker build --target main -t meso:main .
```

There is also a version that works better when using bind mounts to store the results on the host (more info below). To build this version:

```bash
$ docker build --target nonroot -t meso:nonroot.
```

Many HPC systems use [Singularity](https://docs.sylabs.io/guides/3.5/user-guide/introduction.html) instead of Docker. (NOTE: The image is currently incompatible with singularity and can currently only be used with Docker. See "Known issues" section below.) The most straightforward way to build the singularity image is to build and export the image from a machine that has Docker, and then use singularity to convert it to the correct format. After building the image with the above command, export the container to a file:
```bash
$ docker save -o meso.tar meso:main
```
Next, copy the image to a machine with singularity. The image can be converted to a singularity **.sif** file with the following command:

```bash
$ singularity build meso.sif docker-archive://meso.tar
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
$ docker run --rm meso:main -h
```
The outputs are saved in a directory in the container (/home/meso/finished) and can be transferred from the container to the host machine.

The output is a directory named 'run-XXXXXX', where XXXXXX is a zero-padded integer corresponding to the run ID (i.e. the first output is run-000001). The run ID is incremented for each new initial state run in the same job. To ensnure that running a new job won't overwrite existing simulations, you can either create a new results file for each batch of runs, or use the `--start-id` argument to offset the run id. Using `--start-id=$(( $(ls -1 results | wc -l) + 1 ))` will ensure that the job ID starts at 1 greater than the total number of files in the `results` directory, preventing any collisions.

The output contains the spparks input deck (including random seed) used for each simulation, the results/outputs of each simulation, and some additional logs.

## Run with Docker
First, create a directory to save the results to.
```bash
$ mkdir results 
```

To generate simulations:
```bash
$ docker run --rm \
         -v $(pwd)/results:/home/meso-home/runs:rw \
         meso:main [args]
```
Summary of `docker run` arguments:
  - `--rm`: removes container after it executes, preventing clutter
  - `-v $(pwd)/results:/home/meso/finished:rw`: mounts the directory for saving the results.
  - `meso:main`: name and tag of the docker image to run.
  - `[args]`: optional arguments for changing the run parameters, see `$ docker run --rm meso -h` for more info.

**Note:** By default, the container runs as root to have sufficient permissions to write to the bind mount. To access the results without elevated permissions, you will have to change the ownership. On the host machine:
```bash
$ sudo chown -R $(whoami) results
```
## Run with  Docker with nonroot bind mount
It is desirable to not have to manually change permissions after running simulations. Handling non-root users with bind-mounts requires some extra [steps](https://denibertovic.com/posts/handling-permissions-with-docker-volumes/) and would likely break compatiblity with Singularity. Because of this, better handling of the permissions of the bind mount is handled as a separate build stage in the Dockerfile. To build the image:
```bash
$ docker build --target nonroot -t meso:nonroot . 
```
Of course, we still need a folder to save the results to:
```bash
$ mkdir results
```
The UID of the user on the host needs to be passed to the container so that the ownership of the mounted directory can be matched at runtime. To run the container:
```bash
$ docker run --rm -e USER_UID=${UID} \
    -v $(pwd)/results:/home/meso-home/runs:rw  \
    meso:nonroot [args]
```
Explanation of `docker run` options:
  - `-e USER_UID=${UID}`: pass UID from host to container
  - `-v $(pwd)/results:/home/meso-home/runs:rw`: mount directory on host to save simulation results to

## Run with Singularity
We will need a directory on the host to save the results to
```bash
$ mkdir results
```

Singularity also requires an [overlay](https://docs.sylabs.io/guides/3.5/user-guide/persistent_overlays.html) to be created to write the results of the simulation to the container. 
```bash
# creates a 500MB overlay image. You may need to adjust the size depending on your application.
$ mkdir -p overlay/upper overlay/work
$ dd if=/dev/zero of=overlay.img bs=1M count=500 && \
     mkfs.ext3 -d overlay overlay.img
```
To run the container:
```bash
$ singularity run --overlay overlay.img -B "results:/home/meso-home/runs:rw"  meso.sif [args]
```
Explanation of command:
 - `--overlay overlay.img` enables the writeable layer in the container (without it you will get a runtime error)
 - `-B "results:/home/meso-home/runs:rw"` binds the output folder in the container `/home/meso-home/runs` to `results/` on the host and gives read/write permissions, allowing the container to save the finished simulations to the host.

After executing, the finished simulations will be in `results/` on the host.
# References 
<a id="1">[1]</a>
DeCost, B.L., Holm, E.A. Phenomenology of Abnormal Grain Growth in Systems with Nonuniform Grain Boundary Mobility. *Metall Mater Trans A* 48, 2771–2780 (2017).  [doi:10.1007/s11661-016-3673-6](https://doi.org/10.1007/s11661-016-3673-6)
