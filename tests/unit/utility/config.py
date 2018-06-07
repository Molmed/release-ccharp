import os


def load_chiasma_config():
    return _load_file('chiasma.exe.config')


def load_chiasma_deposit_config():
    return _load_file('chiasma_deposit.exe.config')


def load_sqat_connect():
    return _load_file('SQATconnect.xml')


def load_fp_config():
    return _load_file('FPDatabase.exe.config')


def load_fp_connect_config():
    return _load_file('FPDatabaseConfig.txt')


def _load_file(file_name):
    here = os.path.dirname(__file__)
    resources = os.path.join(here, 'resources')
    with open(os.path.join(resources, file_name), 'r') as f:
        content = f.read()
    return content


CHIASMA_CONFIG = load_chiasma_config()

CHIASMA_DEPOSIT_CONFIG = load_chiasma_deposit_config()

SQAT_CONNECT = load_sqat_connect()

FP_CONFIG = load_fp_config()

FP_CONNECT_CONFIG = load_fp_connect_config()
