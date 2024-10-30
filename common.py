"""
odcblib -- стандартная библиотека для импортирования функций

>> import odcblib.common

Файл создан 31.10.2024 в 00:24:46

~//common.py
"""

__author__ = 'pavelmstu'
__copyright__ = 'KIB, 2024'
__license__ = 'LGPL'
__credits__ = [
    'pavelmstu',
]
__version__ = "20241031"
__status__ = "Production"


from random import random




def make_salt():
    return random.getrandbits(64).to_bytes().hex()
