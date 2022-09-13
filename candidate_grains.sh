#!/bin/bash

ntrial=${1} # number of repeated trials for single initial structure
redfrac=${2} # initial fraction of red grains
job_id=${3}  # number to give job
animate=${4} # 1 if grains.mov file should be created, otherwise 0

seeds=($(shuf -n ${ntrial} -i 1-2147483647)) # unique, randomly selected seeds for each grain growth trial

# absolute paths needed for compatibility with Singularity
exp_dir="/home/meso-home/runs/run-${job_id}" # directory for set of trials
template_dir="/home/meso-home/candidate-grains-master-template"

TIMESTAMPS="${exp_dir}/runtimes.txt" # for recording time required to run each simulation

cp -r  ${template_dir} ${exp_dir} # copy code only (ie no initial states/results)

# scratch is a temp directory where all dump files are stored before processing
# results is where the outputs (ie stats.h5) are stored
SCRATCH="${exp_dir}/scratch"
RESULTS="${exp_dir}/spparks_results/run_1"

mkdir -p ${SCRATCH}
mkdir -p ${RESULTS}

cd ${SCRATCH}
# generate single seed for initializing the microstructure
INIT_SEED=$(shuf -n 1 -i 1-2147483647)
INIT_FILE=grow_initial.spkin
echo "seed ${INIT_SEED}" > ${INIT_FILE} 
cat ${exp_dir}/init_template.spkin >> ${INIT_FILE} 
SECONDS=0 # $SECONDS is a special variable that increments every second. use this to time each part of the run.


spparks -in ${INIT_FILE} # run the simulation
mv log.spparks init_spparks.log
# note default -s is -0.5, not 0.5

meso candidate initial0.dream3d -o initial.dream3d -s -0.5 -r ${redfrac}
echo "initialize: ${SECONDS}" >> ${TIMESTAMPS}
SPPARKS_INIT=${exp_dir}/spparks_init
mkdir -p ${SPPARKS_INIT}
for f in initial.dream3d $INIT_FILE init_spparks.log
do
    mv $f ${SPPARKS_INIT}/
done

cd ${exp_dir}
rm -rf ${SCRATCH}

# copy initial seed to initialize repeated trials
for i in $(seq 2 ${ntrial})
do
  cp -r ${RESULTS} ${exp_dir}/spparks_results/run_${i}
done

GROW_FILE=agg_model.spkin

# run all seeds
for i in $(seq 1 ${ntrial})
do
  mkdir ${SCRATCH}
  cd ${SCRATCH} 
  # bash is 0-indexed. remember to avoid off-by-1 error when indexing!
  echo "seed ${seeds[$(expr ${i}-1)]}" > ${GROW_FILE} # set seed for trial
  cat ${exp_dir}/agg_model_template.spkin >> ${GROW_FILE}
  SECONDS=0 # reset timer
  cp ${SPPARKS_INIT}/* . # copy all required outputs from initial microstructure creation to scratch
  spparks -in ${GROW_FILE} # run spparks
  echo "run-${i}: ${SECONDS}" >> ${TIMESTAMPS}
  SECONDS=0
  mv log.spparks grow_spparks.log # rename log
  if [ ${animate} = "1" ];
  then
    # animation and formatted outputs
    meso animate agg_dump*.dream3d -o grains.mov --initial initial.dream3d --colorscheme binary
    # meso networks agg_dump*.dream3d -o network.h5
    mv grains.mov ${exp_dir}/spparks_results/run_${i}
    echo "animate-${i}: ${SECONDS}" >> ${TIMESTAMPS}
  fi
  
  # archive outputs 
  for f in ${GROW_FILE} grow_spparks.log stats.h5
  do
    mv ${f} ${exp_dir}/spparks_results/run_${i}
  done
  cd ${exp_dir}
  rm -rf ${SCRATCH} ${exp_dir}/temp
done
