# start with working spparks binary
# Dockerfile in https://github.com/holmgroup/spparks
FROM spparks-candidate-grains:latest AS main

RUN apt-get update && apt-get install -y --no-install-recommends \
      ca-certificates build-essential git wget ffmpeg && apt-get clean && apt-get autoremove && \
      rm -rf /var/lib/apt/lists/* && \
      wget --quiet https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh && \
      bash Miniconda3-latest-Linux-x86_64.sh -b -p /usr/local/share/miniconda && \
      rm -rf Miniconda3-latest-Linux-x86_64.sh

WORKDIR /home/meso-home
COPY env.yaml setup.py candidate_grains.sh parse_args.py entrypoint.sh ./
COPY meso meso
COPY candidate-grains-master-template candidate-grains-master-template

# create venv, install dependencies, install meso, copy binary
# to /usr/bin, and make it executible
RUN /usr/local/share/miniconda/bin/conda env create --name meso-env -f env.yaml && \
    /usr/local/share/miniconda/envs/meso-env/bin/python -m pip install . && \
    rm env.yaml && \
    cp meso/usr-bin-meso /usr/bin/meso && \
    chmod +x entrypoint.sh && \
    mkdir runs

# add python for meso to path
# also set language encoding needed for CLI to work properly
ENV PATH="/usr/local/share/miniconda/envs/meso-env/bin:${PATH}" \
    LANG_ALL=C.UTF-8 LANG=C.UTF-8

# needed for singularity compatibility
RUN chmod -R 777 /home/meso-home

ENTRYPOINT ["/home/meso-home/entrypoint.sh"]

# build su-exec for handling permissions
FROM debian:10.12-slim AS builder
RUN apt-get update && apt-get install -y \
    build-essential git && \
    rm -rf /var/lib/apt/lists/* && \
    # download the source for su-exec
    cd /home/ && git clone https://github.com/ncopa/su-exec.git && \
    # build su-exec and move the binary to /usr/local/sbin
    cd su-exec && make su-exec && mv su-exec /usr/local/sbin && \
    # remove the remaining files when we are done
    rm -rf /home/su-exec

FROM main AS nonroot
COPY --from=builder /usr/local/sbin/su-exec /usr/local/sbin/su-exec

COPY entrypoint_nonroot.sh ./
RUN chmod +x entrypoint_nonroot.sh
ENTRYPOINT ["./entrypoint_nonroot.sh"]

