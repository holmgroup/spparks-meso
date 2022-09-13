#! /bin/bash

# use default UID=1000 if one is not supplied to the container
if [ -z ${USER_UID} ];
then
    export USER_UID=1000
fi

adduser --disabled-password --gecos "" --uid ${USER_UID} meso

# variable definitions for non-root user
export USER=meso HOME=/home/meso

# allow non-root user to access mounted volume
chown ${USER} /home/meso-home/runs

# 
exec /usr/local/sbin/su-exec ${USER} /home/meso-home/entrypoint.sh "$@"
    

