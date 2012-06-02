import kernel
import data
import functions
import interfaces

config = {}

def init():
    ## Initialise jarvis kernel
    jarvis = kernel.kernel()

    ## Startup daemon process

    ## Connect to data source
    jarvis.register('data', data.init(jarvis))

    ## Initialise functions
    jarvis.register('function', functions.init())

    ## Boot up interfaces
    jarvis.register('interface', interfaces.init(jarvis))

    ## Connect to io streams
    print jarvis.call('calendar', 'event_list')

    return


def setConfig(key, value):
    config[key] = value


def getConfig(key):
    return config[key]
