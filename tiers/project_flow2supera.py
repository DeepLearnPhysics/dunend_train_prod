import glob, os
import numpy as np
from .project_base import project_base


class flow2supera(project_base):

    def __init__(self):
        super().__init__()


    def parse_project_config(self,cfg):

        import flow2supera

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

        PROJECT_SCRIPT = f'''
export PATH=$HOME/.local/bin:$PATH
'''
        if 'LARCV_DIR' in cfg:
            PROJECT_SCRIPT += f'''
echo "Using larcv from {cfg['LARCV_DIR']}"
unset which
source {cfg['LARCV_DIR']}/configure.sh
'''

        PROJECT_SCRIPT += f'''
date
echo "Running Supera"
export PATH=$HOME/.local/bin:$PATH
echo {cmd_supera} $INPUT_FILES
{cmd_supera} $INPUT_FILES &> log_supera.txt
date
'''
        return PROJECT_SCRIPT
    
