"""
Проверяем возможности переноса денег

Файл создан 27.11.2024 в 17:56:08

~/tests/transfer_test.py
"""

__author__ = 'pavelmstu'
__copyright__ = 'KIB, 2024'
__license__ = 'LGPL'
__credits__ = [
    'pavelmstu',
]
__version__ = "20241127"
__status__ = "Production"

import shutil

from bank import Bank
from wallet import ApplicationWallet
from wallet import _smart_card_path

from common import check_smart_card_params


# Информация о банке,
# включая приватный ключ bpk
BANK_PATH = 'data/test_bank.bank.json'

# wid Алисы
# Считаем что доступ имеет только Алиса
#   (!) Вызовите init_wallets.py для создания другого WID1
WID1 =  "96eff875-1a55-47b7-8a8f-4a11be926b10"


# wid Боба
# Считаем что доступ имеет только Алиса
#   (!) Вызовите init_wallets.py для создания другого WID2
WID2 =  "fc426146-15a2-48a5-a81c-cf30f2422fb6"


BANKNOTE_PATH = "tests/data/transfer_test.banknote.status_{0}.odcb"

def _banknote_path(status, *, json=False):
    path_ =  BANKNOTE_PATH.format(str(status).zfill(2))
    if json:
        path_ += ".json"
    print(f"\tпуть для банкноты:{path_}")
    return path_


def _wait_enter():
    class bcolors:
        HEADER = '\033[95m'
        OKBLUE = '\033[94m'
        OKCYAN = '\033[96m'
        OKGREEN = '\033[92m'
        WARNING = '\033[93m'
        FAIL = '\033[91m'
        ENDC = '\033[0m'
        BOLD = '\033[1m'
        UNDERLINE = '\033[4m'
    return input(bcolors.OKGREEN + "Нажмите ENTER для продолжения :"+ bcolors.ENDC)

