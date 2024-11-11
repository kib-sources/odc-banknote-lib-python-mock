"""
odcblib -- стандартная библиотека для импортирования функций

> cd <ваш проект на Python>
> git clone git@github.com:kib-sources/odc-banknote-lib-python-mock.git odcblib

python:
>> import odcblib


Файл создан 30.10.2024 в 22:49:38

~//odcblib.py
"""

__author__ = 'pavelmstu'
__copyright__ = 'KIB, 2024'
__license__ = 'LGPL'
__credits__ = [
    'pavelmstu',
]
__version__ = "20241030"
__status__ = "Develop"
# __status__ = "Production"


import os
import uuid
from dataclasses import dataclass
from typing import List, Optional
import dill

from types_ import KEY
from banknote_blocks import OdcbBlockChain, OdcbBlockHeader, OdcbBlockApplicability
from banknote_blocks import ODCB_FILE_PREFIX, ODCB_FILE_VERSION

from bank import Bank

_odcb_mock_version = "2.0-python-mock"


def lib_version():
    # return "2024.10"
    return "2024.10-mock"

def supported_odcb_versions() -> List[str]:
    return [
        _odcb_mock_version
    ]




class OdcBanknote:
    """
    Файл *.odcb
    Вернее его Mock, конечно...
    """

    # self._header
    # self._chain

    def __init__(
        self,
        header: OdcbBlockHeader,
        chain: Optional[List[OdcbBlockChain]] = None,
    ):
        if chain is None:
            chain = list()
        self._header = header
        self._chain = chain

    @classmethod
    def make(
            cls,
            *,
            bank: Bank,
            code: str,
            amount: int,
            banknote_id: Optional[uuid.UUID]=None,
            applicabilities: Optional[List[str]]=None,
    ):
        if applicabilities is None:
            applicabilities = [
                "ALL-0000-0000000"
            ]

        if len(applicabilities) > 1:
            raise NotImplementedError("Пока не поддерживаем много блоков APPLICABILITIES... :( Укажите один")

        header = bank.init_odcb_block_header(
            banknote_id=banknote_id,
            code=code,
            amount=amount,
            first_applicability=applicabilities[0],
            count_append_applicability_blocks=len(applicabilities)-1,
        )

        _obj = cls(
            header=header,
            chain=list()
        )

        return _obj

    @classmethod
    def load(cls, path):
        assert path.endswith(".odcb")
        with open(path, "rb") as fr:
            file_data = fr.read()
            odbc_file_prefix = file_data[0:len(ODCB_FILE_PREFIX)]
            assert odbc_file_prefix == ODCB_FILE_PREFIX.encode('ascii')

            odbc_file_version = file_data[len(ODCB_FILE_PREFIX):len(ODCB_FILE_PREFIX)+len(ODCB_FILE_VERSION)]
            assert odbc_file_version == ODCB_FILE_VERSION.encode('ascii')

            banknote_data = file_data[len(ODCB_FILE_PREFIX)+len(ODCB_FILE_VERSION):]
            _obj = dill.loads(banknote_data)
            assert isinstance(_obj, OdcBanknote)

            return _obj

    def save(self, path):
        assert path.endswith(".odcb")
        with open(path, "wb") as fw:
            banknote_data = dill.dumps(self)

            file_data = ODCB_FILE_PREFIX.encode('ascii') + ODCB_FILE_VERSION.encode('ascii') + banknote_data

            fw.write(file_data)


    def __eq__(self, other):
        if not isinstance(other, OdcBanknote):
            return False

        if self._header.bank_id != other._header.bank_id:
            return False
        if self._header.banknote_id != other._header.banknote_id:
            return False
        return True