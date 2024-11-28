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
from typing import Tuple, Optional
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
        banknote_id = str(banknote_id)

        for _banknote_id, _counter in self._banknote_id_counter_pears:
            if _banknote_id == banknote_id:
                return _counter

        counter = self._counter

        # counter всегда должен увеличиваться
        # но чтобы нельзя было отследить тенденцию платежей,
        # увеличиваем на случайное число
        self._counter += random.randint(1, 10)

        self._banknote_id_counter_pears.append((banknote_id, counter))

        self._serialize()
        return counter

    def sign_hash0(self, hash0):
        sign0 = make_sign(self._sign_algorithm, hash0, self._spk)
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
        return self._sok

    @property
    def sok_by_bpk(self):
        return self._sok_by_bpk

    @property
    def wid(self):
        return self._wid

    @property
    def wid_and_sok_by_bpk(self):
        return self._wid_and_sok_by_bpk


    def sign_hash_next_block(
        self,
        banknote_id,
        counter_last_block,
        hash_next_block,

    ) -> Optional[SIGN]:
        """
        Подпись нового блока
            (созданный через init_next_block ПРОШЛЫМ владельцем)

        Вызывается ОТПРАВИТЕЛЕМ

        ВАЖНО:
        1. если ввести некорректный hash_next_block, то купюра "сгорит".
        2. если функция оборвётся до return и после удаления (banknote_id, counter_last_block) -- купюра "сгорит"

        :param banknote_id: банкнота
        :param counter_last_block: counter значение last_block,
        которое ранее получалось через get_counter()
        :param hash_next_block: подписываемый хеш next_block.
        :return:
        """
        banknote_id = str(banknote_id)

        i_position = -1
        for i, (banknote_id_, counter) in enumerate(self._banknote_id_counter_pears):
            if banknote_id_ == banknote_id:
                if counter == counter_last_block:
                    # банкнота присутствует в self._banknote_id_counter_pears
                    i_position = i
                    break

        if i_position == -1:
            # Банкноты нет в self._banknote_id_counter_pears
            return None

        sign_ = make_sign(self._sign_algorithm, hash_next_block, private_key=self._spk)

        # удаляем подпись из self._banknote_id_counter_pears
        # если мы этого не сделаем, то одну купюру можно будет передать повторно.
        self._banknote_id_counter_pears.pop(i_position)

        self._serialize()

        return sign_




class ApplicationWallet:
    """
    Класс уровня приложения, но не смарт-карты.

    ВАЖНО: wid сущность смарт-карты, но не ApplicationWallet

    """
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

    @property
    def card_wid(self):
        return self.smart_card.wid

    @property
    def smart_card_params(self):
        return self.smart_card.wid, self.smart_card.sok, self.smart_card.sok_by_bpk, self.smart_card.wid_and_sok_by_bpk

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
        assert next_block.check_hash0(hash_algorithm=hash_algorithm)

        next_block.hash0_by_spk_owner = self.smart_card.sign_hash0(next_block.hash0)
        assert next_block.verify_hash0(sok=self.smart_card.sok, sign_algorithm=sign_algorithm)

        return next_block


    def transfer_banknote(self, sok_new_owner, banknote: OdcBanknote, next_block: OdcbBlockChain) -> Tuple[OdcbBlockChain, OdcbBlockChain]:
        """
        Второй шаг. Вызывается отправителем.

        Изменить последний блок в banknote и выдать его первым аргументом

        Подписать next_block и выдать его вторым агрументом

        :param banknote: банкнота.
        В процессе функции последний блок не заменяется, а выдаётся отдельным первым параметром
        :param next_block:
        :return:
        """
        sign_algorithm = banknote.sign_algorithm
        hash_algorithm = banknote.hash_algorithm
        banknote_id = banknote.banknote_id

        assert self.smart_card.support_sign_algorithm(sign_algorithm)

        last_block = banknote._chain[-1]

        next_block = deepcopy(next_block)
        last_block = deepcopy(last_block)

        assert next_block.parent_hash == last_block.hash_
        assert next_block.check_hash0(hash_algorithm=hash_algorithm)
        assert next_block.verify_hash0(sok=sok_new_owner, sign_algorithm=sign_algorithm)

        next_block.salt = make_salt()
        next_block.hash_ = next_block.calc_hash(hash_algorithm=hash_algorithm)

        # Атомарная защищённая в Смарт-карте операция
        sign_ = self.smart_card.sign_hash_next_block(
            banknote_id=banknote_id,
            counter_last_block=last_block.counter,
            hash_next_block=next_block.hash_,
        )
        next_block.hash_by_spk_or_bpk_previous_owner = sign_

        assert next_block.check_hash(hash_algorithm=hash_algorithm)
        assert next_block.verify_hash(self.smart_card.sok, sign_algorithm=sign_algorithm)

        return last_block, next_block


    def receive_banknote_step2(self, banknote: OdcBanknote, last_block: Optional[OdcbBlockChain], next_block: OdcbBlockChain) -> OdcBanknote:
        """
        Третий шаг. Вызывается получателем.

        :param banknote:
        :param last_block: последний блок банкноты, подписанный прежним владельцем.
        None, если это первичная передача банкноты от банка первому кошельку.
        :param next_block:
        :return: новую banknote, с изменённым последним блоком last_block
        и добавленным новым блоком next_block
        """
        new_banknote = deepcopy(banknote)

        assert next_block.sok_owner_by_bpk == self.smart_card.sok_by_bpk
        assert next_block.banknote_id == new_banknote.banknote_id

        if last_block is None:
            # next_block -- это первый блок в цепочке (кроме хедера)
            assert len(new_banknote._chain) ==  0
            assert new_banknote._header.hash_ == next_block.parent_hash

            new_banknote._chain = [next_block]
            return new_banknote
        else:
            assert last_block.banknote_id == next_block.banknote_id
            assert last_block.hash_ == next_block.parent_hash
            # TODO assert next_block.sok == self.smart_card.sok

            new_banknote._chain = new_banknote._chain[:-1]

            new_banknote._chain.append(last_block)
            new_banknote._chain.append(next_block)

            return new_banknote

