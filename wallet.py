"""

Файл создан 11.11.2024 в 16:10:55

~//wallet.py
"""

__author__ = 'pavelmstu'
__copyright__ = 'KIB, 2024'
__license__ = 'LGPL'
__credits__ = [
    'pavelmstu',
]
__version__ = "20241111"
__status__ = "Develop"

import base64
# __status__ = "Production"

import json
import os.path
import uuid
import random
from datetime import datetime
from typing import Tuple
from copy import deepcopy
from types_ import SIGN

from common import new_key_pears, make_salt, make_sign

from banknote import OdcBanknote
from banknote_blocks import OdcbBlockChain

from types_ import HASH

def _smart_card_path(wid):
    return os.path.join(f'tests', 'data', f'{wid}.smart_card.json')

class SmartCard:
    """
    Класс, реализующий функционал смарт-карты.

    Содержит приватные spk, _banknote_id_counter_pears

    В не Mock-е будет реализовывать функционал доступа к смарт-карте

    """

    def __init__(
        self,
        spk,
        sok,
        wid,
        sok_by_bpk,
        wid_and_sok_by_bpk,
        sign_algorithm="RSA-4096............",
    ):
        self._wid = str(wid)
        self._spk = spk
        self._sok = sok
        self._sok_by_bpk = sok_by_bpk
        self._wid_and_sok_by_bpk = wid_and_sok_by_bpk
        self._sign_algorithm = sign_algorithm

        # Чтобы не было известно сколько операций совершено кошельком,
        #   устанавливаем случайное число.
        #   Главное, чтобы counter всегда увеличивался.
        self._counter = random.randint(1, 10000)

        # список вида
        # [
        #    (banknote_id, counter)
        #    (banknote_id, counter)
        #    ...
        # ]
        self._banknote_id_counter_pears = list()

        # - - - -
        # синхронизация в файле.
        self._path_sinc = _smart_card_path(self._wid)
        # assert not os.path.exists(self._path_sinc)


    def get_counter(self, banknote_id) -> int:

        for _banknote_id, _counter in self._banknote_id_counter_pears:
            if _banknote_id == banknote_id:
                return _counter

        # counter всегда должен увеличиваться
        # но чтобы нельзя было отследить тенденцию платежей,
        # увеличиваем на случайное число
        self._counter += random.randint(1, 10)
        counter = self._counter

        self._banknote_id_counter_pears.append((banknote_id, counter))

        self._serialize()
        return counter

    def sign_hash0(self, hash0):
        sign0 = make_sign("RSA-4096............", hash0, self._spk)
        return sign0


    def _serialize(self, first=False):
        if first is False:
            assert os.path.exists(self._path_sinc)
        else:
            assert not os.path.exists(self._path_sinc)

        info = {
            "wid": self._wid,
            "sok": self._sok,
            "spk": self._spk,
            "sok_by_bpk_base64": base64.b64encode(self._sok_by_bpk).decode(),
            "wid_and_sok_by_bpk_base64": base64.b64encode(self._wid_and_sok_by_bpk).decode(),
            "counter": self._counter,
            "pears": self._banknote_id_counter_pears,
            "_last_serialize": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "_sign_algorithm": self._sign_algorithm
        }
        with open(self._path_sinc, 'w') as fw:
            fw.write(json.dumps(info, indent=4))
        return

    @property
    def sok_by_bpk(self) -> SIGN:
        return self._sok_by_bpk

    @property
    def wid_and_sok_by_bpk(self) -> SIGN:
        return self._wid_and_sok_by_bpk


    def support_sign_algorithm(self, sign_algorithm) -> bool:
        if sign_algorithm == self._sign_algorithm:
            return True
        else:
            return False


    @classmethod
    def load(
        cls,
        wid,
    ):
        wid = str(wid)
        path = _smart_card_path(wid)
        if not os.path.exists(path):
            raise EnvironmentError(f"Нет файла по пути '{path}'. Точно правильный wid={wid} ?")

        with (open(path, 'r') as fr):
            info = json.load(fr)
            assert 'counter' in info
            assert 'pears' in info
            assert 'wid' in info
            assert 'sok' in info
            assert 'spk' in info
            assert "sok_by_bpk_base64" in info
            assert "wid_and_sok_by_bpk_base64" in info
            assert "_sign_algorithm" in info

            assert wid == info['wid']

            counter = info['counter']
            spk = info['spk']
            sok = info['sok']
            sok_by_bpk_base64 = info['sok_by_bpk_base64']
            wid_and_sok_by_bpk_base64 = info['wid_and_sok_by_bpk_base64']
            _sign_algorithm = info['_sign_algorithm']

            sok_by_bpk = base64.b64decode(sok_by_bpk_base64.encode())
            wid_and_sok_by_bpk = base64.b64decode(wid_and_sok_by_bpk_base64.encode())

            _obj = cls(
                spk=spk,
                sok=sok,
                wid=wid,
                sok_by_bpk=sok_by_bpk,
                wid_and_sok_by_bpk=wid_and_sok_by_bpk,
                sign_algorithm=_sign_algorithm,
            )

            _obj._banknote_id_counter_pears = info['pears']
            _obj._counter = counter

            return _obj


    @property
    def sok(self):
        return self.sok

    def init_second_block(
        self,
        header_block
    ):
        """
        Создание второго (первого после хедера) блока.

        Если блок не второй, то используйте init_next_block
        
        :param header_block: 
        :return: 
        """

    def init_next_block(
        self,
        bank_id: str,
        banknote_id: str,
        parent_hash: HASH,
    ):
        """
        Создание нового блока (но не второго)

        Вызывается ПОЛУЧАТЕЛЕМ

        :return:
        """
        banknote_id = str(banknote_id)

        pass


    def sign_next_block(
        self,
        last_block,
        next_block,
    ):
        """
        Подпись нового блока
            (созданный через init_next_block ПРОШЛЫМ владельцем)

        Вызывается ОТПРАВИТЕЛЕМ

        :param last_block:
        :param next_block:
        :return:
        """






