"""
Описание банка

Файл создан 11.11.2024 в 12:19:12

~//bank.py
"""

__author__ = 'pavelmstu'
__copyright__ = 'KIB, 2024'
__license__ = 'LGPL'
__credits__ = [
    'pavelmstu',
]
__version__ = "20241111"
__status__ = "Develop"
# __status__ = "Production"

import json
import uuid
from typing import List, Optional

from common import make_sign, check_sign, make_salt
from banknote_blocks import OdcbBlockHeader


class Bank():

    # _bank_id, _bpk, _bok

    def __init__(
            self,
            bank_id,
            bpk,
            bok,
            codes,
            comment=None,
    ):
        self._bank_id = bank_id
        self._bpk = bpk
        self._bok = bok
        self._comment = comment
        self._codes = codes


    @classmethod
    def load(cls, bank_path):
        assert bank_path.endswith(".bank.json")

        with open(bank_path, "r") as fr:
            data = json.load(fr)
            assert 'bank_id' in data
            assert 'bpk' in data
            assert 'bok' in data
            assert 'codes' in data

            bank_id = data['bank_id']
            bpk = data['bpk']
            bok = data['bok']
            codes = data['codes']
            comment = data.get('comment', None)
            _obj = cls(
                bank_id=bank_id,
                bpk=bpk,
                bok=bok,
                codes=codes,
                comment=comment,
            )
            return _obj


    def init_odcb_block_header(
            self,
            *,
            code: str,
            amount: int,
            count_append_applicability_blocks: int,
            first_applicability: str = "ALL-0000-0000000",
            banknote_id: Optional[uuid.UUID] = None,
    ):
        if banknote_id is None:
            banknote_id = uuid.uuid4()

        assert code in self._codes

        header = OdcbBlockHeader(
            bank_id=self._bank_id,
            banknote_id=banknote_id,
            bok=self._bok,
            code=code,
            amount=amount,
            applicability=first_applicability,
            count_append_applicability_blocks=count_append_applicability_blocks,
            sign_algorithm="RSA-4096............",
            hash_algorithm="SHA-512.............",
            salt=make_salt(),
            hash_=bytes(),
            bank_sign=bytes(),
        )

        hash_ = header.calc_hash()

        header.hash_ = hash_

        assert header.check_hash()

        header.bank_sign = make_sign(
            "RSA-4096............",
            hash_=hash_,
            private_key=self._bpk,
        )

        assert check_sign(
            "RSA-4096............",
            hash_=header.hash_,
            sign=header.bank_sign,
            public_key=self._bok,
        )

        return header


    def init_smart_card(self):
        """
        Инициирование новой смарт-карты
        :return:
        """