import glob, os
import numpy as np
import flow2supera
from project_base import project_base


class project_flow2supera(project_base):

    def num_jobs(self,cfg):
        for key in cfg:
            if not key.lower() == 'slurm_array':
                continue
            num_jobs = cfg[key]
            if '%' in num_jobs:
                num_jobs = num_jobs.split('%')[0]
            if '-' in num_jobs:
                jmin,jmax = num_jobs.split('-')
                num_jobs = int(jmax) - int(jmin) + 1
            return int(num_jobs)
        raise KeyError('SLURM_ARRAY not found in the config. Cannot parse the job count')

    def parse_project_config(self,cfg):

        if not 'SUPERA_CONFIG' in cfg:
            raise KeyError(f'SUPERA_CONFIG key is missing in the configuration data!\n{cfg}')

        # make sure config is valid
        valid_configs = flow2supera.config.list_config()
        if not cfg['SUPERA_CONFIG'] in valid_configs:
            if not os.path.isfile(cfg['SUPERA_CONFIG']):
                raise FileNotFoundError(f'SUPERA_CONFIG {cfg["SUPERA_CONFIG"]} not found.')
            self.COPY_FILES.append(cfg['SUPERA_CONFIG'])
            cfg['SUPERA_CONFIG'] = os.path.basename(cfg['SUPERA_CONFIG'])

        filelist = glob.glob(os.path.expandvars(cfg['GLOB']))
        if len(filelist) < 1:
            raise KeyError(f'GLOB {cfg["GLOB"]} returned no file!')

        # assert the file count matches the requested job count

        if not len(filelist) == self.num_jobs(cfg):
            print(f'GLOB {cfg["GLOB"]} returned {len(filelist)} files')
            print(f'But requested job count is {self.num_jobs(cfg)} (must match)')
            raise ValueError(f'GLOB {cfg["GLOB"]} returned unexpected file count')

        # create a filelist
        with open(os.path.join(cfg['JOB_SOURCE_DIR'],'flist.txt'),'w') as f:
            for name in filelist:
                f.write(os.path.abspath(name)+'\n')
                self.BIND_PATHS.append(self.get_top_dir(name))

        script = '''
import sys
jobid = int(sys.argv[1])-1
print(open('flist.txt','r').read().split()[jobid])
        '''
        with open(os.path.join(cfg['JOB_SOURCE_DIR'],'input_name.py'),'w') as f:
            f.write(script)



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
