import importlib.util
import os
from pathlib import Path
ROOT=Path(__file__).resolve().parent

def load(name):
    mode=os.environ.get('INTERVIEW_LAB_MODE','exercises')
    if mode not in ('exercises','solutions'):
        raise ValueError('invalid lab mode')
    spec=importlib.util.spec_from_file_location('candidate_'+name,ROOT/mode/(name+'.py'))
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
