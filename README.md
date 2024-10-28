# DDE2 - CNN-based regression of drop impact parameters 


## Introduction to repo

In this repo you find all scripts and relevant files we created for our project "CNN-based regression of drop impact parameters" which was part of the DDE2 lecture hold by Cihan Ates. The project data was given by Maximilian Dreisbach. Thank you Cihan and Max for your support! 

## Overview of the repo

- [get_parameters.py](https://git.scc.kit.edu/utgsr/dde2_project/-/blob/main/get_parameters.py) is used to extract all features we created from the render data given by Maximilian Dreisbach. It was submitted to the HPC by using a [bash script](https://git.scc.kit.edu/utgsr/dde2_project/-/blob/main/parameter_bash.sh), the extracted parameter data was saved in a [json file](https://git.scc.kit.edu/utgsr/dde2_project/-/blob/main/parameter_data.json).

- [get_angles_from_pictures.ipynb](https://git.scc.kit.edu/utgsr/dde2_project/-/blob/main/get_angles_from_pictures.ipynb) validates our angle calculation (which was performed via trimesh in get_parameters.py) using a grafical approach.

- [parameter_calculation.ipynb](https://git.scc.kit.edu/utgsr/dde2_project/-/blob/main/parameter_calculation.ipynb) is the long version of get_parameters.py including explanations and validations of the introduced parameters.

- [cnn_project.ipynb](https://git.scc.kit.edu/utgsr/dde2_project/-/blob/main/cnn_project.ipynb) is the notebook where we did the CNN-based regression of our drop impact parameters, using input data with and without glarepoints. In this context we saved the [best model trained on input data with glarepoints](https://git.scc.kit.edu/utgsr/dde2_project/-/blob/main/best_model_norm.h5) as well as the [best model trained on input data without glarepoints](https://git.scc.kit.edu/utgsr/dde2_project/-/blob/main/best_model_norm_wo_gp.h5) to reuse it for later visualization.

- [cnn_project_second_meeting.ipynb](https://git.scc.kit.edu/utgsr/dde2_project/-/blob/main/cnn_project_second_meeting.ipynb) is a former version of the cnn_project.ipynb but was saved seperately, as it contains single output prediction models, whereas the final project concentrates on multi output prediction only.

- [visualization.ipynb](https://git.scc.kit.edu/utgsr/dde2_project/-/blob/main/visualization.ipynb) visualizes what happens in the CNN layers of the models created in our cnn_project.ipynb script.
