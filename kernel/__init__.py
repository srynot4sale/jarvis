import kernel
import data
import functions
import interfaces

def init(config):
    ## Initialise jarvis kernel
    jarvis = kernel.kernel(config)

    ## Connect to data source
    jarvis.register('data', data.init(jarvis))

    ## Initialise functions
    jarvis.register('function', functions.init())

    ## Boot up interfaces
    jarvis.register('interface', interfaces.init(jarvis))

    return jarvis
