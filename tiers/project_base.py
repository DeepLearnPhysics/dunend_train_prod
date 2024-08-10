import yaml, os, pathlib, shutil
import numpy as np
from yaml import Loader
from datetime import timedelta
import warnings, subprocess

class project_base():

    def __init__(self):
        TIERS_DIR=pathlib.Path(__file__).parent.resolve().as_posix()
        self.FMWK_DIR=pathlib.Path(TIERS_DIR).parent.resolve().as_posix()
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

                parent_path = self.REQUIRED[word]

                software_repos = dict(LARNDSIM=os.path.join(self.FMWK_DIR,'modules','larnd-sim'),
                                      FLOW=os.path.join(self.FMWK_DIR,'modules','ndlar_flow'),
                                      )

                for software, default_repo in software_repos.items():
                
                    if word.startswith(software):
                        repository_path = default_repo
                        repo_keyword = software + '_REPOSITORY'
                        if repo_keyword in cfg:
                            repository_path = cfg[repo_keyword]
                        if not os.path.isdir(repository_path):                    
                            print(f'ERROR: to SEARCH {word}, you must provide a valid {repo_keyword} in the config.')
                            raise ValueError(f'Please add local larnd-sim installation path to {repo_keyword} in the config')
                        parent_path = os.path.join(repository_path,parent_path)

                path = os.path.join(parent_path,cfg[opt2])
                
                if not os.path.isfile(path) and not os.path.isdir(path):
                    print(f'Searched a file {cfg[opt2]} but not found...')
                    raise FileNotFoundError(f'{path}')

                cfg[word]=path

            # option 3: set the option to the specified value w/o check
            if opt3 in cfg:
                cfg[word]=cfg[opt3]


        # Register required file to the list to be copied
        for key in self.REQUIRED.keys():
            if type(self.REQUIRED[key]) == str:
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


