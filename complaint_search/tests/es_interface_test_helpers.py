# -------------------------------------------------------------------------
# Helper Methods
# -------------------------------------------------------------------------


def to_absolute(fileName):
    import os.path
    # where is this module?
    thisDir = os.path.dirname(__file__)
    return os.path.join(thisDir, "expected_results", fileName)


def load(shortName):
    import json
    fileName = to_absolute(shortName + '.json')
    with open(fileName, 'r') as f:
        return json.load(f)
