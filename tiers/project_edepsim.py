import yaml, os, pathlib, shutil
import numpy as np
from yaml import Loader
from datetime import timedelta
from .project_base import project_base

class edepsim(project_base):


    def __init__(self):
        super().__init__()

        project_dict = dict(GEOMETRY=os.path.join(self.FMWK_DIR,'geometry'),
            MPVMPR=os.path.join(self.FMWK_DIR,'config'),
            )        
        self.REQUIRED.update(project_dict)

        
    def parse_project_config(self,cfg):
        super().parse_project_config(cfg)


    def gen_project_script(self,cfg):

        macro = self.gen_g4macro(os.path.basename(cfg['MPVMPR']))
        macro_path = os.path.join(cfg['JOB_SOURCE_DIR'],'g4.mac')
        with open(macro_path,'w') as f:
            f.write(macro)
            f.close()

        # Define the core command
        cmd_edepsim = f'''edep-sim \
-g {os.path.basename(cfg['GEOMETRY'])} \
-e {int(cfg['NUM_EVENTS'])} \
-o {cfg['JOB_OUTPUT_ID']}-edepsim.root \
g4.mac \
'''

        cmd_dumptree = f'''dumpTree.py \
    {cfg['JOB_OUTPUT_ID']}-edepsim.root {cfg['JOB_OUTPUT_ID']}-edepsim.h5 \
'''

        # Fill the key attribute
        PROJECT_SCRIPT = f'''

date
echo "Running edep-sim"
echo {cmd_edepsim}
{cmd_edepsim} &>> log_edepsim.txt

date
echo "Running dumpTree"
echo {cmd_dumptree}
{cmd_dumptree} &>> log_dumpTree.txt

# for the next stage
INPUT_FILES={cfg['JOB_OUTPUT_ID']}-edepsim.h5

'''
        return PROJECT_SCRIPT

    def gen_g4macro(self, mpv_config):
        macro=f'''
/edep/hitSeparation volTPCActive -1 mm
/edep/hitSagitta drift 1.0 mm
/edep/hitLength drift 1.0 mm
/edep/db/set/neutronThreshold 0 MeV
/edep/db/set/lengthThreshold 0 mm
/edep/db/set/gammaThreshold 0 MeV
/edep/random/timeRandomSeed
/edep/update

/generator/kinematics/bomb/config {mpv_config}
/generator/kinematics/bomb/verbose 0
/generator/kinematics/set bomb 

/generator/count/fixed/number 1
/generator/count/set fixed
/generator/add

        '''
        return macro
