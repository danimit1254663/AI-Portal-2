# -*- coding: utf-8 -*-

import sys
import subprocess
import tempfile
import threading
import time
import re
from pathlib import Path
from tkinter import filedialog, messagebox, simpledialog


# ============================================================
# АВТОУСТАНОВКА БИБЛИОТЕК
# ============================================================

def install_package(package_name):
    try:
        subprocess.check_call([
            sys.executable,
            "-m",
            "pip",
            "install",
            package_name
        ])
        return True
    except Exception:
        return False


def ensure_package(package_name, import_name=None):
    if import_name is None:
        import_name = package_name

    try:
        __import__(import_name)
        return True
    except ImportError:
        return install_package(package_name)


if not ensure_package("customtkinter", "customtkinter"):
    raise SystemExit(
        "Не удалось установить customtkinter."
    )


import customtkinter as ctk


# ============================================================
# НАСТРОЙКИ
# ============================================================

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


# ============================================================
# БАЗА КОМАНД
# ============================================================

COMMANDS_DB = {

    # ========================================================
    # PYTHON
    # ========================================================

    "Вывод (print)": {
        "template": "print({var1})",
        "vars": [
            "Текст или значение"
        ],
        "type": "python",
        "imports": []
    },

    "Ввод (input)": {
        "template": "{var1} = input({var2})",
        "vars": [
            "Имя переменной",
            "Текст подсказки"
        ],
        "type": "python",
        "imports": []
    },

    "Присваивание переменной": {
        "template": "{var1} = {var2}",
        "vars": [
            "Имя переменной",
            "Значение"
        ],
        "type": "python",
        "imports": []
    },

    "Цикл for": {
        "template": (
            "for i in range({var1}):\n"
            "    pass"
        ),
        "vars": [
            "Количество повторений"
        ],
        "type": "python",
        "imports": []
    },

    "Условие if": {
        "template": (
            "if {var1}:\n"
            "    pass"
        ),
        "vars": [
            "Условие"
        ],
        "type": "python",
        "imports": []
    },

    "Создать функцию": {
        "template": (
            "def {var1}({var2}):\n"
            "    {var3}"
        ),
        "vars": [
            "Имя функции",
            "Параметры",
            "Код функции"
        ],
        "type": "python",
        "imports": []
    },

    # ========================================================
    # CUSTOMTKINTER
    # ========================================================

    "Добавить кнопку": {
        "template": (
            "{var1} = ctk.CTkButton("
            "frame, "
            "text={var2}, "
            "command={var3}"
            ")\n"
            "{var1}.pack(pady=5)"
        ),
        "vars": [
            "Имя переменной кнопки",
            "Текст кнопки",
            "Функция или None"
        ],
        "type": "gui",
        "imports": [
            "import customtkinter as ctk"
        ]
    },

    "Добавить метку": {
        "template": (
            "{var1} = ctk.CTkLabel("
            "frame, "
            "text={var2}"
            ")\n"
            "{var1}.pack(pady=5)"
        ),
        "vars": [
            "Имя переменной",
            "Текст"
        ],
        "type": "gui",
        "imports": [
            "import customtkinter as ctk"
        ]
    },

    "Добавить поле ввода": {
        "template": (
            "{var1} = ctk.CTkEntry(frame)\n"
            "{var1}.pack(pady=5)"
        ),
        "vars": [
            "Имя переменной"
        ],
        "type": "gui",
        "imports": [
            "import customtkinter as ctk"
        ]
    },

    "Добавить текстовое поле": {
        "template": (
            "{var1} = ctk.CTkTextbox("
            "frame, "
            "height={var2}"
            ")\n"
            "{var1}.pack("
            "pady=5, "
            "fill='both', "
            "expand=True"
            ")"
        ),
        "vars": [
            "Имя переменной",
            "Высота"
        ],
        "type": "gui",
        "imports": [
            "import customtkinter as ctk"
        ]
    },

    "Добавить чекбокс": {
        "template": (
            "{var1} = ctk.CTkCheckBox("
            "frame, "
            "text={var2}"
            ")\n"
            "{var1}.pack(pady=5)"
        ),
        "vars": [
            "Имя переменной",
            "Текст"
        ],
        "type": "gui",
        "imports": [
            "import customtkinter as ctk"
        ]
    },

    "Добавить ComboBox": {
        "template": (
            "{var1} = ctk.CTkComboBox("
            "frame, "
            "values={var2}"
            ")\n"
            "{var1}.pack(pady=5)"
        ),
        "vars": [
            "Имя переменной",
            "Список значений"
        ],
        "type": "gui",
        "imports": [
            "import customtkinter as ctk"
        ]
    },

    # ========================================================
    # CUSTOMTKINTER — ФОТО ИЗ ФАЙЛА
    # ========================================================

    "Добавить изображение из файла": {
        "template": (
            "_img_path = {var2}\n"
            "_img = Image.open(_img_path).convert('RGBA')\n"
            "_img.thumbnail(({var3}, {var4}))\n"
            "\n"
            "{var1}_image = ctk.CTkImage(\n"
            "    light_image=_img,\n"
            "    dark_image=_img,\n"
            "    size=_img.size\n"
            ")\n"
            "\n"
            "{var1} = ctk.CTkLabel(\n"
            "    frame,\n"
            "    text='',\n"
            "    image={var1}_image\n"
            ")\n"
            "{var1}.pack(pady=10)"
        ),
        "vars": [
            "Имя переменной",
            "Путь к изображению",
            "Максимальная ширина",
            "Максимальная высота"
        ],
        "type": "gui",
        "imports": [
            "import customtkinter as ctk",
            "from PIL import Image"
        ]
    },

    # ========================================================
    # CUSTOMTKINTER — ФОТО ПО URL
    # ========================================================

    "Добавить изображение по URL": {
        "template": (
            "_response_{var1} = requests.get("
            "{var2}, "
            "timeout=30"
            ")\n"
            "_response_{var1}.raise_for_status()\n"
            "\n"
            "_image_data_{var1} = BytesIO("
            "_response_{var1}.content"
            ")\n"
            "\n"
            "_img_{var1} = Image.open("
            "_image_data_{var1}"
            ").convert('RGBA')\n"
            "_img_{var1}.thumbnail(({var3}, {var4}))\n"
            "\n"
            "{var1}_image = ctk.CTkImage(\n"
            "    light_image=_img_{var1},\n"
            "    dark_image=_img_{var1},\n"
            "    size=_img_{var1}.size\n"
            ")\n"
            "\n"
            "{var1} = ctk.CTkLabel(\n"
            "    frame,\n"
            "    text='',\n"
            "    image={var1}_image\n"
            ")\n"
            "{var1}.pack(pady=10)"
        ),
        "vars": [
            "Имя переменной",
            "URL изображения",
            "Максимальная ширина",
            "Максимальная высота"
        ],
        "type": "gui",
        "imports": [
            "import customtkinter as ctk",
            "import requests",
            "from io import BytesIO",
            "from PIL import Image"
        ]
    },

    # ========================================================
    # FOLIUM — КАРТА
    # ========================================================

    "Создать карту": {
        "template": (
            "{var1} = folium.Map(\n"
            "    location=[{var2}, {var3}],\n"
            "    zoom_start={var4},\n"
            "    control_scale=True\n"
            ")\n"
            "\n"
            "_route_points = []"
        ),
        "vars": [
            "Имя карты",
            "Широта",
            "Долгота",
            "Масштаб"
        ],
        "type": "folium",
        "imports": [
            "import folium"
        ]
    },

    # ========================================================
    # FOLIUM — ОБЫЧНЫЙ МАРКЕР
    # ========================================================

    "Добавить маркер": {
        "template": (
            "_marker_{var2} = folium.Marker(\n"
            "    location=[{var3}, {var4}],\n"
            "    tooltip={var5},\n"
            "    popup={var6}\n"
            ")\n"
            "_marker_{var2}.add_to({var1})\n"
            "\n"
            "if {var7}:\n"
            "    _route_points.append(({var3}, {var4}))"
        ),
        "vars": [
            "Переменная карты",
            "Уникальное имя точки",
            "Широта",
            "Долгота",
            "Название",
            "Текст popup",
            "Маршрутная точка (True/False)"
        ],
        "type": "folium",
        "imports": [
            "import folium"
        ]
    },

    # ========================================================
    # FOLIUM — МАРКЕР + ЛОКАЛЬНОЕ ФОТО
    # ========================================================

    "Добавить маркер с фото из файла": {
        "template": (
            "_img_uri_{var2} = image_to_data_uri({var6})\n"
            "\n"
            "_html_{var2} = (\n"
            "    '<div style=\"width:320px;\">'\n"
            "    '<h3 style=\"text-align:center;\">' +\n"
            "    str({var5}) +\n"
            "    '</h3>'\n"
            "    '<img src=\"' +\n"
            "    _img_uri_{var2} +\n"
            "    '\" width=\"300\" '\n"
            "    'style=\"display:block;'\n"
            "    'margin:auto;'\n"
            "    'border-radius:10px;\">'\n"
            "    '<p style=\"text-align:center;'\n"
            "    'font-size:15px;\">' +\n"
            "    str({var7}) +\n"
            "    '</p>'\n"
            "    '</div>'\n"
            ")\n"
            "\n"
            "_popup_{var2} = folium.Popup(\n"
            "    IFrame(\n"
            "        _html_{var2},\n"
            "        width=340,\n"
            "        height=380\n"
            "    ),\n"
            "    max_width=340\n"
            ")\n"
            "\n"
            "_marker_{var2} = folium.Marker(\n"
            "    location=[{var3}, {var4}],\n"
            "    popup=_popup_{var2},\n"
            "    tooltip={var5}\n"
            ")\n"
            "\n"
            "_marker_{var2}.add_to({var1})\n"
            "\n"
            "if {var8}:\n"
            "    _route_points.append(({var3}, {var4}))"
        ),
        "vars": [
            "Переменная карты",
            "Уникальное имя точки",
            "Широта",
            "Долгота",
            "Название",
            "Путь к изображению",
            "Описание",
            "Маршрутная точка (True/False)"
        ],
        "type": "folium",
        "imports": [
            "import folium",
            "import base64",
            "import mimetypes",
            "from folium import IFrame"
        ],
        "helpers": [
            "image_to_data_uri"
        ]
    },

    # ========================================================
    # FOLIUM — МАРКЕР + URL ФОТО
    # ========================================================

    "Добавить маркер с фото по URL": {
        "template": (
            "_html_{var2} = (\n"
            "    '<div style=\"width:320px;\">'\n"
            "    '<h3 style=\"text-align:center;\">' +\n"
            "    str({var5}) +\n"
            "    '</h3>'\n"
            "    '<img src=\"' +\n"
            "    str({var6}) +\n"
            "    '\" width=\"300\" '\n"
            "    'style=\"display:block;'\n"
            "    'margin:auto;'\n"
            "    'border-radius:10px;\">'\n"
            "    '<p style=\"text-align:center;'\n"
            "    'font-size:15px;\">' +\n"
            "    str({var7}) +\n"
            "    '</p>'\n"
            "    '</div>'\n"
            ")\n"
            "\n"
            "_popup_{var2} = folium.Popup(\n"
            "    IFrame(\n"
            "        _html_{var2},\n"
            "        width=340,\n"
            "        height=380\n"
            "    ),\n"
            "    max_width=340\n"
            ")\n"
            "\n"
            "_marker_{var2} = folium.Marker(\n"
            "    location=[{var3}, {var4}],\n"
            "    popup=_popup_{var2},\n"
            "    tooltip={var5}\n"
            ")\n"
            "\n"
            "_marker_{var2}.add_to({var1})\n"
            "\n"
            "if {var8}:\n"
            "    _route_points.append(({var3}, {var4}))"
        ),
        "vars": [
            "Переменная карты",
            "Уникальное имя точки",
            "Широта",
            "Долгота",
            "Название",
            "URL изображения",
            "Описание",
            "Маршрутная точка (True/False)"
        ],
        "type": "folium",
        "imports": [
            "import folium",
            "from folium import IFrame"
        ]
    },

    # ========================================================
    # ПОИСК + URL ФОТО
    # ========================================================

    "Добавить точку по поиску с фото URL": {
        "template": (
            "try:\n"
            "    _search_result_{var2} = ox.geocode({var3})\n"
            "except Exception as _search_error_{var2}:\n"
            "    raise RuntimeError(\n"
            "        'Не удалось найти точку ' +\n"
            "        str({var3}) +\n"
            "        ': ' +\n"
            "        str(_search_error_{var2})\n"
            "    )\n"
            "\n"
            "if not _search_result_{var2}:\n"
            "    raise RuntimeError(\n"
            "        'Точка не найдена: ' + str({var3})\n"
            "    )\n"
            "\n"
            "_lat_{var2} = float(_search_result_{var2}[0])\n"
            "_lon_{var2} = float(_search_result_{var2}[1])\n"
            "\n"
            "_html_{var2} = (\n"
            "    '<div style=\"width:320px;\">'\n"
            "    '<h3 style=\"text-align:center;\">' +\n"
            "    str({var4}) +\n"
            "    '</h3>'\n"
            "    '<img src=\"' +\n"
            "    str({var5}) +\n"
            "    '\" width=\"300\" '\n"
            "    'style=\"display:block;'\n"
            "    'margin:auto;'\n"
            "    'border-radius:10px;\">'\n"
            "    '<p style=\"text-align:center;'\n"
            "    'font-size:15px;\">' +\n"
            "    str({var6}) +\n"
            "    '</p>'\n"
            "    '</div>'\n"
            ")\n"
            "\n"
            "_popup_{var2} = folium.Popup(\n"
            "    IFrame(\n"
            "        _html_{var2},\n"
            "        width=340,\n"
            "        height=380\n"
            "    ),\n"
            "    max_width=340\n"
            ")\n"
            "\n"
            "_marker_{var2} = folium.Marker(\n"
            "    location=[_lat_{var2}, _lon_{var2}],\n"
            "    popup=_popup_{var2},\n"
            "    tooltip={var4}\n"
            ")\n"
            "\n"
            "_marker_{var2}.add_to({var1})\n"
            "\n"
            "if {var7}:\n"
            "    _route_points.append(\n"
            "        (_lat_{var2}, _lon_{var2})\n"
            "    )"
        ),
        "vars": [
            "Переменная карты",
            "Уникальное имя точки",
            "Поиск / адрес",
            "Название",
            "URL изображения",
            "Описание",
            "Маршрутная точка (True/False)"
        ],
        "type": "folium",
        "imports": [
            "import folium",
            "import osmnx as ox",
            "from folium import IFrame"
        ]
    },

    # ========================================================
    # ПОИСК + ЛОКАЛЬНОЕ ФОТО
    # ========================================================

    "Добавить точку по поиску с локальным фото": {
        "template": (
            "try:\n"
            "    _search_result_{var2} = ox.geocode({var3})\n"
            "except Exception as _search_error_{var2}:\n"
            "    raise RuntimeError(\n"
            "        'Не удалось найти точку ' +\n"
            "        str({var3}) +\n"
            "        ': ' +\n"
            "        str(_search_error_{var2})\n"
            "    )\n"
            "\n"
            "if not _search_result_{var2}:\n"
            "    raise RuntimeError(\n"
            "        'Точка не найдена: ' + str({var3})\n"
            "    )\n"
            "\n"
            "_lat_{var2} = float(_search_result_{var2}[0])\n"
            "_lon_{var2} = float(_search_result_{var2}[1])\n"
            "\n"
            "_img_uri_{var2} = image_to_data_uri({var5})\n"
            "\n"
            "_html_{var2} = (\n"
            "    '<div style=\"width:320px;\">'\n"
            "    '<h3 style=\"text-align:center;\">' +\n"
            "    str({var4}) +\n"
            "    '</h3>'\n"
            "    '<img src=\"' +\n"
            "    _img_uri_{var2} +\n"
            "    '\" width=\"300\" '\n"
            "    'style=\"display:block;'\n"
            "    'margin:auto;'\n"
            "    'border-radius:10px;\">'\n"
            "    '<p style=\"text-align:center;'\n"
            "    'font-size:15px;\">' +\n"
            "    str({var6}) +\n"
            "    '</p>'\n"
            "    '</div>'\n"
            ")\n"
            "\n"
            "_popup_{var2} = folium.Popup(\n"
            "    IFrame(\n"
            "        _html_{var2},\n"
            "        width=340,\n"
            "        height=380\n"
            "    ),\n"
            "    max_width=340\n"
            ")\n"
            "\n"
            "_marker_{var2} = folium.Marker(\n"
            "    location=[_lat_{var2}, _lon_{var2}],\n"
            "    popup=_popup_{var2},\n"
            "    tooltip={var4}\n"
            ")\n"
            "\n"
            "_marker_{var2}.add_to({var1})\n"
            "\n"
            "if {var7}:\n"
            "    _route_points.append(\n"
            "        (_lat_{var2}, _lon_{var2})\n"
            "    )"
        ),
        "vars": [
            "Переменная карты",
            "Уникальное имя точки",
            "Поиск / адрес",
            "Название",
            "Путь к изображению",
            "Описание",
            "Маршрутная точка (True/False)"
        ],
        "type": "folium",
        "imports": [
            "import folium",
            "import base64",
            "import mimetypes",
            "import osmnx as ox",
            "from folium import IFrame"
        ],
        "helpers": [
            "image_to_data_uri"
        ]
    },

    # ========================================================
    # ЭКСПОРТ HTML
    # ========================================================

    "Экспорт HTML": {
        "template": (
            "{var1}.save({var2})"
        ),
        "vars": [
            "Переменная карты",
            "Имя HTML-файла"
        ],
        "type": "folium",
        "imports": [
            "import folium"
        ]
    },

    # ========================================================
    # ЛИНИЯ
    # ========================================================

    "Добавить линию": {
        "template": (
            "folium.PolyLine(\n"
            "    {var2},\n"
            "    color={var3},\n"
            "    weight={var4},\n"
            "    opacity={var5}\n"
            ").add_to({var1})"
        ),
        "vars": [
            "Переменная карты",
            "Список координат",
            "Цвет",
            "Толщина",
            "Прозрачность"
        ],
        "type": "folium",
        "imports": [
            "import folium"
        ]
    },

    # ========================================================
    # ПОДПИСЬ
    # ========================================================

    "Добавить подпись": {
        "template": (
            "folium.Marker(\n"
            "    location=[{var2}, {var3}],\n"
            "    icon=folium.DivIcon(\n"
            "        html=f'''"
            "<div style=\""
            "color:{var5};"
            "font-size:{var6}px;"
            "font-weight:bold;"
            "white-space:nowrap;"
            "\">"
            "{var4}"
            "</div>"
            "'''"
            "    )\n"
            ").add_to({var1})"
        ),
        "vars": [
            "Переменная карты",
            "Широта",
            "Долгота",
            "Текст",
            "Цвет",
            "Размер шрифта"
        ],
        "type": "folium",
        "imports": [
            "import folium"
        ]
    },

    # ========================================================
    # ГРАНИЦЫ
    # ========================================================

    "Показать карту по границам": {
        "template": (
            "{var1}.fit_bounds({var2})"
        ),
        "vars": [
            "Переменная карты",
            "Список координат"
        ],
        "type": "folium",
        "imports": [
            "import folium"
        ]
    },

    # ========================================================
    # МАРШРУТ
    # ========================================================

    "Построить маршрут по маршрутным точкам": {
        "template": (
            "if len(_route_points) >= 2:\n"
            "\n"
            "    _coords_string = ';'.join(\n"
            "        f'{lon},{lat}'\n"
            "        for lat, lon in _route_points\n"
            "    )\n"
            "\n"
            "    _url = (\n"
            "        'https://router.project-osrm.org/'\n"
            "        'route/v1/driving/'\n"
            "        + _coords_string\n"
            "        + '?overview=full&geometries=geojson'\n"
            "    )\n"
            "\n"
            "    _response = requests.get(\n"
            "        _url,\n"
            "        timeout=30\n"
            "    )\n"
            "    _response.raise_for_status()\n"
            "\n"
            "    _route_data = _response.json()\n"
            "\n"
            "    if _route_data.get('routes'):\n"
            "\n"
            "        _route = _route_data['routes'][0]\n"
            "\n"
            "        _route_distance_km = (\n"
            "            _route['distance'] / 1000\n"
            "        )\n"
            "\n"
            "        _route_duration_min = (\n"
            "            _route['duration'] / 60\n"
            "        )\n"
            "\n"
            "        _route_coordinates = [\n"
            "            [lat, lon]\n"
            "            for lon, lat in\n"
            "            _route['geometry']['coordinates']\n"
            "        ]\n"
            "\n"
            "        folium.PolyLine(\n"
            "            _route_coordinates,\n"
            "            color='blue',\n"
            "            weight=6,\n"
            "            opacity=0.8,\n"
            "            tooltip=(\n"
            "                f'Маршрут: '\n"
            "                f'{_route_distance_km:.2f} км | '\n"
            "                f'{_route_duration_min:.0f} мин.'\n"
            "            )\n"
            "        ).add_to({var1})\n"
            "\n"
            "        if _route_coordinates:\n"
            "\n"
            "            _route_middle_index = (\n"
            "                len(_route_coordinates) // 2\n"
            "            )\n"
            "\n"
            "            _route_middle = (\n"
            "                _route_coordinates[_route_middle_index]\n"
            "            )\n"
            "\n"
            "            _route_info_html = f'''"
            "            <div style=\""
            "                background:white;"
            "                padding:10px 16px;"
            "                border:2px solid #333;"
            "                border-radius:10px;"
            "                font-size:15px;"
            "                font-weight:bold;"
            "                white-space:nowrap;"
            "                box-shadow:0 2px 8px rgba(0,0,0,0.3);"
            "                text-align:center;"
            "                transform:translate(-50%,-50%);"
            "            \">"
            "                🚗 Маршрут<br>"
            "                📏 {_route_distance_km:.2f} км<br>"
            "                ⏱ {_route_duration_min:.0f} мин."
            "            </div>"
            "            '''\n"
            "\n"
            "            folium.Marker(\n"
            "                location=_route_middle,\n"
            "                icon=folium.DivIcon(\n"
            "                    html=_route_info_html,\n"
            "                    icon_size=(180, 80),\n"
            "                    icon_anchor=(90, 40)\n"
            "                )\n"
            "            ).add_to({var1})\n"
            "\n"
            "    else:\n"
            "        print('OSRM не вернул маршрут.')\n"
            "\n"
            "else:\n"
            "    print(\n"
            "        'Для маршрута нужно минимум '\n"
            "        '2 маршрутные точки.'\n"
            "    )"
        ),
        "vars": [
            "Переменная карты"
        ],
        "type": "folium",
        "imports": [
            "import folium",
            "import requests"
        ]
    }
}


