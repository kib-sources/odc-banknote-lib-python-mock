# odc-banknote-lib-python-mock

Mock для ODC v2 протокола взаимодействия

## Установка

```bash
~$ cd <ПУТЬ_ДО_ВАШЕГО_ПРОЕКТА>
~$ git clone git@github.com:kib-sources/odc-banknote-lib-python-mock.git odcblib
```

В этом случае:
```python
import odcblib

print(odcblib.lib_version())
print(odcblib.supported_odcb_versions())
```
будет импортировать [__init__.py](__init__.py) файл.

Так же не забудьте добавить в свой `.gitignore`:
```python
odcblib/
```
или пропишите `odclib` как 
[подмодуль git-а](https://git-scm.com/book/ru/v2/Инструменты-Git-Подмодули).