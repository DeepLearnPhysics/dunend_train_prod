import yaml, os, pathlib, shutil
import numpy as np
from yaml import Loader
import larndsim
import flow2supera
from datetime import timedelta
from project_base import project_base


REQUIRED = dict(GEOMETRY=os.path.join(pathlib.Path(__file__).parent.resolve(),'geometry'),
    MPVMPR=os.path.join(pathlib.Path(__file__).parent.resolve(),'config'),
    LARNDSIM_SIM_PROPERTIES='larndsim/simulation_properties/',
    LARNDSIM_SIM_PROPERTIES_EXT=os.path.join(pathlib.Path(__file__).parent.resolve(),'config'),
    LARNDSIM_PIXEL_LAYOUT='larndsim/pixel_layouts/',
    LARNDSIM_DET_PROPERTIES='larndsim/detector_properties/',
    LARNDSIM_RESPONSE='larndsim/bin',
    LARNDSIM_LIGHT_LUT='larndsim/bin',
    LARNDSIM_LIGHT_DET_NOISE='larndsim/bin',
    LARNDSIM_LIGHT_SIMULATION=False,
    LARNDSIM_LIGHT_LUT_EXT="['/sdf/data/neutrino/2x2/light_lut/lightLUT_Mod0.npz', '/sdf/data/neutrino/2x2/light_lut/lightLUT_Mod123.npz']",
    LARNDSIM_CONFIG='2x2_mpvmpr',
    FLOW_YAML=pathlib.Path(__file__).parent.resolve().as_posix(),
    FLOW_DATA=pathlib.Path(__file__).parent.resolve().as_posix(),
    )

class project_larndsim(project_base):


    def __init__(self):
        super().__init__()

        project_dict = dict(LARNDSIM_SIM_PROPERTIES='larndsim/simulation_properties/',
            LARNDSIM_SIM_PROPERTIES_EXT=os.path.join(pathlib.Path(__file__).parent.resolve(),'config'),
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


        cfg['FLOW_YAML']=os.path.join(pathlib.Path(os.path.abspath(__file__)).parent.resolve(), cfg['FLOW_REPOSITORY'],'yamls')
        cfg['FLOW_DATA']=os.path.join(pathlib.Path(os.path.abspath(__file__)).parent.resolve(), cfg['FLOW_REPOSITORY'],'data')


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

        macro = self.gen_g4macro(os.path.basename(cfg['MPVMPR']))
        with open(cfg['G4_MACRO_PATH'],'w') as f:
            f.write(macro)
            f.close()
        self.gen_job_script(cfg)

        for key in REQUIRED.keys():
            if type(REQUIRED[key]) == str:
                if key.startswith("LARNDSIM_") and not key.endswith("_EXT"):
                    continue
                else:
                    if isinstance(cfg[key], list):
                        for i_f, f in enumerate(cfg[key]):
                            self.COPY_FILES.append(f)
                            cfg[key][i_f] = os.path.basename(f)
                    elif os.path.exists(cfg[key]):
                        self.COPY_FILES.append(cfg[key])


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


    def gen_job_script(self, cfg):

        #
        # edep-sim
        #
        cmd_edepsim = f'''edep-sim \
-g {os.path.basename(cfg['GEOMETRY'])} \
-e {int(cfg['NUM_EVENTS'])} \
-o {cfg['JOB_OUTPUT_ID']}-edepsim.root \
{os.path.basename(cfg['G4_MACRO_PATH'])} \
'''

        #
        # dumptree
        #
        cmd_dumptree = f'''dumpTree.py \
    {cfg['JOB_OUTPUT_ID']}-edepsim.root {cfg['JOB_OUTPUT_ID']}-edepsim.h5 \
'''

        #
        # larnd-sim
        #
        cmd_larndsim = f'''{cfg['LARNDSIM_SCRIPT']} \
--config={cfg['LARNDSIM_CONFIG']} \
--simulation_properties={os.path.basename(cfg['LARNDSIM_SIM_PROPERTIES_EXT'])} \
--light_simulated={str(cfg['LARNDSIM_LIGHT_SIMULATION'])} \
--light_lut_filename="{cfg['LARNDSIM_LIGHT_LUT_EXT']}" \
--input_filename={cfg['JOB_OUTPUT_ID']}-edepsim.h5 \
--output_filename={cfg['JOB_OUTPUT_ID']}-larndsim.h5 \
--save_memory=log_resources.h5 \
'''
        #
        # Flow
        #
        cmd_flow_def = f'''

inFile={cfg['JOB_OUTPUT_ID']}-larndsim.h5

outFile={cfg['JOB_OUTPUT_ID']}-flow.h5

# charge workflows
workflow1='yamls/proto_nd_flow/workflows/charge/charge_event_building.yaml'
workflow2='yamls/proto_nd_flow/workflows/charge/charge_event_reconstruction.yaml'
workflow3='yamls/proto_nd_flow/workflows/combined/combined_reconstruction.yaml'
workflow4='yamls/proto_nd_flow/workflows/charge/prompt_calibration.yaml'
workflow5='yamls/proto_nd_flow/workflows/charge/final_calibration.yaml'

# light workflows
workflow6='yamls/proto_nd_flow/workflows/light/light_event_building_mc.yaml'
workflow7='yamls/proto_nd_flow/workflows/light/light_event_reconstruction.yaml'

# charge-light trigger matching
workflow8='yamls/proto_nd_flow/workflows/charge/charge_light_assoc.yaml'

        '''

        cmd_flow_charge = 'h5flow -c $workflow1 $workflow2 $workflow3 $workflow4 -i $inFile -o $outFile'
        cmd_flow_light = 'h5flow -c $workflow6 $workflow7 -i $inFile -o $outFile'
        cmd_flow_charge_light = 'h5flow -c $workflow8 -i $outFile -o $outFile'

        #
        # Supera
        #
        cmd_supera = f'''run_flow2supera.py \
-o {cfg['JOB_OUTPUT_ID']}-larcv.root \
-c {cfg['SUPERA_CONFIG']} \
{cfg['JOB_OUTPUT_ID']}-flow.h5'''

        self.PROJECT_SCRIPT=f'''#!/bin/bash
date
echo "starting a job"

export PATH=$HOME/.local/bin:$PATH

nvidia-smi &> jobinfo_gpu.txt

OUTPUT_NAME={cfg['JOB_OUTPUT_ID']}
'''
        if 'LARCV_DIR' in cfg:
            self.PROJECT_SCRIPT += f'''

echo "Using larcv from {cfg['LARCV_DIR']}"
source {cfg['LARCV_DIR']}/configure.sh

'''

        self.PROJECT_SCRIPT += f'''

date
echo "Running edep-sim"

echo {cmd_edepsim}

{cmd_edepsim} &>> log_edepsim.txt


date
echo "Running dumpTree"

echo {cmd_dumptree}

{cmd_dumptree} &>> log_dumptree.txt


date
echo "Running larnd-sim"

echo {cmd_larndsim}

{cmd_larndsim} &>> log_larndsim.txt

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

date
echo "Running Supera"
echo {cmd_supera} 
{cmd_supera} &> log_supera.txt

date
echo "Removing the some configuration files..."
rm -f lightLUT_Mod*.npz

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

    p=project_larndsim()
    p.generate(sys.argv[1])
    sys.exit(0)
