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


import random
import uuid
from typing import Optional, Tuple

from Crypto.Hash import SHA512
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5

from types_ import SIGN, HASH, KEY


# def import_key(str_key: str) -> KEY:

from clib import c_core


def to_odcb_bytes(some):
    if isinstance(some, bytes):
        return some
    if isinstance(some, str):
        return some.encode('ascii')
    if isinstance(some, int):
        return some.to_bytes(length=8, byteorder='big')
    if isinstance(some, uuid.UUID):
        return str(some).encode('ascii')

    raise NotImplementedError(f"Не реализована функция {to_odcb_bytes.__name__} для типа {type(some)}")

@c_core
def make_salt():
    # return random.getrandbits(64).to_bytes().hex()

    RANDOM_ALPHABET = '0123456789qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM'

    return ''.join(random.sample(RANDOM_ALPHABET, 32))


@c_core
def make_hash(hash_algorithm:str, *args) -> HASH:
    # В python всё можно привести к строке и это удобно.
    # Однако в Си коде хеш будем брать от последовательности байт.
    # Поэтому переводим всё в байты

    if hash_algorithm != "SHA-512.............":
        raise NotImplementedError(f"Не реализована поддержка хеш-алгоритма '{hash_algorithm}'.")


    bytes_data = b''.join([
        to_odcb_bytes(arg)
        for arg in args
    ])

    h = SHA512.new()
    h.update(bytes_data)
    hash_ = h.digest()
    return hash_


@c_core
def check_sign(
    sign_algorithm: str,
    hash_: HASH,
    sign: SIGN,
    public_key: KEY,
) -> bool:
    assert sign_algorithm == "RSA-4096............"

    key = RSA.importKey(public_key)
    verifier = PKCS1_v1_5.new(key)
    hash_object = SHA512.new(data=hash_)
    verified = verifier.verify(hash_object, sign)
    return verified


@c_core
def make_sign(
    sign_algorithm: str,
    hash_: HASH,
    private_key: KEY,
    # public_key: Optional[KEY] = None,
) -> SIGN:

    assert sign_algorithm == "RSA-4096............"

    key = RSA.importKey(private_key)
    signer = PKCS1_v1_5.new(key)
    hash_object = SHA512.new(data=hash_)
    sign = signer.sign(hash_object)

    return sign


@c_core
def new_key_pears() -> Tuple[KEY, KEY]:
    private_key = RSA.generate(4096)
    public_key = private_key.publickey()

    private_key_str = private_key.exportKey().decode()
    public_key_str = public_key.exportKey().decode()

    return private_key_str, public_key_str


def check_smart_card_params(
        wid,
        sok,
        sok_by_bpk,
        wid_and_sok_by_bpk,
        *,
        bok,
        wid_check=None,
        hash_algorithm="SHA-512.............",
        sign_algorithm="RSA-4096............",
) -> bool:
    """
    Проверяются параметры
    :param wid:
    :param sok:
    :param sok_by_bpk:
    :param wid_and_sok_by_bpk:
    :param bok:
    :param wid_check: (Опционально)
    функция по проверке наличия WID в базе данных
    Возвращает False, если wid-а нет, либо если он не валиден.
    :param hash_algorithm:
    :param sign_algorithm:
    :return:
    """
    if wid_check is not None:
        if not wid_check(wid):
            return False

    hash_ = make_hash(hash_algorithm, sok)
    if not check_sign(sign_algorithm, hash_, sok_by_bpk, public_key=bok):
        return False

    hash_ = make_hash(hash_algorithm, wid, sok)
    if not check_sign(sign_algorithm, hash_, wid_and_sok_by_bpk, public_key=bok):
        return False

    return True



