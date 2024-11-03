# Ant_detection_Yolo8

## Please contact Ofir Levy ([levyofir@tauex.tau.ac.il]()) about the code or data

### Preparing the Python environment
Our approach uses the recommendations and Python modules in Microsoft's computer vision recipes. Our training scripts are adaptations of their training scripts for detection and classification scenarios.

We prepared the conda environment as described in their GitHub repository:


```bash
git clone https://github.com/Microsoft/computervision-recipes
cd computervision-recipes
conda env create -f environment.yml
```

Additional required libraries:
- os
- opencv-python
- ipython

To run `parallel_run.sh`, in the command line, go to folder where the file is, and run `./parallel_run.sh`
You may change the parameters and their values in the `parallel_run.sh` according to your needs.