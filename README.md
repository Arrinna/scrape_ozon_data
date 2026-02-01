# Ozon Dataset Project

Собираем данные по продажам с data.ozon.ru

1. Установка окружения и библиотек

``` bash
python -m venv .venv
.\.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac
python -m pip install --upgrade pip
pip install -r requirements.txt
```

2. Собираем ссылки - get_links.py

3. Скачиваем каждую категорию в xlsx - download_categories.py

4. Объединяем файлы в один - merge_brands_year.py