# ============================================================
# HELPERS
# ============================================================

HELPERS = {

    "image_to_data_uri": '''
def image_to_data_uri(path):
    import base64
    import mimetypes

    path = str(path)

    mime_type, _ = mimetypes.guess_type(path)

    if not mime_type:
        mime_type = "image/jpeg"

    with open(path, "rb") as img:
        encoded = base64.b64encode(
            img.read()
        ).decode("utf-8")

    return "data:" + mime_type + ";base64," + encoded
''',

    "image_to_base64": '''
def image_to_base64(path):
    import base64

    with open(path, "rb") as img:
        return base64.b64encode(
            img.read()
        ).decode("utf-8")
'''
}


# ============================================================
# ГЛОБАЛЬНЫЕ ПЕРЕМЕННЫЕ
# ============================================================

constructor_window = None

frame = None
combo = None
textbox = None
title_entry = None
size_entry = None

input_widgets = []

added_command_types = []

used_imports = set()
used_helpers = set()


# ============================================================
# PYTHON STRING
# ============================================================

def python_string(value):
    return (
        value
        .replace("\\", "\\\\")
        .replace("'", "\\'")
        .replace("\n", "\\n")
        .replace("\r", "\\r")
    )


def python_double_string(value):
    return (
        value
        .replace("\\", "\\\\")
        .replace('"', '\\"')
        .replace("\n", "\\n")
        .replace("\r", "\\r")
    )


