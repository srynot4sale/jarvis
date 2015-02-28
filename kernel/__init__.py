import kernel
import data

import importlib
import os.path
import sys


def init(config):
    ## Initialise jarvis kernel
    jarvis = kernel.kernel(config)

    ## Connect to data source
    jarvis.register('data', data.init(jarvis))

    ## Initialise functions
    jarvis.register('function', load_modules('functions'))

    ## Set up interfaces
    jarvis.register('interface', load_modules('interfaces'))

    ## Finish setup
    jarvis.setup()

    return jarvis


def load_modules(location):
    funcs = []

    # Get current directory
    path  = os.path.abspath(os.path.join(
        os.path.dirname(__file__), '..', location))
    files = os.listdir(path)

    for m in sorted(files):
        module, ext = os.path.splitext(m)
        fullmodule = '%s.%s' % (location, module)

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
