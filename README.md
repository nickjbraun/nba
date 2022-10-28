# nba
Projects with NBA data

# requirements
Anaconda python distribution is installed and accessible

# check if conda is up to date
conda -V
conda update conda

# see available list of python versions
conda search "^python$"

# create virtual environment
conda create -n nba_env python=3.9.7 anaconda
conda activate nba_env
conda install pip
pip3 install -r requirements.txt

# activate virtual environment, make sure in the NBA root directory









# set up python environment
pyenv install 3.10.7
python3 -m venv "nba_env"
source nba_env/bin/activate



# libraries






# to see list of all environments
conda info -e
conda env list
# to deactivate
conda deactivate
# to delete a no longer needed environment
conda env remove -n nba_env