def quote_value(value):
    if value.startswith(("'", '"')):
        return value

    return "'" + python_string(value) + "'"


# ============================================================
# ОЧИСТКА ПОЛЕЙ
# ============================================================

def clear_input_area():
    for widget in input_widgets:
        try:
            widget.destroy()
        except Exception:
            pass

    input_widgets.clear()


# ============================================================
# ИЗОБРАЖЕНИЕ
# ============================================================

def browse_image(entry):
    path = filedialog.askopenfilename(
        parent=constructor_window,
        title="Выберите изображение",
        filetypes=[
            (
                "Изображения",
                "*.png *.jpg *.jpeg *.gif *.webp *.bmp"
            ),
            (
                "Все файлы",
                "*.*"
            )
        ]
    )

    if not path:
        return

    entry.delete(0, "end")
    entry.insert(0, path)


# ============================================================
# ИЗМЕНЕНИЕ КОМАНДЫ
# ============================================================

def on_command_change(event=None):

    clear_input_area()

    selected = combo.get()

    if selected not in COMMANDS_DB:
        return

    command = COMMANDS_DB[selected]

    variables = command.get("vars", [])

    for index, variable_name in enumerate(variables):

        row = 4 + index

        label = ctk.CTkLabel(
            frame,
            text=variable_name + ":",
            width=260,
            anchor="e"
        )

        label.grid(
            row=row,
            column=0,
            sticky="e",
            padx=10,
            pady=5
        )

        input_widgets.append(label)

        is_image_file = (
            "Путь к изображению" in variable_name
            and selected in (
                "Добавить маркер с фото из файла",
                "Добавить изображение из файла",
                "Добавить точку по поиску с локальным фото"
            )
        )

        if is_image_file:

            container = ctk.CTkFrame(
                frame,
                fg_color="transparent"
            )

            container.grid(
                row=row,
                column=1,
                sticky="w",
                padx=10,
                pady=5
            )

            entry = ctk.CTkEntry(
                container,
                width=210
            )

            entry.pack(side="left")

            browse_button = ctk.CTkButton(
                container,
                text="Обзор...",
                width=80,
                command=lambda e=entry: browse_image(e)
            )

            browse_button.pack(
                side="left",
                padx=(5, 0)
            )

            input_widgets.append(container)
            input_widgets.append(entry)

        else:

            entry = ctk.CTkEntry(
                frame,
                width=350
            )

            entry.grid(
                row=row,
                column=1,
                sticky="w",
                padx=10,
                pady=5
            )

            input_widgets.append(entry)