class Wallet:

    _SUPPORTED_HASH_ALGORITHMS = [
        "SHA-512............."
    ]


    def __init__(
        self,
        name,
        smart_wid,
    ):
        smart_card = SmartCard.load(smart_wid)

        self.smart_card = smart_card
        self.name = name


    def receive_banknote_step1(self, banknote: OdcBanknote) -> OdcbBlockChain:
        """
        Первый шаг. Вызывается получателем.

        Создаёт новый блок владения банкнотой
        :param banknote:
        :return:
        """
        sign_algorithm = banknote.sign_algorithm
        hash_algorithm = banknote.hash_algorithm

        if not self.smart_card.support_sign_algorithm(sign_algorithm):
            raise NotImplementedError(f"SmartCard не поддерживает алгоритм подписи {sign_algorithm}")

        bank_id = banknote.bank_id
        banknote_id = banknote.banknote_id
        parent_hash = banknote.last_chain_hash

        next_block = OdcbBlockChain(
            bank_id=bank_id,
            banknote_id=banknote_id,
            parent_hash=parent_hash,
            counter=self.smart_card.get_counter(banknote_id),
            salt0=make_salt(),
            sok_owner_by_bpk=self.smart_card.sok_by_bpk,
        )

        next_block.hash0 = next_block.calc_hash0(
            hash_algorithm=hash_algorithm,
        )
        assert next_block.hash0 == next_block.check_hash0(hash_algorithm=hash_algorithm)

        next_block.hash0_by_spk_owner = self.smart_card.sign_hash0(next_block.hash0)

        return next_block


    def transfer_banknote(self, banknote: OdcBanknote, next_block: OdcbBlockChain) -> Tuple[OdcBanknote, OdcBanknote]:
        """
        Второй шаг. Вызывается отправителем.

        Изменить последний блок в banknote и выдать его первым аргументом

        Подписать next_block и выдать его вторым агрументом

        :param banknote: банкнота.
        В процессе функции последний блок не заменяется, а выдаётся отдельным первым параметром
        :param next_block:
        :return:
        """

        last_block = banknote._chain[-1]

        raise NotImplementedError()


        return last_block, next_block


    def receive_banknote_step2(self, banknote: OdcBanknote, last_block: OdcbBlockChain, next_block: OdcbBlockChain) -> OdcBanknote:
        """
        Третий шаг. Вызывается получателем.

        :param banknote:
        :param last_block:
        :param next_block:
        :return: новую banknote, с изменённым последним блоком last_block
        и добавленным новым блоком next_block
        """

        # TODO проверки верификации

        new_banknote = deepcopy(banknote)

        new_banknote._chain = new_banknote._chain[:-1]

        new_banknote._chain.append(last_block)
        new_banknote._chain.append(next_block)

        return new_banknote

