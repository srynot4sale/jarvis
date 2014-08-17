import logging, os.path, re, subprocess, time

## Test suite setup and teardown functionality
log = logging.getLogger(__name__)

server = None
def setup_function():
    global server
    log.info('Run setup')

    # Open file descriptor for /dev/null so we can pipe stdout and sterr to it
    null = open('/dev/null', 'w')

    # Open test instance of server, which resets database on load
    server = subprocess.Popen(["python", "start_server.py", "--test"], stdout=null, stderr=null)

    # The server takes a while to come up, so we'll hit it a few times until we get a proper response
    tries = 0
    sleep = 0.1
    while 1:
        if tries > 20:
            log.info('Exceeded 20 tries')
            break
        try:
            tries += 1
            make_request('server menu')
            log.info('Server up after %d tries' % tries)
            break
        except:
            time.sleep(sleep)
            continue


def teardown_function():
    log.info('Run teardown')

    # Kill server test instance
    server.kill()


## Test coverage
def test_coverage():
    # Search for classes starting with action_ in the functions subdir
    matches = subprocess.check_output(["""grep -RE -o 'class action_(.*)\(.*\)' functions/ | grep -vi test"""], shell=True)
    for match in matches.split('\n'):
        if not match.strip():
            continue
        # Now pull out the function, action and a parentclass
        match = re.search('functions/([a-z0-9]+)\.py\:class action_([a-z0-9_]+)\((.*)\)', match)
        if not match:
            continue
        function = match.group(1)
        action = match.group(2)
        parentclass = match.group(3)[7:] if match.group(3)[0:7] == 'action_' else None

        # We expect this action's tests to be in the following location
        testfile = 'functions/tests/%s_test.py' % function
        if not os.path.isfile(testfile):
            count = 0
        else:
            try:
                # In the file, search for the magic string "Tests: $function_$action"
                res = """grep -RE -o '^\s*\!Tests\:\s+%s_%s$' %s""" % (function, action, testfile)
                tests = subprocess.check_output([res], shell=True)
                count = len(tests.strip().split('\n'))
            except:
                count = 0

        if parentclass:
            action += ' (%s)' % parentclass
        print('%s %s - %d tests' % (function, action, count))



if __name__ == "__main__":
    print("Run test coverage:")
    print('')
    test_coverage()
