import yaml, os, pathlib, shutil
import numpy as np
from yaml import Loader
import larndsim
from datetime import timedelta
from project_base import project_base


REQUIRED = dict(GEOMETRY=os.path.join(pathlib.Path(__file__).parent.resolve(),'geometry'),
    MPVMPR=os.path.join(pathlib.Path(__file__).parent.resolve(),'config'),
    SIM_PROPERTIES='larndsim/simulation_properties/',
    PIXEL_LAYOUT='larndsim/pixel_layouts/',
    DET_PROPERTIES='larndsim/detector_properties/',
    RESPONSE='larndsim/bin',
    LIGHT_LUT='larndsim/bin',
    LIGHT_DET_NOISE='larndsim/bin',
    LIGHT_SIMULATION=False,
    FLOW_YAML=pathlib.Path(__file__).parent.resolve().as_posix(),
    )

class project_larndsim(project_base):

    def parse_project_config(self,cfg):

        cfg['G4_MACRO_PATH']=os.path.join(cfg['JOB_SOURCE_DIR'],'g4.mac')

        cfg['FLOW_YAML']=os.path.join(pathlib.Path(os.path.abspath(__file__)).parent.resolve(), cfg['FLOW_REPOSITORY'],'yamls')

        # Check required configuration files
        for word in REQUIRED.keys():
            opt1 = 'USE_' + word
            opt2 = 'SEARCH_' + word
            opt3 = 'SET_' + word

            duplicate = int(opt1 in cfg) + int(opt2 in cfg) + int(opt3 in cfg)
            if duplicate > 1:
                print(f'ERROR: only one of "USE"/"SEARCH"/"SET can be requested for {word}.')
                print(f'{opt1}: {cfg.get(opt1,None)}')
                print(f'{opt2}: {cfg.get(opt2,None)}')
                print(f'{opt2}: {cfg.get(opt3,None)}')
                raise ValueError('Please fix the configuration file.')
                
            if duplicate == 0:
                print(f'ERROR: keyword not found (need either USE_{word} or SEARCH_{word} or SET_{word})')
                print(f'{cfg}')
                raise ValueError('Please fix the configuration file.')

            # option 1: take the path specified by the user
            if opt1 in cfg:
                if not os.path.isfile(cfg[opt1]):
                    print(f'ERROR: {word} file not found at the specified location.')
                    print(f'       {cfg[opt1]}')
                    raise FileNotFoundError(f'{cfg[opt1]}')
                cfg[word]=cfg[opt1]

            # option 2: grab from larnd-sim repository
            if opt2 in cfg:
                if not 'LARNDSIM_REPOSITORY' in cfg:
                    print(f'ERROR: to SEARCH {word}, you must provide LARNDSIM_REPOSITORY in the config.')
                    raise ValueError('Please add local larnd-sim installation path to LARNDSIM_REPOSITORY in the config')

                path = os.path.join(REQUIRED[word],cfg[opt2])
                print("path: ", path)
                if not path.startswith('/'):
                    path = os.path.join(cfg['LARNDSIM_REPOSITORY'],path)

                if not os.path.isfile(path) and not os.path.isdir(path):
                    print(f'Searched a file {cfg[opt2]} but not found...')
                    raise FileNotFoundError(f'{path}')

                cfg[word]=path

            # option 3: set the option to the specified value w/o check
            if opt3 in cfg:
                cfg[word]=cfg[opt3]

    def gen_project_script(self,cfg):

        macro = self.gen_g4macro(os.path.basename(cfg['MPVMPR']))
        with open(cfg['G4_MACRO_PATH'],'w') as f:
            f.write(macro)
            f.close()
        self.gen_job_script(cfg)

        for key in REQUIRED.keys():
            print("key: ", key)
            print("type(REQUIRED[key]) ", type(REQUIRED[key]))
            if type(REQUIRED[key]) == str:
                self.COPY_FILES.append(cfg[key])


    def gen_g4macro(self, mpv_config):
        macro=f'''
/edep/hitSeparation TPCActive_shape -1 mm
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

    def gen_flow_script(self, cfg):

        macro=f'''

scp {cfg['FLOW_REPOSITORY']}/yamls .

pwd

inFile={cfg['JOB_OUTPUT_ID']}-larndsim.h5

outFile={cfg['JOB_OUTPUT_ID']}-flow.h5
#outFile={cfg['STORAGE_DIR']}/{cfg['JOB_WORK_DIR']}/{cfg['JOB_OUTPUT_ID']}-flow.h5

echo $inFile
echo $outFile

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

h5flow -c $workflow1 $workflow2 $workflow3 $workflow4 $workflow5\
    -i $inFile -o $outFile

h5flow -c $workflow6 $workflow7\
    -i $inFile -o $outFile

h5flow -c $workflow8\
    -i $outFile -o $outFile

        '''
        return macro


    def gen_job_script(self, cfg):

        cmd_edepsim = f'''edep-sim \
-g {os.path.basename(cfg['GEOMETRY'])} \
-e {int(cfg['NUM_EVENTS'])} \
-o {cfg['JOB_OUTPUT_ID']}-edepsim.root \
{os.path.basename(cfg['G4_MACRO_PATH'])} \
'''

        cmd_dumptree = f'''dumpTree.py \
    {cfg['JOB_OUTPUT_ID']}-edepsim.root {cfg['JOB_OUTPUT_ID']}-edepsim.h5 \
'''

        cmd_larndsim = f'''{cfg['LARNDSIM_SCRIPT']} \
--simulation_properties={os.path.basename(cfg['SIM_PROPERTIES'])} \
--pixel_layout={os.path.basename(cfg['PIXEL_LAYOUT'])} \
--detector_properties={os.path.basename(cfg['DET_PROPERTIES'])} \
--response_file={os.path.basename(cfg['RESPONSE'])} \
--light_lut_filename={os.path.basename(cfg['LIGHT_LUT'])} \
--light_det_noise_filename={os.path.basename(cfg['LIGHT_DET_NOISE'])} \
--light_simulated={str(cfg['LIGHT_SIMULATION'])} \
--input_filename={cfg['JOB_OUTPUT_ID']}-edepsim.h5 \
--output_filename={cfg['JOB_OUTPUT_ID']}-larndsim.h5 \
--save_memory=log_resources.h5 \
'''

        cmd_flow = self.gen_flow_script(cfg)

        self.PROJECT_SCRIPT=f'''#!/bin/bash
date
echo "starting a job"

export PATH=$HOME/.local/bin:$PATH

nvidia-smi &> jobinfo_gpu.txt

OUTPUT_NAME={cfg['JOB_OUTPUT_ID']}


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

date
echo "Running ndlar_flow"

echo {cmd_flow}

{cmd_flow} &>> log_flow.txt

date
echo "Removing the response file..."
rm {os.path.basename(cfg['RESPONSE'])}

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
