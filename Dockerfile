# stort with working spparks binary
FROM spparks-candidate-grains:latest

USER root
 # install dependencies
RUN apt-get update && apt-get -y --no-install-recommends install \
	ca-certificates \
	software-properties-common \
	python3-venv \
	python3-dev \
	ffmpeg \
    && apt-get clean \
	&& apt-get autoremove \
	&& rm -rf /var/lib/apt/lists/*

WORKDIR /home/root/

# spparks-candidate-grains already defines UID1000 so start at 1001
RUN groupadd --gid=1001 meso \
    && useradd --uid 1001 --gid 1001 -m meso

ENV HOME=/home/meso
WORKDIR ${HOME}

USER meso
COPY requirements.txt requirements.txt
RUN python3 -m venv env
ENV PATH="${HOME}/env/bin:${HOME}/.local/bin:${PATH}"
RUN python3 -m pip install -r requirements.txt

COPY --chown=meso:meso meso meso
COPY --chown=meso:meso setup.py setup.py
RUN pip install .

USER root
RUN chmod o+x meso/usr-bin-meso
RUN cp meso/usr-bin-meso /usr/bin/meso


USER meso
COPY --chown=meso:meso candidate-grains-master-template candidate-grains-master-template
COPY --chown=meso:meso single_set.sh single_set.sh
COPY --chown=meso:meso parse_args.py parse_args.py
COPY --chown=meso:meso run_job.sh run_job.sh

# needed or else python will try to use ASCII and error out on meso command
ENV LC_ALL=C.UTF-8 \
    LANG=C.UTF-8

# 
VOLUME /home/meso/finished

ENTRYPOINT ["bash", "run_job.sh"]
