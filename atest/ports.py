import time


def _get_three_least_significant_digits_from_current_time():
    return int(str(time.time())[-4:].replace('.', ''))

_base = _get_three_least_significant_digits_from_current_time()

SERVER_PORT = 54000 + _base
SERVER_PORT_2 = 55000 + _base
CLIENT_1_PORT = 44000 + _base
CLIENT_2_PORT = 45000 + _base
