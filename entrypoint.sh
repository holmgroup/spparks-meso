#! /bin/bash

# 5 outputs to stdout
# note that if -h or --help is called, then the first output will be
# "Usage" instead of the actual value
# 1: number of initial states 
# 2: number of growth simulations for each initial state
# 3: fraction of red grains in each initial state
# 4: start id of job (determines filename for saving)
# 5: 1 if animation script should be run, 0 otherwise
x=$(python /home/meso-home/parse_args.py $@ ) 
xarr=( ${x} ) # store as array to test if help was called

if [ "${xarr[0]}" = "usage:" ]; then
	printf "%s\n" "${x[@]}" # print formatted output (printf saves pretty printing)
	exit 0 # help was called, no action needed
fi

n_init=${xarr[0]} # number of initial states to generate
ntrial=${xarr[1]} # number of repeated trials for single initial structure
redfrac=${xarr[2]} # initial fraction of red grains
start_id=${xarr[3]} # start id of job
animate=${xarr[4]} # 1 if .mov animations should be generated for growth simulations

for i in $(seq 0 $(( ${n_init} - 1 )) );
do
	# determine job id number and format (0 padding)
	job_id_unformat=$(( ${start_id} + ${i}))
	job_id_format=$(python -c "print(f'{${job_id_unformat}:06d}')")  

	# run single set of growht simulations for 1 initial microstructure
	. /home/meso-home/candidate_grains.sh ${ntrial} ${redfrac} ${job_id_format} ${animate}

done
