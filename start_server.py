import config

import pkg_resources
from pkg_resources import DistributionNotFound, VersionConflict
import sys

#
# config.py is expected to contain:
#
# config = {}
# config['database_host']         = 'localhost'
# config['database_username']     = 'jarvis'
# config['database_password']     = 'password'
# config['interface_http_port']   = 'XXXX'
# config['username']              = 'My Name'
# config['secret']                = 'secrethash'
#

## Check dependencies
with open('requirements.txt') as dependencies:
    try:
        pkg_resources.require(dependencies)
    except (DistributionNotFound, VersionConflict) as e:
        print('ERROR: dependencies not satisified')
        print('Are you sure you are running this inside virtualenv?')
        print('')
        print('To do so, run:')
        print('\tsource env/bin/activate')
        print('')
        print('If that doesn\'t fix it, update dependencies:')
        print('\tpip install -r requirements.txt')
        print('')
        print('Failed dependencies were:')
        print('\t%s' % e)
        print('')
        sys.exit('Dependency error')

## Initialise Jarvis kernel
import kernel

jarvis = kernel.init(config.config)
