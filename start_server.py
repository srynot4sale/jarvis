#! bin/python
import config

import pkg_resources
from pkg_resources import DistributionNotFound, VersionConflict
import sys

## Check dependencies
with open('requirements.txt') as dependencies:
    try:
        pkg_resources.require(dependencies)
    except (DistributionNotFound, VersionConflict) as e:
        print('ERROR: dependencies not satisified')
        print('Are you sure you are running this inside virtualenv?')
        print('')
        print('To do so, run this script as so:')
        print('\t~/code/jarvis-src/start_server.py')
        print('')
        print('If that doesn\'t fix it, update dependencies:')
        print('\tsource bin/activate')
        print('\tpip install -r requirements.txt')
        print('')
        print('Failed dependencies were:')
        print('\t%s' % e)
        print('')
        sys.exit('Dependency error')

## Check config
import config_example
conf_required   = set(config_example.config)
conf_set        = set(config.config)
if conf_required != conf_set and not conf_required.issubset(conf_set):
    print('ERROR: some config variables appear to be missing')
    print('All config variables uncommented in config_example.py are requred.')
    print('')
    print('Mising config entries: %s' % ', '.join(conf_required.difference(conf_set)))
    print('')
    sys.exit('Configuration error')


## Initialise Jarvis kernel
import kernel
jarvis = kernel.init(config.config)
jarvis.start()
