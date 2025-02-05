import yaml, os, pathlib, shutil
import numpy as np
from yaml import Loader
from datetime import timedelta
from .project_base import project_base


class flow(project_base):


    def __init__(self):
        super().__init__()
        project_dict = dict(FLOW_YAML='',FLOW_DATA='', FLOW_YAML_PATH='')
        self.REQUIRED.update(project_dict)
        
    def parse_project_config(self,cfg):
        super().parse_project_config(cfg)

    def gen_project_script(self,cfg):

        cmd_flow_def = f'''
inFile=$INPUT_FILES
outFile={cfg['JOB_OUTPUT_ID']}-flow.h5

# charge workflows
workflow1='yamls/{cfg['FLOW_YAML_PATH']}/workflows/charge/charge_event_building_mc.yaml'
workflow2='yamls/{cfg['FLOW_YAML_PATH']}/workflows/charge/charge_event_reconstruction_mc.yaml'
workflow3='yamls/{cfg['FLOW_YAML_PATH']}/workflows/combined/combined_reconstruction_mc.yaml'
workflow4='yamls/{cfg['FLOW_YAML_PATH']}/workflows/charge/prompt_calibration_mc.yaml'
workflow5='yamls/{cfg['FLOW_YAML_PATH']}/workflows/charge/final_calibration_mc.yaml'

# light workflows{cfg['FLOW_YAML_PATH']}
workflow6='yamls/{cfg['FLOW_YAML_PATH']}/workflows/light/light_event_building_mc.yaml'
workflow7='yamls/{cfg['FLOW_YAML_PATH']}/workflows/light/light_event_reconstruction.yaml'

# charge-light trigger matching
workflow8='yamls/{cfg['FLOW_YAML_PATH']}/workflows/charge/charge_light_assoc.yaml'

        '''

        cmd_flow_charge = 'h5flow -c $workflow1 $workflow2 $workflow3 $workflow4 $workflow5 -i $inFile -o $outFile'
        cmd_flow_light = 'h5flow -c $workflow6 $workflow7 -i $inFile -o $outFile'
        cmd_flow_charge_light = 'h5flow -c $workflow8 -i $outFile -o $outFile'

        PROJECT_SCRIPT=f'''

{cmd_flow_def}

date
echo "Running ndlar_flow charge"
echo {cmd_flow_charge}
{cmd_flow_charge} &>> log_flow.txt

#date
#echo "Running ndlar_flow light"
#{cmd_flow_light} &>> log_flow_light.txt

#date
#echo "Running ndlar_flow charge_light"
#{cmd_flow_charge_light} &>> log_flow_charge_light.txt

# for the next stage
INPUT_FILES=$outFile
    
'''
        
        return PROJECT_SCRIPT
