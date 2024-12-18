"""
Тест инициации банкноты

Файл создан 11.11.2024 в 13:08:50

~/tests/init_banknote.py
"""

__author__ = 'pavelmstu'
__copyright__ = 'KIB, 2024'
__license__ = 'LGPL'
__credits__ = [
    'pavelmstu',
]
__version__ = "20241111"
__status__ = "Production"

from bank import Bank

from banknote import OdcBanknote


def main():
    print("init_banknote.py")
    print("Тест инициации банкноты")


    bank = Bank.load('data/test_bank.bank.json')

    print("Создание банкноты")
    banknote = bank.make_banknote(
        code="KIB (000)",
        amount=100,
    )


    PATH = 'tests/data/test_banknote.odcb'

    print(f"Сохрание банкноты по пути {PATH}")
    banknote.save(PATH)
    banknote.save_json(PATH+".json")

    print(f"Загрузка банкноты по пути {PATH}")
    banknote2 = OdcBanknote.load(PATH)

    print("Проверка сохнанение+загрузки")
    assert banknote == banknote2



    print("-----\nDONE")



if __name__ == "__main__":
    main()
