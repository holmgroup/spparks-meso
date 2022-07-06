#!/bin/bash
#SBATCH -J AGGmodel
#SBATCH --partition=batchhr
#SBATCH --output=/mnt/data/users/rcohn/Projects/AFRL_AGG/SPPARKS_results/candidate_grains/backup_logs/backup_out_%A_%a.stdout

y=`date +%Y`
mon=`date +%m`
d=`date +%d`
h=`date +%H`
m=`date +%M`

timestamp="${y}_${mon}_${d}_${h}_${m}"

echo "timestamp: ${timestamp}"
source_dir="/home/rcohn/data/Projects/AFRL_AGG/DeCost_SPPARKS/candidate-grains-master/"
target_root="/home/rcohn/data/Projects/AFRL_AGG/SPPARKS_results/candidate_grains/"
echo "source directory: ${source_dir}"
echo "target directory: ${target_root}"
cd $target_root

target_dir="${timestamp}_candidate_grains_master/"
echo "data will be copied to: ${target_root}${target_dir}"

mkdir $target_dir

cd $target_dir
echo "moving  ${source_dir}spparks_results to ${target_root}${target_dir}spparks_results" 
mv "${source_dir}spparks_results" spparks_results
echo "done"

echo "moving ${source_dir}dumps_grow to ${target_root}${target_dir}dumps_grow"
mv "${source_dir}dumps_grow" dumps_grow
echo "done"

echo "moving ${source_dir}dumps_initial to ${target_root}${target_dir}dumps_initial"
mv "${source_dir}dumps_initial" "dumps_initial"
echo "done"

cd "${source_dir}"

echo "copying remaining contents of ${source_dir} to ${target_root}${target_dir}"
cp -r ./* "${target_root}${target_dir}"
echo "done"

echo "creating following folders in ${source_dir}:"
echo "spparks_results/ dumps_grow/ dumps_initial/"
mkdir  spparks_results dumps_grow dumps_initial

echo "done"
