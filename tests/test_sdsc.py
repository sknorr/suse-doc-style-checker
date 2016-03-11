import pytest

import os
import sdsc
from lxml import etree
        
def test_sdsc_version(capsys):
    """checks for output of sdsc --version"""
    with pytest.raises(SystemExit):
        sdsc.main(["--version"])
    out, err = capsys.readouterr()
    assert sdsc.__version__ == out.split()[-1]

# The xmltestcase fixture returns all files in tests/cases
def test_xml(xmltestcase):
    nr_errors = 0
    resultxml = sdsc.checkOneFile(xmltestcase)
    
    # Parse the input file and gather all ids
    inputtree = etree.parse(xmltestcase)
    inputids = []
    for elem in inputtree.getiterator():
        id = elem.get("id")
        if id != None:
            if not id.startswith("sdsc.test."):
                inputids.append(id)
    if len(inputids) == 0:
        pytest.skip("No tests found in {0}".format(os.path.basename(xmltestcase)))

    # Parse the result file and collect ids of errors and warnings
    resulttree = etree.fromstring(resultxml)
    warnings = {}
    errors = {}
    currentPartSource = ""
    for elem in resulttree.getiterator():
        if elem.tag == "part":
            currentPartSource = elem.get("source")
            warnings[currentPartSource] = []
            errors[currentPartSource] = []
        elif elem.tag == "result":
            elemType = elem.get("type", "info")
            if elemType == "info":
                continue

            withinid = elem.findtext("location/withinid")
            message = elem.find("message")
            if withinid == None:
                withinid = elem.findtext("message/id")
                if withinid == None:
                    pytest.fail("No withinid found")
            
            if elemType == "warning":
                warnings[currentPartSource].append({ 'id': withinid, 'message': etree.tostring(message, method="text") })

    # Isolate unexpected warnings
    for checkmodule, warnlist in warnings.items():
        for warning in warnlist:
            if not warning["id"].startswith("sdsc.expect.warning.{0}".format(checkmodule)):
                print("Unexpected warning {0!r} generated by module {1!r} for ID {2!r}".format(warning["message"], checkmodule, warning["id"]))
                nr_errors -= -1
    
    if nr_errors > 0:
        pytest.fail("Test failed with {0} errors!".format(nr_errors))