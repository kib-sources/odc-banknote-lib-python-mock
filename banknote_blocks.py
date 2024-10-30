"""
python:
>> import odcblib.banknote_blocks

Файл создан 30.10.2024 в 23:05:20

~//banknote_blocks.py
"""

__author__ = 'pavelmstu'
__copyright__ = 'KIB, 2024'
__license__ = 'LGPL'
__credits__ = [
    'pavelmstu',
]
__version__ = "20241030"
__status__ = "Develop"

import random
import uuid
# __status__ = "Production"

from dataclasses import dataclass

from .types import HASH
from .types import SIGN
from .types import KEY

ODCB_FILE_PREFIX = "ODC banknote........"
ODCB_FILE_VERSION = "v2-py-mock"

assert len(ODCB_FILE_PREFIX) == 20
assert ODCB_FILE_PREFIX == "ODC banknote........"
assert len(ODCB_FILE_VERSION) == 10

# Далее префикса и версии мы можем НЕ придерживаться ODC v2 протокола *.odbc банкнот.
# Версия "v2-py-mock" указывает что это замоченная версия.



@dataclass
class OdcbBlockHeader:

    bank_id: str
    banknote_id: uuid.UUID

    bok: KEY

    # currency code
    code: str

    amount: int

    applicability: str

    count_append_applicability_blocks: int # = 0

    sign_algorithm: str # = "RSA-4096............"
    hash_algorithm: str # = "SHA-512............."

    salt: str # = _some_salt

    #  hash = hash(bank_id, ..., sign_algorithm, hash_algorithm, salt)
    hash_: HASH = ""

    bank_sign: SIGN = ""

    def _calc_hash(self):
        raise NotImplementedError()

    def _check_hash(self):
        raise NotImplementedError()



@dataclass
class OdcbBlockApplicability:

    bank_id: str
    banknote_id: uuid.UUID

    parent_hash: HASH

    applicability: str

    salt: str # = _some_salt

    hash: HASH = ""

    bank_sign: SIGN = ""


@dataclass
class OdcbBlockChain:

    bank_id: str
    banknote_id: uuid.UUID

    parent_hash: HASH

    # sok_owner: KEY -- можно вычислить, расшифровав sok_owner_by_bpk
    sok_owner_by_bpk: SIGN

    counter: int

    salt0: str
    hash0: HASH
    hash0_by_spk_owner: SIGN

    salt: str
    hash: HASH
    hash_by_spk_or_bpk_previous_owner: SIGN

    # --------------
    # опциональные поля, при online, а не offline передаче
    salt_bank: str
    hash_bank: HASH
    hash_bank_by_bpk: SIGN


