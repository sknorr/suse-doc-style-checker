import glob
import os

def pytest_generate_tests(metafunc):
    """Replace the xmltestcases fixture by all files in tests/cases """
    if 'xmltestcase' in metafunc.fixturenames:
        location = os.path.dirname(os.path.realpath(__file__))
        testcases = glob.glob(location + "/cases/*")
        testcases.sort() # Sort them alphabetically
        metafunc.parametrize("xmltestcase", testcases)