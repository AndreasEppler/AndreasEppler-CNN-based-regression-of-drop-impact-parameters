#!/bin/bash

#SBATCH --nodes 1
#SBATCH --ntasks=1
#SBATCH --partition=single
#SBATCH --mem-per-cpu 9000
#SBATCH --time=10:00:00
#SBATCH --job-name=get_parameters
#SBATCH --mail-type ALL
#SBATCH --mail-user=utgsr@student.kit.edu
module purge
module load devel/python/3.8.6_intel_19.1

source $HOME/DDE2_project/dde2_venv/bin/activate
python3 -m pip install matplotlib
python3 -m pip install trimesh
python3 -m pip install shapely
python3 -m pip install scipy
python3 -m pip install scikit-image
python3 get_parameters.py > parameters.out
