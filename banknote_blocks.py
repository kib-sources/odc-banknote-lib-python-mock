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

import enum
import random
import uuid
# __status__ = "Production"

from dataclasses import dataclass

from types_ import HASH, SIGN, KEY, UUID_STR

ODCB_FILE_PREFIX = "ODC banknote........"
ODCB_FILE_VERSION = "v2-py-mock"

assert len(ODCB_FILE_PREFIX) == 20
assert ODCB_FILE_PREFIX == "ODC banknote........"
assert len(ODCB_FILE_VERSION) == 10

# Далее префикса и версии мы можем НЕ придерживаться ODC v2 протокола *.odbc банкнот.
# Версия "v2-py-mock" указывает что это замоченная версия.

from common import make_hash, check_sign

from clib import c_core


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
    hash_: HASH = bytes()

    bank_sign: SIGN = ""

    def calc_hash(self):
        return make_hash(
            "SHA-512.............",
            self.bank_id,
            self.banknote_id,
            self.bok,
            self.code,
            self.amount,
            self.applicability,
            self.count_append_applicability_blocks,
            self.sign_algorithm,
            self.hash_algorithm,
            self.salt,
        )

    def check_hash(self):
        if self.hash_ == self.calc_hash():
            return True
        else:
            return False


@dataclass
class OdcbBlockApplicability:

    bank_id: str
    banknote_id: UUID_STR

    parent_hash: HASH

    applicability: str

    salt: str # = _some_salt

    hash: HASH = ""

    bank_sign: SIGN = ""

# @dataclass
# class OdcbBlockChain:

@dataclass
class OdcbBlockTransfer:

    bank_id: str
    banknote_id: UUID_STR

    parent_hash: HASH

    # sok_owner: KEY -- НЕЛЬЗЯ вычислить, расшифровав sok_owner_by_bpk
    # sok_owner_by_bpk -- это подписанный хеш от sok_owner
    # верифицируется только в момент передачи на следующий блок
    sok_owner_by_bpk: SIGN

    counter: int

    salt0: str
    hash0: HASH = ""
    hash0_by_spk_owner: SIGN = bytes()

    salt: str = ""
    hash_: HASH = bytes()
    hash_by_spk_or_bpk_previous_owner: SIGN = bytes()

    @c_core
    def calc_hash0(self, hash_algorithm="SHA-512............."):
        return make_hash(
            hash_algorithm,
            self.bank_id,
            self.banknote_id,
            self.parent_hash,
            self.sok_owner_by_bpk,
            self.counter,
            self.salt0,
        )

    @c_core
    def check_hash0(self, hash_algorithm="SHA-512............."):
        if self.hash0 == self.calc_hash0(hash_algorithm=hash_algorithm):
            return True
        else:
            return False

    @c_core
    def verify_sok(self, sok, bok, *, sign_algorithm="RSA-4096............", hash_algorithm="SHA-512............."):
        return check_sign(
            sign_algorithm,
            make_hash(hash_algorithm, sok),
            self.sok_owner_by_bpk,
            bok
        )

    @c_core
    def verify_hash0(self, sok, *, sign_algorithm="RSA-4096............"):
        return check_sign(
            sign_algorithm,
            self.hash0,
            self.hash0_by_spk_owner,
            sok,
        )

    @c_core
    def calc_hash(self, hash_algorithm="SHA-512............."):
        return make_hash(
            hash_algorithm,
            self.bank_id,
            self.banknote_id,
            self.parent_hash,
            self.sok_owner_by_bpk,
            self.counter,
            self.salt0,
            # ----
            self.hash0,
            self.hash0_by_spk_owner,
            # ----
            self.salt,
        )

    @c_core
    def check_hash(self,  hash_algorithm="SHA-512............."):
        if self.hash_ == self.calc_hash(hash_algorithm=hash_algorithm):
            return True
        else:
            return False

    @c_core
    def verify_hash(self, sok_or_bok, *, sign_algorithm="RSA-4096............"):
        return check_sign(
            sign_algorithm,
            self.hash_,
            self.hash_by_spk_or_bpk_previous_owner,
            sok_or_bok,
        )

    # --------------
    # опциональные поля, при online, а не offline передаче
    # ВАЖНО: salt, hash, hash_by_spk_or_bpk_previous_owner в подпись НЕ попадают.
    #  Это нужно чтобы была возможность подписать банком как до передачи банкноты, так и после неё.
    salt_bank: str = ""
    hash_bank: HASH = bytes()
    hash_bank_by_bpk: SIGN = bytes()

    @c_core
    def calc_hash_bank(self, hash_algorithm="SHA-512............."):
        return make_hash(
            hash_algorithm,
            self.bank_id,
            self.banknote_id,
            self.parent_hash,
            self.sok_owner_by_bpk,
            self.counter,
            self.salt0,
            # ----
            self.hash0,
            self.hash0_by_spk_owner,
            # ----
            self.salt_bank
        )

    @c_core
    def check_hash_bank(self,  hash_algorithm="SHA-512............."):
        if self.hash_bank == self.calc_hash_bank(hash_algorithm=hash_algorithm):
            return True
        else:
            return False

    @c_core
    def verify_hash_bank(self, bok, *, sign_algorithm="RSA-4096............"):
        return check_sign(
            sign_algorithm,
            self.hash_bank,
            self.hash_bank_by_bpk,
            bok,
        )

    @c_core
    def hash_validation(self, hash_algorithm="SHA-512............."):
        if not self.check_hash0(hash_algorithm=hash_algorithm):
            return False
        if self.hash_ and not self.check_hash(hash_algorithm=hash_algorithm):
            return False
        if self.hash_bank and not self.check_hash_bank(hash_algorithm=hash_algorithm):
            return False
        return True

