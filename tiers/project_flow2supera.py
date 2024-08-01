import glob, os
import numpy as np
import flow2supera
from project_base import project_base


class flow2supera(project_base):

    def __init__(self):
        super().__init__()


    def parse_project_config(self,cfg):

        super().parse_project_config(cfg)

        if not 'SUPERA_CONFIG' in cfg:
            raise KeyError(f'SUPERA_CONFIG key is missing in the configuration data!\n{cfg}')

        # make sure config is valid
        valid_configs = flow2supera.config.list_config()
        if not cfg['SUPERA_CONFIG'] in valid_configs:
            if not os.path.isfile(cfg['SUPERA_CONFIG']):
                raise FileNotFoundError(f'SUPERA_CONFIG {cfg["SUPERA_CONFIG"]} not found.')
            self.COPY_FILES.append(cfg['SUPERA_CONFIG'])
            cfg['SUPERA_CONFIG'] = os.path.basename(cfg['SUPERA_CONFIG'])


    def gen_project_script(self,cfg):

        cmd_supera = f'''run_flow2supera.py \
-o {cfg['JOB_OUTPUT_ID']}-larcv.root \
-c {cfg['SUPERA_CONFIG']}'''

        self.PROJECT_SCRIPT = f'''#!/bin/bash

echo "Starting a job"
date

export PATH=$HOME/.local/bin:$PATH

echo "Copying a file"
SOURCE_FILE_NAME=`python3 input_name.py $SLURM_ARRAY_TASK_ID`
INPUT_FILE_NAME=`basename $SOURCE_FILE_NAME`
echo scp $SOURCE_FILE_NAME $INPUT_FILE_NAME
scp $SOURCE_FILE_NAME $INPUT_FILE_NAME
date
'''
        if 'LARCV_DIR' in cfg:
            self.PROJECT_SCRIPT += f'''

echo "Using larcv from {cfg['LARCV_DIR']}"
source {cfg['LARCV_DIR']}/configure.sh
'''

        self.PROJECT_SCRIPT += f'''

echo "Running Supera"
export PATH=$HOME/.local/bin:$PATH
echo {cmd_supera} $INPUT_FILE_NAME
{cmd_supera} $INPUT_FILE_NAME &> log_supera.txt
date

echo "Removing the input"
echo rm $INPUT_FILE_NAME
rm $INPUT_FILE_NAME
date

echo "Touching the input filename"
echo touch $INPUT_FILE_NAME
touch $INPUT_FILE_NAME
date

echo "Exiting"
        '''

if __name__ == '__main__':
    import sys
    if not len(sys.argv) == 2:
        print(f'Invalid number of the arguments ({len(sys.argv)})')
        print(f'Usage: {os.path.basename(__file__)} $JOB_CONFIGURATION_YAML')
        sys.exit(1)

    if not sys.argv[1].endswith('.yaml'):
        print('The argument must be a yaml file with .yaml extension.')
        print(f'(provided: {os.path.basename(sys.argv[1])})')
        sys.exit(2)

    p=project_flow2supera()
    p.generate(sys.argv[1])
    sys.exit(0)