# ============================================================
# ЗАМЕНА ПЕРЕМЕННЫХ
# ============================================================

def replace_template_variables(template, values):

    result = template

    for index, value in enumerate(values, start=1):

        result = result.replace(
            f"{{var{index}}}",
            value
        )

    unresolved = re.findall(
        r"\{var\d+\}",
        result
    )

    if unresolved:
        raise ValueError(
            "В шаблоне остались незаменённые переменные:\n\n"
            + "\n".join(sorted(set(unresolved)))
        )

    return result


# ============================================================
# BOOL
# ============================================================

def normalize_bool(value):

    value = value.strip().lower()

    true_values = {
        "true",
        "1",
        "да",
        "yes",
        "y",
        "on"
    }

    false_values = {
        "false",
        "0",
        "нет",
        "no",
        "n",
        "off"
    }

    if value in true_values:
        return "True"

    if value in false_values:
        return "False"

    return value


# ============================================================
# IDENTIFIER
# ============================================================

def safe_identifier(value):

    value = re.sub(
        r"\W+",
        "_",
        value,
        flags=re.UNICODE
    )

    if not value:
        value = "point"

    if value[0].isdigit():
        value = "_" + value

    return value


# ============================================================
# ДОБАВЛЕНИЕ КОМАНДЫ
# ============================================================

