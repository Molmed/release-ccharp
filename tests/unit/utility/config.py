import os


def load_chiasma_config():
    here = os.path.dirname(__file__)
    with open(os.path.join(here, 'chiasma.exe.config'), 'r') as f:
        content = f.read()
    return content

def load_sqat_connect():
    here = os.path.dirname(__file__)
    with open(os.path.join(here, 'SQATconnect.xml'), 'r') as f:
        content = f.read()
    return content


CHIASMA_CONFIG = load_chiasma_config()

SQAT_CONNECT = load_sqat_connect()
