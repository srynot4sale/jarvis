import logging, os.path, re, subprocess, time

## Test suite setup and teardown functionality
log = logging.getLogger(__name__)

server = None
def setup_function():
    global server
    log.info('Run setup')
    null = open('/dev/null', 'w')
    server = subprocess.Popen(["python", "start_server.py", "--test"], stdout=null, stderr=null)

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


## Test coverage
def test_coverage():
    matches = subprocess.check_output(["""grep -RE -o 'class action_(.*)\(' functions/ | grep -vi test"""], shell=True)
    for match in matches.split('\n'):
        if not match.strip():
            continue
        match = re.search('functions/([a-z0-9]+)\.py\:class action_([a-z0-9_]+)\(', match)
        if not match:
            continue
        function = match.group(1)
        action = match.group(2)

        testfile = 'functions/tests/%s_test.py' % function
        if not os.path.isfile(testfile):
            print('%s %s - No test file exists! Expecting %s' % (function, action, testfile))
            continue

        try:
            res = """grep -RE -o '^\s*\!Tests\:\s+%s_%s$' %s""" % (function, action, testfile)
            tests = subprocess.check_output([res], shell=True)
            count = len(tests.strip().split('\n'))
        except:
            count = 0

        print('%s %s - %d tests' % (function, action, count))



if __name__ == "__main__":
    print("Run test coverage:")
    print('')
    test_coverage()
