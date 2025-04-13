"""
clib -- библиотека odc-bancnote-core,
которая доллжна быть написана на Си

Файл создан 13.04.2025 в 15:05:09

~//clib.py
"""

__author__ = 'pavelmstu'
__copyright__ = 'KIB, 2025'
__license__ = 'LGPL'
__credits__ = [
    'pavelmstu',
]
__version__ = "20250413"
__status__ = "Develop"

# __status__ = "Production"


def c_core(some):
    """
    Декоратор, указывающий, что данная функция должны быть в clib
    :return:
    """
    return some