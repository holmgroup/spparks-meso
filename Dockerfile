FROM debian:10.12-slim AS base

# libraries needed both during build and runtime
# ln -s commands are needed for the linker to find the right libraries during the build
RUN apt-get update && apt-get -y --no-install-recommends install \
    ca-certificates libhdf5-dev libeigen3-dev build-essential ffmpeg && \
	apt-get clean && apt-get autoremove && rm -rf /var/lib/apt/lists* && \
	ln -s /usr/lib/x86_64-linux-gnu/libhdf5_serial.so /usr/lib/libhdf5.so && \
    ln -s /usr/lib/x86_64-linux-gnu/libhdf5_serial_hl.so /usr/lib/libhdf5_hl.so

FROM base AS builder
# git, wget, build-essential only needed during build
# build binaries for spparks, su-exec, and miniconda 
RUN apt-get update && apt-get -y --no-install-recommends install \
    git wget && apt-get clean && apt-get autoremove && \
    rm -rf /var/lib/apt/lists* && cd /home && \
    git clone https://github.com/holmgroup/spparks.git spparks-src && \
    git clone https://github.com/ncopa/su-exec.git su-exec && \
    wget --quiet https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh && \
    cd /home/spparks-src/src && make stubs && make h5 && mv spk_h5 /home/spparks && \
    cd /home/su-exec && make su-exec && mv su-exec /usr/local/sbin/su-exec && \
    rm -rf /home/spparks-src /home/su-exec

# for running container 
FROM base AS main
WORKDIR /home/meso-home 
COPY --from=builder /home/Miniconda3-latest-Linux-x86_64.sh ./
COPY --from=builder /home/spparks /usr/local/sbin/spparks

RUN  bash /home/meso-home/Miniconda3-latest-Linux-x86_64.sh -b -p /usr/local/share/miniconda

COPY env.yaml setup.py candidate_grains.sh parse_args.py entrypoint.sh ./
COPY candidate-grains-master-template candidate-grains-master-template
COPY meso meso

# move spparks and conda so they can be executed
# create venv, install dependencies, install meso, copy binary
# to /usr/bin, and make it executible
# chmod home directory needed for singularity compatibility since it runs with a different user

RUN /usr/local/share/miniconda/bin/conda env create --name meso-env -f env.yaml && \
    /usr/local/share/miniconda/envs/meso-env/bin/python -m pip install . && \
    rm env.yaml && \
    cp meso/usr-bin-meso /usr/bin/meso && \
    chmod +x entrypoint.sh && \
    mkdir runs && chmod -R 777 /home/meso-home


# add python for meso to path
# also set language encoding needed for CLI to work properly
ENV PATH="/usr/local/share/miniconda/envs/meso-env/bin:${PATH}" \
    LANG_ALL=C.UTF-8 LANG=C.UTF-8



ENTRYPOINT ["/home/meso-home/entrypoint.sh"]

# for running container with non-root permissions for bidn mount
FROM main AS nonroot
COPY --from=builder /usr/local/sbin/su-exec /usr/local/sbin/su-exec
COPY entrypoint_nonroot.sh ./
RUN chmod +x entrypoint_nonroot.sh
ENTRYPOINT ["./entrypoint_nonroot.sh"]

