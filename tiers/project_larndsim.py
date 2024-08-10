import yaml, os, pathlib, shutil
import numpy as np
from yaml import Loader
from datetime import timedelta
from .project_base import project_base

class larndsim(project_base):


    def __init__(self):
        super().__init__()

        project_dict = dict(LARNDSIM_SIM_PROPERTIES='larndsim/simulation_properties/',
            LARNDSIM_SIM_PROPERTIES_EXT=os.path.join(pathlib.Path(__file__).parent.resolve(),'../config'),
            LARNDSIM_PIXEL_LAYOUT='larndsim/pixel_layouts/',
            LARNDSIM_DET_PROPERTIES='larndsim/detector_properties/',
            LARNDSIM_RESPONSE='larndsim/bin',
            LARNDSIM_LIGHT_LUT='larndsim/bin',
            LARNDSIM_LIGHT_DET_NOISE='larndsim/bin',
            LARNDSIM_LIGHT_SIMULATION=False,
            LARNDSIM_LIGHT_LUT_EXT="['/sdf/data/neutrino/2x2/light_lut/lightLUT_Mod0.npz', '/sdf/data/neutrino/2x2/light_lut/lightLUT_Mod123.npz']",
            LARNDSIM_CONFIG='2x2_mpvmpr',
            )

        self.REQUIRED.update(project_dict)


    def parse_project_config(self,cfg):

        super().parse_project_config(cfg)


    def gen_project_script(self,cfg):

        #
        # larnd-sim
        #
        cmd_larndsim = f'''{cfg['LARNDSIM_SCRIPT']} \
--config={cfg['LARNDSIM_CONFIG']} \
--simulation_properties={os.path.basename(cfg['LARNDSIM_SIM_PROPERTIES_EXT'])} \
--light_simulated={str(cfg['LARNDSIM_LIGHT_SIMULATION'])} \
--light_lut_filename="{cfg['LARNDSIM_LIGHT_LUT_EXT']}" \
--input_filename=$INPUT_FILES \
--output_filename={cfg['JOB_OUTPUT_ID']}-larndsim.h5 \
--save_memory=log_resources.h5 \
'''

        PROJECT_SCRIPT=f'''
date
echo "Running larnd-sim"
echo {cmd_larndsim}

{cmd_larndsim} &>> log_larndsim.txt

# for the next stage
INPUT_FILES={cfg['JOB_OUTPUT_ID']}-larndsim.h5
'''
        return PROJECT_SCRIPT