def add_command():

    selected = combo.get()

    if selected not in COMMANDS_DB:

        messagebox.showwarning(
            "Внимание",
            "Выберите команду.",
            parent=constructor_window
        )

        return

    command = COMMANDS_DB[selected]

    entries = [
        widget
        for widget in input_widgets
        if isinstance(widget, ctk.CTkEntry)
    ]

    variables = command.get("vars", [])

    if len(entries) != len(variables):

        messagebox.showerror(
            "Ошибка",
            "Количество полей не совпадает.",
            parent=constructor_window
        )

        return

    values = []

    for entry in entries:

        value = entry.get().strip()

        if not value:

            messagebox.showwarning(
                "Внимание",
                "Заполните все поля.",
                parent=constructor_window
            )

            return

        values.append(value)

    # --------------------------------------------------------
    # GUI
    # --------------------------------------------------------

    if selected in (
        "Добавить кнопку",
        "Добавить метку",
        "Добавить чекбокс"
    ):
        values[1] = quote_value(values[1])

    if selected == "Добавить ComboBox":

        raw = values[1]

        if not raw.startswith("["):

            items = [
                x.strip()
                for x in raw.split(",")
                if x.strip()
            ]

            values[1] = repr(items)

    if selected == "Добавить изображение по URL":
        values[1] = quote_value(values[1])

    if selected == "Добавить изображение из файла":
        values[1] = quote_value(values[1])

    # --------------------------------------------------------
    # Обычный маркер
    # --------------------------------------------------------

    if selected == "Добавить маркер":

        values[4] = quote_value(values[4])
        values[5] = quote_value(values[5])
        values[6] = normalize_bool(values[6])
        values[1] = safe_identifier(values[1])

    # --------------------------------------------------------
    # Маркер + локальное фото
    # --------------------------------------------------------

    if selected == "Добавить маркер с фото из файла":

        values[4] = quote_value(values[4])
        values[5] = quote_value(values[5])
        values[6] = quote_value(values[6])
        values[7] = normalize_bool(values[7])
        values[1] = safe_identifier(values[1])

    # --------------------------------------------------------
    # Маркер + URL фото
    # --------------------------------------------------------

    if selected == "Добавить маркер с фото по URL":

        values[4] = quote_value(values[4])
        values[5] = quote_value(values[5])
        values[6] = quote_value(values[6])
        values[7] = normalize_bool(values[7])
        values[1] = safe_identifier(values[1])

    # --------------------------------------------------------
    # Поиск + URL фото
    # --------------------------------------------------------

    if selected == "Добавить точку по поиску с фото URL":

        values[2] = quote_value(values[2])
        values[3] = quote_value(values[3])
        values[4] = quote_value(values[4])
        values[5] = quote_value(values[5])
        values[6] = normalize_bool(values[6])
        values[1] = safe_identifier(values[1])

    # --------------------------------------------------------
    # Поиск + локальное фото
    # --------------------------------------------------------

    if selected == "Добавить точку по поиску с локальным фото":

        values[2] = quote_value(values[2])
        values[3] = quote_value(values[3])
        values[4] = quote_value(values[4])
        values[5] = quote_value(values[5])
        values[6] = normalize_bool(values[6])
        values[1] = safe_identifier(values[1])

    # --------------------------------------------------------
    # Экспорт HTML
    # --------------------------------------------------------

    if selected == "Экспорт HTML":

        values[1] = quote_value(values[1])

    # --------------------------------------------------------
    # Линия
    # --------------------------------------------------------

    if selected == "Добавить линию":

        values[2] = quote_value(values[2])

    # --------------------------------------------------------
    # Подпись
    # --------------------------------------------------------

    if selected == "Добавить подпись":

        values[3] = quote_value(values[3])
        values[4] = quote_value(values[4])

    # --------------------------------------------------------
    # Генерация
    # --------------------------------------------------------

    try:

        generated = replace_template_variables(
            command["template"],
            values
        )

    except Exception as e:

        messagebox.showerror(
            "Ошибка шаблона",
            str(e),
            parent=constructor_window
        )

        return

    textbox.insert(
        "end",
        generated + "\n\n"
    )

    textbox.see("end")

    added_command_types.append(
        command.get("type", "python")
    )

    for imp in command.get("imports", []):

        used_imports.add(imp)

    for helper in command.get("helpers", []):

        used_helpers.add(helper)


# ============================================================
# ОЧИСТИТЬ КОД
# ============================================================

def clear_code():

    textbox.delete(
        "1.0",
        "end"
    )

    added_command_types.clear()
    used_imports.clear()
    used_helpers.clear()


# ============================================================
# ОТКРЫТЬ PYTHON
# ============================================================

def open_py_file():

    path = filedialog.askopenfilename(
        parent=constructor_window,
        title="Открыть Python-файл",
        filetypes=[
            (
                "Python",
                "*.py"
            ),
            (
                "Все файлы",
                "*.*"
            )
        ]
    )

    if not path:
        return

    try:

        with open(
            path,
            "r",
            encoding="utf-8-sig"
        ) as file:

            code = file.read()

    except UnicodeDecodeError:

        try:

            with open(
                path,
                "r",
                encoding="cp1251"
            ) as file:

                code = file.read()

        except Exception as e:

            messagebox.showerror(
                "Ошибка открытия",
                str(e),
                parent=constructor_window
            )

            return

    except Exception as e:

        messagebox.showerror(
            "Ошибка открытия",
            str(e),
            parent=constructor_window
        )

        return

    textbox.delete(
        "1.0",
        "end"
    )

    textbox.insert(
        "1.0",
        code
    )

    textbox.see("1.0")

    used_imports.clear()
    used_helpers.clear()
    added_command_types.clear()

    if "folium" in code:
        used_imports.add("import folium")
        added_command_types.append("folium")

    if "requests" in code:
        used_imports.add("import requests")

    if "osmnx" in code or "ox." in code:
        used_imports.add("import osmnx as ox")

    if "base64" in code:
        used_imports.add("import base64")

    if "mimetypes" in code:
        used_imports.add("import mimetypes")

    if "BytesIO(" in code:
        used_imports.add("from io import BytesIO")

    if "Image.open" in code:
        used_imports.add("from PIL import Image")

    if "IFrame(" in code:
        used_imports.add("from folium import IFrame")

    if "image_to_base64(" in code:
        used_helpers.add("image_to_base64")

    if "image_to_data_uri(" in code:
        used_helpers.add("image_to_data_uri")

    messagebox.showinfo(
        "Файл открыт",
        f"Python-файл загружен:\n\n{path}",
        parent=constructor_window
    )


