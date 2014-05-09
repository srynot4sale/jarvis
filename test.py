import subprocess
import time
import logging
log = logging.getLogger(__name__)

server = None
def setup_function():
    global server
    log.info('Run setup')
    server = subprocess.Popen(["python", "start_server.py", "--test"])

    tries = 0
    sleep = 0.1
    while 1:
        if tries > 20:
            log.info('Exceeded 20 tries')
            break
        try:
            tries += 1
            make_request('server connect')
            log.info('Server up after %d tries' % tries)
            break
        except:
            time.sleep(sleep)
            continue


def teardown_function():
    log.info('Run teardown')
    server.kill()
