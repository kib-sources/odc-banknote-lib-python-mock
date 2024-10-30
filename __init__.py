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

from .types import KEY
from .banknote_blocks import OdcbBlockChain, OdcbBlockHeader, OdcbBlockApplicability

from .common import make_salt

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

    def __init__(
            self,
            bank_id: str,
            banknote_id: uuid.UUID,
            bok: KEY,
            code: str,
            amount: int,
            applicabilities: Optional[List[str]]
    ):
        if applicabilities is None:
            applicabilities = [
                "ALL-0000-0000000"
            ]

        self.header = OdcbBlockHeader(
            bank_id=bank_id,
            banknote_id=banknote_id,
            bok=bok,
            applicability=applicabilities[0],
            count_append_applicability_blocks=len(applicabilities)-1,
            sign_algorithm="RSA-4096............",
            hash_algorithm="SHA-512.............",
            salt=make_salt(),
        )

        raise NotImplementedError("Нужно дописать вычисление hash")

        if len(applicabilities)>0:
            for applicability in applicabilities[1:]:
                self.applicability_list = OdcbBlockApplicability(
                    bank_id=bank_id,
                    banknote_id=banknote_id,
                    applicability=applicability,
                )
        self.chain = list()

        pass

    @classmethod
    def load(cls, path):
        assert path.endswith(".odcb")
        return OdcBanknote()

    def save(self, path):
        assert path.endswith(".odcb")
        with open(path, "w") as odcb:
            pass