# ============================================================
# ПРОВЕРКА БИБЛИОТЕК
# ============================================================

def install_required_for_code():

    required = []

    if any(
        "folium" in imp
        for imp in used_imports
    ):
        required.append(
            ("folium", "folium")
        )

    if any(
        "requests" in imp
        for imp in used_imports
    ):
        required.append(
            ("requests", "requests")
        )

    if any(
        "customtkinter" in imp
        for imp in used_imports
    ):
        required.append(
            ("customtkinter", "customtkinter")
        )

    if any(
        "PIL" in imp
        for imp in used_imports
    ):
        required.append(
            ("Pillow", "PIL")
        )

    if any(
        "osmnx" in imp
        for imp in used_imports
    ):
        required.append(
            ("osmnx", "osmnx")
        )

    failed = []

    for package, module in required:

        try:

            __import__(module)

        except ImportError:

            if not install_package(package):
                failed.append(package)

    if failed:

        messagebox.showerror(
            "Ошибка библиотек",
            "Не удалось установить:\n\n"
            + "\n".join(failed),
            parent=constructor_window
        )

        return False

    return True


# ============================================================
# HEADER
# ============================================================

def generate_header(
    has_gui,
    has_folium
):

    imports = set(used_imports)

    if has_gui:
        imports.add(
            "import customtkinter as ctk"
        )

    if has_folium:
        imports.add(
            "import folium"
        )

    lines = [
        "# -*- coding: utf-8 -*-",
        ""
    ]

    preferred_order = [

        "import customtkinter as ctk",

        "import folium",

        "import requests",

        "import osmnx as ox",

        "import base64",

        "import mimetypes",

        "from io import BytesIO",

        "from PIL import Image",

        "from folium import IFrame"
    ]

    for imp in preferred_order:

        if imp in imports:
            lines.append(imp)

    for imp in sorted(imports):

        if imp not in preferred_order:
            lines.append(imp)

    lines.append("")

    return "\n".join(lines)


# ============================================================
# ПОЛНЫЙ СКРИПТ
# ============================================================

def generate_full_script():

    user_code = textbox.get(
        "1.0",
        "end"
    ).strip()

    if not user_code:

        messagebox.showwarning(
            "Внимание",
            "Сначала добавьте код.",
            parent=constructor_window
        )

        return None

    has_gui = (
        "gui" in added_command_types
        or "ctk." in user_code
    )

    has_folium = (
        "folium" in added_command_types
        or "folium." in user_code
    )

    # --------------------------------------------------------
    # Автоматические импорты
    # --------------------------------------------------------

    if "requests." in user_code:
        used_imports.add(
            "import requests"
        )

    if "ox." in user_code:
        used_imports.add(
            "import osmnx as ox"
        )

    if "base64." in user_code:
        used_imports.add(
            "import base64"
        )

    if "mimetypes." in user_code:
        used_imports.add(
            "import mimetypes"
        )

    if "BytesIO(" in user_code:
        used_imports.add(
            "from io import BytesIO"
        )

    if "Image." in user_code:
        used_imports.add(
            "from PIL import Image"
        )

    if "IFrame(" in user_code:
        used_imports.add(
            "from folium import IFrame"
        )

    if "image_to_base64(" in user_code:
        used_helpers.add(
            "image_to_base64"
        )

    if "image_to_data_uri(" in user_code:
        used_helpers.add(
            "image_to_data_uri"
        )

    # --------------------------------------------------------
    # Helpers
    # --------------------------------------------------------

    helper_text = ""

    for helper_name in used_helpers:

        helper_text += (
            HELPERS[helper_name]
            + "\n"
        )

    # --------------------------------------------------------
    # Header
    # --------------------------------------------------------

    header = generate_header(
        has_gui,
        has_folium
    )

    parts = [
        header
    ]

    # --------------------------------------------------------
    # Helpers
    # --------------------------------------------------------

    if helper_text:

        parts.append(

            "# ============================================================\n"
            "# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ\n"
            "# ============================================================\n\n"
            + helper_text
        )

    # --------------------------------------------------------
    # GUI
    # --------------------------------------------------------

    if has_gui:

        window_title = (
            title_entry.get().strip()
            or "Моё приложение"
        )

        window_size = (
            size_entry.get().strip()
            or "400x300"
        )

        safe_title = python_double_string(
            window_title
        )

        parts.append(

            f'''
# ============================================================
# ГЛАВНОЕ ОКНО
# ============================================================

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

root = ctk.CTk()

root.title("{safe_title}")

root.geometry("{window_size}")


# ============================================================
# ОСНОВНОЙ FRAME
# ============================================================

frame = ctk.CTkFrame(root)

frame.pack(
    padx=20,
    pady=20,
    fill="both",
    expand=True
)
'''
        )

    # --------------------------------------------------------
    # Код пользователя
    # --------------------------------------------------------

    parts.append(

        '''
# ============================================================
# КОД, СОЗДАННЫЙ В КОНСТРУКТОРЕ
# ============================================================

'''
        + user_code
        + "\n"
    )

    # --------------------------------------------------------
    # Mainloop
    # --------------------------------------------------------

    if has_gui:

        parts.append(

            '''
# ============================================================
# ЗАПУСК
# ============================================================

root.mainloop()
'''
        )

    return "\n".join(parts)


# ============================================================
# СОХРАНИТЬ PY
# ============================================================

def save_as_py():

    script = generate_full_script()

    if script is None:
        return

    try:

        compile(
            script,
            "<generated>",
            "exec"
        )

    except SyntaxError as e:

        messagebox.showerror(
            "Ошибка синтаксиса",
            (
                f"{e}\n\n"
                f"Строка: {e.lineno}\n"
                f"Текст: {e.text or ''}"
            ),
            parent=constructor_window
        )

        return

    path = filedialog.asksaveasfilename(

        parent=constructor_window,

        title="Сохранить Python-файл",

        defaultextension=".py",

        filetypes=[
            (
                "Python",
                "*.py"
            ),
            (
                "Все файлы",
                "*.*"
            )
        ]
    )

    if not path:
        return

    try:

        with open(
            path,
            "w",
            encoding="utf-8"
        ) as file:

            file.write(script)

        messagebox.showinfo(
            "Готово",
            "Python-файл сохранён:\n\n"
            + path,
            parent=constructor_window
        )

    except Exception as e:

        messagebox.showerror(
            "Ошибка сохранения",
            str(e),
            parent=constructor_window
        )


