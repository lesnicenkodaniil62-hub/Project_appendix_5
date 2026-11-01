# **Название проекта**

## Описание

## Установка

1. Клонируйте репозиторий:
```
git clone https://github.com/lesnicenkodaniil62-hub/
```
2. Установите зависимости:
```
Проект построен на базе Django и использует PostgreSQL в качестве базы данных. Для обеспечения качества кода настроены строгие правила линтинга, форматирования и статического анализа типов, а также написано покрытие тестами.
Основные компоненты
1. Веб-фреймворк, база данных и окружение:
django — основной веб-фреймворк проекта.
psycopg2 — драйвер для подключения и работы с базой данных PostgreSQL.
python-dotenv — загрузка переменных окружения из файла .env.
Pillow — библиотека для обработки и работы с изображениями.
2. Работа с данными, API и автоматизация:
pandas и openpyxl — анализ данных, а также чтение/запись файлов формата Excel (.xlsx).
schedule — планировщик задач (используется для автоматического почасового обновления данных в БД).
requests — отправка HTTP-запросов к внешним API.
3. Контроль качества кода (Linting & Formatting):
black и isort — автоматическое форматирование кода и сортировка импортов.
flake8 — проверка кода на соответствие стандартам PEP8 и поиск синтаксических ошибок.
mypy, django-stubs, django-stubs-ext — статическая проверка типов (Type Hinting) с полной поддержкой типизации для Django.
4. Тестирование:
pytest — фреймворк для написания и запуска тестов.
pytest-cov — инструмент для измерения покрытия кода тестами (Code Coverage).
5. Стандартные библиотеки Python:
В проекте также активно используются встроенные модули Python, которые не требуют отдельной установки через Poetry:
os — для взаимодействия с операционной системой, работы с путями и переменными окружения.
json — для парсинга, чтения и сериализации данных в формате JSON.
logging — для настройки, форматирования и вывода логов приложения.
unittest.mock — встроенный модуль для мокирования объектов (используются Mock и patch при написании тестов).
IPython — это улучшенная интерактивная оболочка для Python,

1. flake8 
poetry add --group lint flake8
2. mypy
poetry add --group lint mypy
3. black
poetry add --group lint black
4. isort
poetry add --group lint isort
5. psycopg2
poetry add --group lint psycopg2
6. schedule
poetry add schedule
7. requests
poetry add requests
8. pandas
poetry add pandas
9. openpyxl
poetry add openpyxl
10. python-dotenv
poetry add python-dotenv
11. django
poetry add django
12. redis
poetry add redis
13. django-redis
poetry add redis django-redis
14. pytest
poetry add --group dev pytest
Code coverage в
Code coverage в библиотеку pytest
15. pytest-cov
poetry add --group dev pytest-cov
16. django-stubs
poetry add --group lint django-stubs
17. django-stubs-ext
poetry add --group lint django-stubs-ext 
18. python-dotenv
poetry add --group lint python-dotenv   
19. pillow
poetry add --group lint pillow
20. ipython
poetry add --group dev ipython

```
Более подробные настройки линтеров можно узнать тут, а также тесты, которые прошли функции можно узнать тут же [документации](docs/README.md).

## Использование:

## Документация:

Для получения дополнительной информации обратитесь к [документации](docs/README.md).

## Лицензия:

Этот проект лицензирован по [лицензии MIT](LICENSE).