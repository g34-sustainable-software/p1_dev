# Before Running the Experiments 

1. Download the zip package of energibridge and follow the system installation instructions
2. Ensure user perimissions such that the following command will work: 
```bash 
target/release/energibridge --summary sleep 1
``` 
3. Move or copy the `target` directory into the root directory of this project. 
4. Ensure that google chrome is installed 
5. Run the installation commands: 
```bash 
python -m venv venv 
source venv/bin/activate # for Linux or hardware equivalent
pip install -r requirements.txt
```


# How to Capture Energy consumption metrics
If google chrome is installed ensure you are in the root directory of this project. 
These commands have been tested on MACOSX and a Linux machine. \
For guaranteed performance use the following hardware: 
- Model Name:   MacBook Air
- Model Identifier:     Mac14,2
- Chip: Apple M2
- Total Number of Cores:        8 (4 performance and 4 efficiency)
- Memory:       8 GB
- Resolution:   2560x1664 Retina
- Refresh Rate: 60Hz

Start the energy capture using one of the two commands: 
```bash
python run_experiment.py --setting <Any combination of: ["all-off", "stable-volume", "voice-boost", "ambient-mode"] without the quotations, commas or braces>
```
or
```bash
python run_experiment.py --setting all-off stable-volume voice-boost ambient-mode
```


# Sumary
To create a summary of all the data, open the Jupyter notebook `compilation.ipynb`.   
Run the `run all` command and view the results.














