# ============================================================
# ЭКСПОРТ HTML
# ============================================================

def export_html():

    code = textbox.get(
        "1.0",
        "end"
    ).strip()

    if not code:

        messagebox.showwarning(
            "Внимание",
            "Сначала создайте карту.",
            parent=constructor_window
        )

        return

    # Ищем наиболее очевидную переменную Folium-карты.
    map_variables = re.findall(
        r"([A-Za-z_]\w*)\s*=\s*folium\.Map\s*\(",
        code
    )

    if not map_variables:

        messagebox.showwarning(
            "Карта не найдена",
            (
                "В коде не найдена конструкция:\n\n"
                "имя_карты = folium.Map(...)"
            ),
            parent=constructor_window
        )

        return

    if len(map_variables) == 1:

        map_variable = map_variables[0]

    else:

        map_variable = simpledialog.askstring(
            "Переменная карты",
            "Введите имя карты:\n\n"
            + "\n".join(map_variables),
            initialvalue=map_variables[-1],
            parent=constructor_window
        )

        if not map_variable:
            return

    path = filedialog.asksaveasfilename(
        parent=constructor_window,
        title="Экспорт карты в HTML",
        defaultextension=".html",
        filetypes=[
            (
                "HTML",
                "*.html"
            ),
            (
                "Все файлы",
                "*.*"
            )
        ]
    )

    if not path:
        return

    # Добавляем сохранение непосредственно
    # в создаваемый Python-код.
    export_line = (
        "\n\n"
        "# ============================================================\n"
        "# ЭКСПОРТ HTML\n"
        "# ============================================================\n\n"
        f"{map_variable}.save({quote_value(path)})\n"
    )

    # Не добавляем второй экспорт при повторном нажатии.
    textbox.insert(
        "end",
        export_line
    )

    textbox.see("end")

    script = generate_full_script()

    if script is None:
        return

    try:

        compile(
            script,
            "<generated>",
            "exec"
        )

    except SyntaxError as e:

        messagebox.showerror(
            "Ошибка синтаксиса",
            (
                f"{e}\n\n"
                f"Строка: {e.lineno}\n"
                f"Текст: {e.text or ''}"
            ),
            parent=constructor_window
        )

        return

    if not install_required_for_code():
        return

    temp_path = None

    try:

        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".py",
            prefix="html_export_",
            delete=False,
            encoding="utf-8"
        ) as temp:

            temp.write(script)
            temp_path = temp.name

        process = subprocess.Popen([
            sys.executable,
            temp_path
        ])

        def wait_and_cleanup():

            try:
                return_code = process.wait()

                if return_code == 0:

                    constructor_window.after(
                        0,
                        lambda: messagebox.showinfo(
                            "HTML экспортирован",
                            "Карта сохранена:\n\n" + path,
                            parent=constructor_window
                        )
                    )

                else:

                    constructor_window.after(
                        0,
                        lambda: messagebox.showerror(
                            "Ошибка экспорта",
                            (
                                "Python завершился с кодом "
                                + str(return_code)
                            ),
                            parent=constructor_window
                        )
                    )

            except Exception as e:

                constructor_window.after(
                    0,
                    lambda: messagebox.showerror(
                        "Ошибка экспорта",
                        str(e),
                        parent=constructor_window
                    )
                )

            finally:

                if temp_path:

                    for _ in range(20):

                        try:

                            Path(
                                temp_path
                            ).unlink(
                                missing_ok=True
                            )

                            if not Path(
                                temp_path
                            ).exists():

                                break

                        except Exception:
                            pass

                        time.sleep(0.2)

        threading.Thread(
            target=wait_and_cleanup,
            daemon=True
        ).start()

    except Exception as e:

        if temp_path:

            try:
                Path(
                    temp_path
                ).unlink(
                    missing_ok=True
                )
            except Exception:
                pass

        messagebox.showerror(
            "Ошибка экспорта",
            str(e),
            parent=constructor_window
        )


# ============================================================
# ЗАПУСК PYTHON
# ============================================================

def run_code():

    script = generate_full_script()

    if script is None:
        return

    try:

        compile(
            script,
            "<generated>",
            "exec"
        )

    except SyntaxError as e:

        messagebox.showerror(
            "Ошибка синтаксиса",
            (
                f"{e}\n\n"
                f"Строка: {e.lineno}\n"
                f"Текст: {e.text or ''}"
            ),
            parent=constructor_window
        )

        return

    if not install_required_for_code():
        return

    temp_path = None

    try:

        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".py",
            prefix="constructor_",
            delete=False,
            encoding="utf-8"
        ) as temp:

            temp.write(script)
            temp_path = temp.name

        process = subprocess.Popen([
            sys.executable,
            temp_path
        ])

        def cleanup():

            try:
                process.wait()
            except Exception:
                pass

            for _ in range(20):

                try:

                    Path(
                        temp_path
                    ).unlink(
                        missing_ok=True
                    )

                    if not Path(
                        temp_path
                    ).exists():

                        break

                except Exception:
                    pass

                time.sleep(0.5)

        threading.Thread(
            target=cleanup,
            daemon=True
        ).start()

    except Exception as e:

        if temp_path:

            try:
                Path(
                    temp_path
                ).unlink(
                    missing_ok=True
                )
            except Exception:
                pass

        messagebox.showerror(
            "Ошибка запуска",
            str(e),
            parent=constructor_window
        )


# ============================================================
# ЗАГРУЗКА КОМАНД ИЗ TXT
# ============================================================

def load_commands_from_file():

    path = filedialog.askopenfilename(

        parent=constructor_window,

        title="Выберите TXT-файл",

        filetypes=[
            (
                "TXT",
                "*.txt"
            ),
            (
                "Все файлы",
                "*.*"
            )
        ]
    )

    if not path:
        return

    loaded = 0

    try:

        with open(
            path,
            "r",
            encoding="utf-8-sig"
        ) as file:

            for line in file:

                line = line.strip()

                if not line:
                    continue

                if line.startswith("#"):
                    continue

                parts = line.split(
                    "|",
                    3
                )

                if len(parts) < 3:
                    continue

                name = parts[0].strip()
                template = parts[1].strip()
                vars_text = parts[2].strip()

                command_type = (
                    parts[3].strip()
                    if len(parts) >= 4
                    else "python"
                )

                variables = []

                if vars_text:

                    variables = [
                        x.strip()
                        for x in vars_text.split(",")
                        if x.strip()
                    ]

                COMMANDS_DB[name] = {
                    "template": template,
                    "vars": variables,
                    "type": command_type,
                    "imports": []
                }

                loaded += 1

        refresh_combo()

        messagebox.showinfo(
            "Готово",
            f"Загружено команд: {loaded}",
            parent=constructor_window
        )

    except Exception as e:

        messagebox.showerror(
            "Ошибка",
            str(e),
            parent=constructor_window
        )


