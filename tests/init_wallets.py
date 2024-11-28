"""
Тестовая функция создания банкнот

Файл создан 27.11.2024 в 16:56:14

~/tests/send_banknote_to_first_wallet.py
"""

__author__ = 'pavelmstu'
__copyright__ = 'KIB, 2024'
__license__ = 'LGPL'
__credits__ = [
    'pavelmstu',
]
__version__ = "20241127"
__status__ = "Production"

from bank import Bank

from banknote import OdcBanknote

from wallet import ApplicationWallet


def init_banknote():
    print("init_banknote.py")
    print("Тест инициации банкноты")


    bank = Bank.load('data/test_bank.bank.json')

    print("Создание банкноты")
    banknote = OdcBanknote.make(
        bank=bank,
        code="KIB (000)",
        amount=100,
    )


    PATH = 'tests/data/test_banknote.odcb'

    # print(f"Сохрание банкноты по пути {PATH}")
    # banknote.save(PATH)

    # print(f"Загрузка банкноты по пути {PATH}")
    # banknote2 = OdcBanknote.load(PATH)

    # print("Проверка сохнанение+загрузки")
    # assert banknote == banknote2

    return banknote


def main():
    bank = Bank.load('data/test_bank.bank.json')

    # --------------------------------------------------------------------------------------------------------------
    # На стороне банка инициируются смарт-карты


    wid1 = bank.make_smart_card()
    print(f"Создана SmartCard с wid={wid1} (WID1)")

    wid2 = bank.make_smart_card()
    print(f"Создана SmartCard с wid={wid2} (WID2)")

    print("""Далее wid1 передаётся физическим образом Алисе, а wid2 -- Бобу. 
Боб не имеет доступа к wid1, 
а Алиса к wid2.
В рамках этого POC это невозможно проверить, т.к. оба файла лежат на одном компьютере.
В нормальной реализации ODC это будет не файлы, а "закупоренные" SIM карты.
Поле wid, поле sok а так же подписи sok_by_bpk и wid_and_sok_by_bpk будут внутри и неизменны.
Поле spk тоже будет внутри и неизвлекаемо из сим-карты. 

Сейчас вы можете это посмотреть в файлах *.smart_card.json типа.
    """)

    alice = ApplicationWallet(
        "Алиса",
        wid1,
    )

    bob = ApplicationWallet(
        "Боб",
        wid2,
    )

    print("Кошельки Алисы и Боба успешно созданы")

    print("Не забудьте перенести wid1 и wid2 поля в глобальные переменные WID1 и WID2 для дальнейшего тестирования.")




if __name__ == "__main__":
    main()
