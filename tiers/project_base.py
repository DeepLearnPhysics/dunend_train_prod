import yaml, os, pathlib, shutil
import numpy as np
from yaml import Loader
from datetime import timedelta
import warnings, subprocess


class project_base():

    def __init__(self):
        self.COPY_FILES=[]
        self.REQUIRED={}

    def parse_project_config(self,cfg):
        '''
        Function to be implemented, but should be called with super().parse_project_config(cfg)
        in the child clss.
        cfg is a configuration dictionary.
        Parse configuration as necessary.
        '''

        # Check required configuration files
        for word in self.REQUIRED.keys():
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

                if word.startswith('LARNDSIM'):
                    if not 'LARNDSIM_REPOSITORY' in cfg:
                        print(f'ERROR: to SEARCH {word}, you must provide LARNDSIM_REPOSITORY in the config.')
                        raise ValueError('Please add local larnd-sim installation path to LARNDSIM_REPOSITORY in the config')

                    if not path.startswith('/'):
                        path = os.path.join(cfg['LARNDSIM_REPOSITORY'],path)

                if not os.path.isfile(path) and not os.path.isdir(path):
                    print(f'Searched a file {cfg[opt2]} but not found...')
                    raise FileNotFoundError(f'{path}')

                cfg[word]=path

            # option 3: set the option to the specified value w/o check
            if opt3 in cfg:
                cfg[word]=cfg[opt3]


        # Register required file to the list to be copied
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

        return


    def gen_project_script(self,cfg):
        '''
        Function to be implemented.
        cfg is a configuration dictionary.
        Fill the list of files to be copied to self.COPY_FILES.
        Those files will be available under the job directory with the same name.
        Return the contents of a project script and return (as a string)
        '''
        pass


