import os


def load_order_config():
    return _load_file('Order.exe.config')


def load_chiasma_config():
    return _load_file('chiasma.exe.config')


def load_chiasma_shared_kernel_config():
    return _load_file('chiasma.sharedkernel.exe.config')


def load_chiama_config_replacement_test():
    return _load_file('chiasma.exe.config.replacetest')


def load_chiama_config_transformed():
    return _load_file('chiasma.exe.config.transformed')


def load_chiasma_deposit_config():
    return _load_file('chiasma_deposit.exe.config')


def load_sqat_connect():
    return _load_file('SQATconnect.xml')


def load_fp_config():
    return _load_file('FPDatabase.exe.config')


def load_fp_connect_config():
    return _load_file('FPDatabaseConfig.txt')


def load_sqat_exe_config():
    return _load_file('sqat.exe.config')


def _load_file(file_name):
    here = os.path.dirname(__file__)
    resources = os.path.join(here, 'resources')
    with open(os.path.join(resources, file_name), 'r') as f:
        content = f.read()
    return content


ORDER_CONFIG = load_order_config()

CHIASMA_CONFIG = load_chiasma_config()

CHIASMA_SHAREDKERNEL_CONFIG = load_chiasma_shared_kernel_config()

CHIASMA_CONFIG_REPLACE_TEST = load_chiama_config_replacement_test()

CHIASMA_CONFIG_TRANSFORMED = load_chiama_config_transformed()

CHIASMA_DEPOSIT_CONFIG = load_chiasma_deposit_config()

SQAT_CONNECT = load_sqat_connect()

SQAT_EXE_CONFIG = load_sqat_exe_config()

FP_CONFIG = load_fp_config()

FP_CONNECT_CONFIG = load_fp_connect_config()
