"""
python:
>> import odcblib.types

Файл создан 30.10.2024 в 23:33:35

~//types.py
"""

__author__ = 'pavelmstu'
__copyright__ = 'KIB, 2024'
__license__ = 'LGPL'
__credits__ = [
    'pavelmstu',
]
__version__ = "20241030"
# __status__ = "Develop"
__status__ = "Production"

import uuid

HASH = str

SIGN = bytes

KEY = bytes

# WID - wallet id
WID = uuid.UUID