def main():

    bank = Bank.load('data/test_bank.bank.json')

    # Глобальная переменная для всех участников
    BOK = bank.bok

    alice = ApplicationWallet(
        "Алиса",
        WID1,
    )

    bob = ApplicationWallet(
        "Боб",
        WID2,
    )
    print("Банк, Алиса и Боб успешно загружены из файлов")
    print(f"Можете на этом шаге посмотреть JSON файлы:\n\t{_smart_card_path(alice.card_wid)}\n\t{_smart_card_path(bob.card_wid)}")

    _ = _wait_enter()


    # Функция проверки валидности wid-а
    wid_check = lambda wid: True if wid in [WID1, WID2] else False

    print("-----------------------------------------")
    print("Предварительный шаг. Создаём банкноту")
    banknote_status = 0


    banknote = bank.make_banknote(
        code="KIB (000)",
        amount=100,
    )

    print(f"\tСоздана банкнота наминалом в {banknote.amount} единиц валюты {banknote.code}.")
    print(f"\tСм.путь: {_banknote_path(status=banknote_status)}")
    banknote.save(_banknote_path(status=banknote_status))
    banknote.save_json(_banknote_path(status=banknote_status, json=True))
    banknote_status += 1

    print("------------------------------------------")
    # ----------------
    # Сторона банка
    # ----------------
    print("шаг 1 (БАНК)")


    # - - - - - - - - - - - -
    # Передача БАНК -> АЛИСА
    print("\n---------- Передаём банкноту от банка Алисе")
    banknote = banknote
    pass

    # ----------------
    # Сторона Алисы.
    # ----------------
    print("шаг 2 (Алиса)")

    # ----------------
    print("\tИнициация по передаче банкноты")
    next_block = alice.receive_banknote_step1(banknote)

    # - - - - - - - - - - - -
    # Передача АЛИСА -> БАНК
    print("----------- Алиса передаёт next_block Банку")
    next_block = next_block
    wid, sok, sok_by_bpk, wid_and_sok_by_bpk = alice.smart_card_params
    pass
    pass

    # ----------------
    # Сторона Банка.
    # ----------------
    print("шаг 3. (Банк)")

    # -----------------
    print("\tВалидация кошелька Алисы")
    assert check_smart_card_params(
        wid, sok, sok_by_bpk, wid_and_sok_by_bpk,
        bok=BOK, wid_check=wid_check,
        hash_algorithm=banknote.hash_algorithm,
        sign_algorithm=banknote.sign_algorithm,
    )
    # del sok
    del wid
    del sok_by_bpk
    del wid_and_sok_by_bpk

    print("\tПодписывание next_block: bank.transfer_banknote")
    next_block = bank.transfer_banknote(banknote, next_block=next_block, sok=sok)


    # - - - - - - - - - - - -
    # Передача  БАНК -> Алиса
    print("----------- Банк передаёт next_block Алисе")
    next_block = next_block
    banknote = banknote

    print("шаг 4. (Алиса)")
    print("\talice.receive_banknote_step2")
    banknote = alice.receive_banknote_step2(banknote, last_block=None, next_block=next_block)
    del next_block

    print("\t\tПолучили второй блок (первый после хедера) в банкноте.")
    print(f"\t\tПоместили её по пути: {_banknote_path(status=banknote_status)}")
    banknote.save(_banknote_path(status=banknote_status))
    banknote.save_json(_banknote_path(status=banknote_status, json=True))
    banknote_status += 1

    print("---------------")
    print("---------------")
    print("На этом коммуникация Банк--Алиса по первичной передаче банкноты завершился.")
    print(f"Можете на этом шаге посмотреть JSON файл {_smart_card_path(alice.card_wid)}")

    _ = _wait_enter()

    del sok
    # ----------------------------
    # ----------------------------
    # ----------------------------
    # ----------------------------

    print("=======================")
    print("=======================")
    print("=======================")

    print("----------------------------")
    print("Передача банкноты от Алисы Бобу")

    print(f"Можете до передачи посмотреть JSON файл Алисы {_smart_card_path(alice.card_wid)}")
    print(f"Можете до передачи посмотреть JSON файл Боба {_smart_card_path(bob.card_wid)}")

    _ = _wait_enter()

    print("Шаг 0 (сторона Алисы)")
    print("----------- Алиса передаёт текущую банкноту Бобу. А так же информацию о себе")
    banknote = banknote
    widА, sokА, sokА_by_bpk, widА_and_sokА_by_bpk = alice.smart_card_params
    pass
    pass

    print("Шаг 1 (сторона Боба)")
    print("\tВалидация кошелька Алисы")
    assert check_smart_card_params(
        widА, sokА, sokА_by_bpk, widА_and_sokА_by_bpk,
        bok=BOK, wid_check=wid_check,
        hash_algorithm=banknote.hash_algorithm,
        sign_algorithm=banknote.sign_algorithm,
    )

    print("\tВалидация банкноты")
    assert banknote.validation()

    print("\tИнициация next_block для получения банкноты")
    next_block = bob.receive_banknote_step1(banknote)

    # Передача Боб -> Алиса
    print("----------- Боб передаёт next_block Алисе. А так же свои параметры для прооверки")
    next_block = next_block
    widB, sokB, sokB_by_bpk, widB_and_sokB_by_bpk = bob.smart_card_params
    pass
    pass

    print("Шаг 2 (Алиса)")
    print("\tВалидация кошелька Боба")
    assert check_smart_card_params(
        widB, sokB, sokB_by_bpk, widB_and_sokB_by_bpk,
        bok=BOK, wid_check=wid_check,
        hash_algorithm=banknote.hash_algorithm,
        sign_algorithm=banknote.sign_algorithm,
    )

    print("\tПодписывание Боб-ом next_block")
    last_block, next_block = alice.transfer_banknote(sokB, banknote, next_block)


    print("-------Передача last_block, next_block от Алисы к Бобу")
    last_block = last_block
    next_block = next_block

    print("Шаг 3 (Боб)")

    print('\tПроверка что next_block не изменён')
    pass # здесь эту проверку опустим, но нужно проверять

    print("\tbob.receive_banknote_step2")
    banknote = bob.receive_banknote_step2(banknote, last_block, next_block)

    print("\tВалидация банкноты")
    assert banknote.validation(bok=BOK)

    print("-------------")
    print("\t\tПолучили третий блок (второй после хедера) в банкноте.")
    print(f"\t\tПоместили её по пути: {_banknote_path(status=banknote_status)}")
    banknote.save(_banknote_path(status=banknote_status))
    banknote.save_json(_banknote_path(status=banknote_status, json=True))
    banknote_status += 1

    print(f"Можете посмотреть JSON файл Алисы {_smart_card_path(alice.card_wid)}")
    print(f"Можете посмотреть JSON файл Боба {_smart_card_path(bob.card_wid)}")
    _wait_enter()



def _copy_wallets():
    for wid in [WID1, WID2]:
        shutil.copyfile(f"data/{wid}.smart_card.json", f"tests/data/{wid}.smart_card.json")

if __name__ == "__main__":
    _copy_wallets()
    main()
    print("\nВсё!")
