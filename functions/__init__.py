# Jarvis functions
import importlib
import os.path
import sys

def init():
    funcs = []

    # Get current directory
    path  = os.path.abspath(os.path.dirname(__file__))
    files = os.listdir(path)

    for m in sorted(files):
        module, ext = os.path.splitext(m)
        fullmodule = 'functions.%s' % module

        # Ignore this file
        if module == '__init__':
            continue

        # Ensure that it's a python file and that the module isn't already loaded
        if ext != '.py' or fullmodule in sys.modules:
            continue

        # Import module
        loaded_mod = importlib.import_module(fullmodule)

        # Initialise module and register with kernel
        funcs.append(loaded_mod.controller(module))

    return funcs
