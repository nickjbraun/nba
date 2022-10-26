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
conda create -n nba_env python=3.10 anaconda

# activate virtual environment, make sure in the NBA root directory
source activate nba_env
conda install pip
pip3 install -r requirements.txt




# set up python environment
pyenv install 3.10.7
python3 -m venv "nba_env"
source nba_env/bin/activate



# libraries






# to see list of all environments
conda info -e
# to deactivate
source deactivate
# to delete a no longer needed environment
conda remove -n yourenvname -all