# ============================================================
# ОБНОВЛЕНИЕ COMBOBOX
# ============================================================

def refresh_combo():

    values = list(
        COMMANDS_DB.keys()
    )

    combo.configure(
        values=values
    )

    if values:

        combo.set(
            values[0]
        )

        on_command_change()


# ============================================================
# ОТКРЫТИЕ КОНСТРУКТОРА
# ============================================================

def open_constructor(parent=None):

    global constructor_window
    global frame
    global combo
    global textbox
    global title_entry
    global size_entry

    if (
        constructor_window is not None
        and constructor_window.winfo_exists()
    ):

        constructor_window.deiconify()
        constructor_window.lift()
        constructor_window.focus_force()

        return constructor_window

    constructor_window = ctk.CTkToplevel(
        parent
    )

    constructor_window.title(
        "Конструктор кода"
    )

    constructor_window.geometry(
        "1100x950"
    )

    constructor_window.minsize(
        900,
        750
    )

    # --------------------------------------------------------
    # FRAME
    # --------------------------------------------------------

    frame = ctk.CTkFrame(
        constructor_window
    )

    frame.pack(
        padx=15,
        pady=15,
        fill="both",
        expand=True
    )

    frame.rowconfigure(
        11,
        weight=1
    )

    frame.columnconfigure(
        1,
        weight=1
    )

    # --------------------------------------------------------
    # ЗАГОЛОВОК
    # --------------------------------------------------------

    ctk.CTkLabel(
        frame,
        text="Конструктор кода",
        font=ctk.CTkFont(
            size=24,
            weight="bold"
        )
    ).grid(
        row=0,
        column=0,
        columnspan=2,
        pady=(5, 15)
    )

    # --------------------------------------------------------
    # НАСТРОЙКИ
    # --------------------------------------------------------

    settings = ctk.CTkFrame(
        frame,
        fg_color="transparent"
    )

    settings.grid(
        row=1,
        column=0,
        columnspan=2,
        sticky="ew",
        pady=5
    )

    ctk.CTkLabel(
        settings,
        text="Название окна:"
    ).pack(
        side="left",
        padx=5
    )

    title_entry = ctk.CTkEntry(
        settings,
        width=180
    )

    title_entry.pack(
        side="left",
        padx=5
    )

    title_entry.insert(
        0,
        "Моё приложение"
    )

    ctk.CTkLabel(
        settings,
        text="Размер:"
    ).pack(
        side="left",
        padx=(20, 5)
    )

    size_entry = ctk.CTkEntry(
        settings,
        width=100
    )

    size_entry.pack(
        side="left",
        padx=5
    )

    size_entry.insert(
        0,
        "400x300"
    )

    # --------------------------------------------------------
    # КОМАНДА
    # --------------------------------------------------------

    ctk.CTkLabel(
        frame,
        text="Команда:"
    ).grid(
        row=2,
        column=0,
        sticky="e",
        padx=10,
        pady=5
    )

    combo = ctk.CTkComboBox(
        frame,
        values=list(
            COMMANDS_DB.keys()
        ),
        width=600,
        command=on_command_change
    )

    combo.grid(
        row=2,
        column=1,
        sticky="w",
        padx=10,
        pady=5
    )

    if COMMANDS_DB:

        combo.set(
            next(
                iter(COMMANDS_DB)
            )
        )

    # --------------------------------------------------------
    # ДОБАВИТЬ
    # --------------------------------------------------------

    ctk.CTkButton(
        frame,
        text="Добавить команду",
        command=add_command,
        width=180
    ).grid(
        row=3,
        column=1,
        sticky="w",
        padx=10,
        pady=10
    )

    # --------------------------------------------------------
    # РЕДАКТОР
    # --------------------------------------------------------

    textbox = ctk.CTkTextbox(
        frame,
        wrap="none",
        font=(
            "Consolas",
            14
        )
    )

    textbox.grid(
        row=11,
        column=0,
        columnspan=2,
        sticky="nsew",
        padx=10,
        pady=10
    )

    # --------------------------------------------------------
    # КНОПКИ
    # --------------------------------------------------------

    buttons = ctk.CTkFrame(
        frame,
        fg_color="transparent"
    )

    buttons.grid(
        row=12,
        column=0,
        columnspan=2,
        pady=10
    )

    ctk.CTkButton(
        buttons,
        text="Запустить код",
        command=run_code,
        width=140
    ).pack(
        side="left",
        padx=4
    )

    ctk.CTkButton(
        buttons,
        text="Экспорт HTML",
        command=export_html,
        width=140
    ).pack(
        side="left",
        padx=4
    )

    ctk.CTkButton(
        buttons,
        text="Открыть .py",
        command=open_py_file,
        width=130
    ).pack(
        side="left",
        padx=4
    )

    ctk.CTkButton(
        buttons,
        text="Сохранить .py",
        command=save_as_py,
        width=140
    ).pack(
        side="left",
        padx=4
    )

    ctk.CTkButton(
        buttons,
        text="Очистить код",
        command=clear_code,
        width=130
    ).pack(
        side="left",
        padx=4
    )

    ctk.CTkButton(
        buttons,
        text="Загрузить команды",
        command=load_commands_from_file,
        width=160
    ).pack(
        side="left",
        padx=4
    )

    # --------------------------------------------------------
    # ЗАКРЫТИЕ
    # --------------------------------------------------------

    def close_constructor():

        global constructor_window

        try:
            constructor_window.destroy()
        except Exception:
            pass

        constructor_window = None

    constructor_window.protocol(
        "WM_DELETE_WINDOW",
        close_constructor
    )

    # --------------------------------------------------------
    # ИНИЦИАЛИЗАЦИЯ
    # --------------------------------------------------------

    on_command_change()

    constructor_window.lift()
    constructor_window.focus_force()

    return constructor_window


# ============================================================
# САМОСТОЯТЕЛЬНЫЙ ЗАПУСК
# ============================================================

if __name__ == "__main__":

    root = ctk.CTk()

    root.title(
        "Конструктор кода"
    )

    root.geometry(
        "500x320"
    )

    ctk.CTkLabel(
        root,
        text="Конструктор кода",
        font=ctk.CTkFont(
            size=24,
            weight="bold"
        )
    ).pack(
        pady=(60, 20)
    )

    ctk.CTkLabel(
        root,
        text="Python + CustomTkinter + Folium"
    ).pack(
        pady=5
    )

    ctk.CTkButton(
        root,
        text="Открыть конструктор",
        width=250,
        height=45,
        command=lambda: open_constructor(root)
    ).pack(
        pady=25
    )

    root.mainloop()