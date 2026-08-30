# -*- coding: utf-8 -*-

import sys
import subprocess
import tempfile
import threading
import time
import re
from pathlib import Path
from tkinter import filedialog, messagebox


def install_package(package_name):
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", package_name
        ])
        return True
    except Exception:
        return False


def ensure_package(package_name, import_name=None):
    import_name = import_name or package_name
    try:
        __import__(import_name)
        return True
    except ImportError:
        return install_package(package_name)


if not ensure_package("customtkinter", "customtkinter"):
    raise SystemExit("Не удалось установить customtkinter.")

import customtkinter as ctk


ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


# ============================================================
# БАЗА КОМАНД
# ============================================================

COMMANDS_DB = {

    # --------------------------------------------------------
    # PYTHON
    # --------------------------------------------------------

    "Вывод (print)": {
        "template": "print({var1})",
        "vars": ["Текст или значение"],
        "type": "python",
        "imports": []
    },

    "Ввод (input)": {
        "template": "{var1} = input({var2})",
        "vars": ["Имя переменной", "Текст подсказки"],
        "type": "python",
        "imports": []
    },

    "Присваивание переменной": {
        "template": "{var1} = {var2}",
        "vars": ["Имя переменной", "Значение"],
        "type": "python",
        "imports": []
    },

    "Цикл for": {
        "template": (
            "for i in range({var1}):\n"
            "    pass"
        ),
        "vars": ["Количество повторений"],
        "type": "python",
        "imports": []
    },

    "Условие if": {
        "template": (
            "if {var1}:\n"
            "    pass"
        ),
        "vars": ["Условие"],
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

    # --------------------------------------------------------
    # GUI
    # --------------------------------------------------------

    "Добавить кнопку": {
        "template": (
            "{var1} = ctk.CTkButton("
            "frame, text={var2}, command={var3}"
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
            "frame, text={var2}"
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
            "frame, height={var2}"
            ")\n"
            "{var1}.pack("
            "pady=5, fill='both', expand=True"
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
            "frame, text={var2}"
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
            "frame, values={var2}"
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

    "Добавить изображение из файла": {
        "template": (
            "_img_path = {var2}\n"
            "_img = Image.open(_img_path).convert('RGBA')\n"
            "_img.thumbnail(({var3}, {var4}))\n"
            "{var1}_image = ctk.CTkImage("
            "light_image=_img, dark_image=_img, size=_img.size"
            ")\n"
            "{var1} = ctk.CTkLabel("
            "frame, text='', image={var1}_image"
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

    "Добавить изображение по URL": {
        "template": (
            "_response_{var1} = requests.get("
            "{var2}, timeout=30"
            ")\n"
            "_response_{var1}.raise_for_status()\n"
            "_image_data_{var1} = BytesIO("
            "_response_{var1}.content"
            ")\n"
            "_img_{var1} = Image.open("
            "_image_data_{var1}"
            ").convert('RGBA')\n"
            "_img_{var1}.thumbnail(({var3}, {var4}))\n"
            "{var1}_image = ctk.CTkImage("
            "light_image=_img_{var1}, "
            "dark_image=_img_{var1}, "
            "size=_img_{var1}.size"
            ")\n"
            "{var1} = ctk.CTkLabel("
            "frame, text='', image={var1}_image"
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
    # FOLIUM
    # ========================================================

    "Создать карту": {
        "template": (
            "# ==================================================\n"
            "# КАРТА\n"
            "# ==================================================\n"
            "\n"
            "{var1} = folium.Map(\n"
            "    location=[{var2}, {var3}],\n"
            "    zoom_start={var4},\n"
            "    control_scale=True,\n"
            "    attribution_control=False\n"
            ")\n"
            "\n"
            "# Создаём собственный attribution-контрол.\n"
            "# Стандартный Leaflet prefix с украинским флагом\n"
            "# НЕ используется.\n"
            "\n"
            "_attribution_{var1} = folium.Element(\n"
            "    '''\n"
            "    <script>\n"
            "    (function() {\n"
            "        function setupAttribution() {\n"
            "            var mapObject = window.{var1};\n"
            "\n"
            "            if (!mapObject || !window.L) {\n"
            "                return;\n"
            "            }\n"
            "\n"
            "            if (mapObject.attributionControl) {\n"
            "                return;\n"
            "            }\n"
            "\n"
            "            var attribution = L.control.attribution({\n"
            "                position: 'bottomright'\n"
            "            }).addTo(mapObject);\n"
            "\n"
            "            attribution.setPrefix(\n"
            "                '<a href=\"https://leafletjs.com/\" '\n"
            "                'title=\"A JavaScript library for interactive maps\">'\n"
            "                + 'Leaflet'</n"
            "                + '</a>'\n"
            "            );\n"
            "\n"
            "            attribution.addAttribution(\n"
            "                '&copy; '\n"
            "                + '<a href=\"https://www.openstreetmap.org/copyright\">'\n"
            "                + 'OpenStreetMap contributors'\n"
            "                + '</a>'\n"
            "            );\n"
            "        }\n"
            "\n"
            "        if (document.readyState === 'loading') {\n"
            "            document.addEventListener(\n"
            "                'DOMContentLoaded',\n"
            "                setupAttribution\n"
            "            );\n"
            "        } else {\n"
            "            setupAttribution();\n"
            "        }\n"
            "    })();\n"
            "    </script>\n"
            "    '''\n"
            ")\n"
            "\n"
            "_attribution_{var1}.add_to({var1})\n"
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

    # --------------------------------------------------------
    # МАРКЕР
    # --------------------------------------------------------

    "Добавить маркер": {
        "template": (
            "_marker_{var2} = folium.Marker("
            "location=[{var3}, {var4}], "
            "tooltip={var5}, "
            "popup={var6}"
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

    # --------------------------------------------------------
    # МАРКЕР С ФОТО
    # --------------------------------------------------------

    "Добавить маркер с фото из файла": {
        "template": (
            "_img64_{var2} = image_to_base64({var6})\n"
            "\n"
            "_html_{var2} = (\n"
            "    '<div style=\"width:320px;\">'\n"
            "    '<h3 style=\"text-align:center;\">'\n"
            "    + str({var5}) +\n"
            "    '</h3>'\n"
            "    '<img src=\"data:image/jpeg;base64,'\n"
            "    + _img64_{var2} +\n"
            "    '\" width=\"300\" '\n"
            "    'style=\"display:block;margin:auto;'\n"
            "    'border-radius:10px;\">'\n"
            "    '<p style=\"text-align:center;font-size:15px;\">'\n"
            "    + str({var7}) +\n"
            "    '</p>'\n"
            "    '</div>'\n"
            ")\n"
            "\n"
            "_popup_{var2} = folium.Popup(\n"
            "    IFrame(_html_{var2}, width=340, height=380),\n"
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
            "from folium import IFrame"
        ],
        "helpers": [
            "image_to_base64"
        ]
    },

    "Добавить маркер с фото по URL": {
        "template": (
            "_html_{var2} = (\n"
            "    '<div style=\"width:320px;\">'\n"
            "    '<h3 style=\"text-align:center;\">'\n"
            "    + str({var5}) +\n"
            "    '</h3>'\n"
            "    '<img src=\"' + str({var6}) + '\" '\n"
            "    'width=\"300\" '\n"
            "    'style=\"display:block;margin:auto;'\n"
            "    'border-radius:10px;\">'\n"
            "    '<p style=\"text-align:center;font-size:15px;\">'\n"
            "    + str({var7}) +\n"
            "    '</p>'\n"
            "    '</div>'\n"
            ")\n"
            "\n"
            "_popup_{var2} = folium.Popup(\n"
            "    IFrame(_html_{var2}, width=340, height=380),\n"
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

    # --------------------------------------------------------
    # ПОИСК
    # --------------------------------------------------------

    "Добавить точку по поиску": {
        "template": (
            "try:\n"
            "    _search_{var2} = ox.geocode({var3})\n"
            "except Exception as _err_{var2}:\n"
            "    raise RuntimeError(\n"
            "        'Не удалось найти точку: '\n"
            "        + str(_err_{var2})\n"
            "    )\n"
            "\n"
            "if not _search_{var2}:\n"
            "    raise ValueError(\n"
            "        'Поиск не вернул координаты: '\n"
            "        + str({var3})\n"
            "    )\n"
            "\n"
            "_lat_{var2} = float(_search_{var2}[0])\n"
            "_lon_{var2} = float(_search_{var2}[1])\n"
            "\n"
            "_marker_{var2} = folium.Marker(\n"
            "    location=[_lat_{var2}, _lon_{var2}],\n"
            "    tooltip={var4},\n"
            "    popup={var5}\n"
            ")\n"
            "\n"
            "_marker_{var2}.add_to({var1})\n"
            "\n"
            "if {var6}:\n"
            "    _route_points.append((_lat_{var2}, _lon_{var2}))"
        ),
        "vars": [
            "Переменная карты",
            "Уникальное имя точки",
            "Поиск / адрес",
            "Название",
            "Текст popup",
            "Маршрутная точка (True/False)"
        ],
        "type": "folium",
        "imports": [
            "import folium",
            "import osmnx as ox"
        ]
    },

    "Добавить точку по поиску с фото URL": {
        "template": (
            "try:\n"
            "    _search_{var2} = ox.geocode({var3})\n"
            "except Exception as _err_{var2}:\n"
            "    raise RuntimeError(\n"
            "        'Не удалось найти точку: '\n"
            "        + str(_err_{var2})\n"
            "    )\n"
            "\n"
            "if not _search_{var2}:\n"
            "    raise ValueError(\n"
            "        'Поиск не вернул координаты: '\n"
            "        + str({var3})\n"
            "    )\n"
            "\n"
            "_lat_{var2} = float(_search_{var2}[0])\n"
            "_lon_{var2} = float(_search_{var2}[1])\n"
            "\n"
            "_html_{var2} = (\n"
            "    '<div style=\"width:320px;\">'\n"
            "    '<h3 style=\"text-align:center;\">'\n"
            "    + str({var4}) +\n"
            "    '</h3>'\n"
            "    '<img src=\"' + str({var5}) + '\" '\n"
            "    'width=\"300\" '\n"
            "    'style=\"display:block;margin:auto;'\n"
            "    'border-radius:10px;\">'\n"
            "    '<p style=\"text-align:center;font-size:15px;\">'\n"
            "    + str({var6}) +\n"
            "    '</p>'\n"
            "    '</div>'\n"
            ")\n"
            "\n"
            "_popup_{var2} = folium.Popup(\n"
            "    IFrame(_html_{var2}, width=340, height=380),\n"
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
            "    _route_points.append((_lat_{var2}, _lon_{var2}))"
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

    "Добавить точку по поиску с локальным фото": {
        "template": (
            "try:\n"
            "    _search_{var2} = ox.geocode({var3})\n"
            "except Exception as _err_{var2}:\n"
            "    raise RuntimeError(\n"
            "        'Не удалось найти точку: '\n"
            "        + str(_err_{var2})\n"
            "    )\n"
            "\n"
            "if not _search_{var2}:\n"
            "    raise ValueError(\n"
            "        'Поиск не вернул координаты: '\n"
            "        + str({var3})\n"
            "    )\n"
            "\n"
            "_lat_{var2} = float(_search_{var2}[0])\n"
            "_lon_{var2} = float(_search_{var2}[1])\n"
            "\n"
            "_img64_{var2} = image_to_base64({var5})\n"
            "\n"
            "_html_{var2} = (\n"
            "    '<div style=\"width:320px;\">'\n"
            "    '<h3 style=\"text-align:center;\">'\n"
            "    + str({var4}) +\n"
            "    '</h3>'\n"
            "    '<img src=\"data:image/jpeg;base64,'\n"
            "    + _img64_{var2} +\n"
            "    '\" width=\"300\" '\n"
            "    'style=\"display:block;margin:auto;'\n"
            "    'border-radius:10px;\">'\n"
            "    '<p style=\"text-align:center;font-size:15px;\">'\n"
            "    + str({var6}) +\n"
            "    '</p>'\n"
            "    '</div>'\n"
            ")\n"
            "\n"
            "_popup_{var2} = folium.Popup(\n"
            "    IFrame(_html_{var2}, width=340, height=380),\n"
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
            "    _route_points.append((_lat_{var2}, _lon_{var2}))"
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
            "import osmnx as ox",
            "from folium import IFrame"
        ],
        "helpers": [
            "image_to_base64"
        ]
    },

    # --------------------------------------------------------
    # ЛИНИЯ
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # ПОДПИСЬ
    # --------------------------------------------------------

    "Добавить подпись": {
        "template": (
            "folium.Marker(\n"
            "    location=[{var2}, {var3}],\n"
            "    icon=folium.DivIcon(\n"
            "        html=(\n"
            "            '<div style=\"color:'\n"
            "            + str({var5})\n"
            "            + ';font-size:'\n"
            "            + str({var6})\n"
            "            + 'px;font-weight:bold;'\n"
            "            + 'white-space:nowrap;\">'\n"
            "            + str({var4})\n"
            "            + '</div>'\n"
            "        )\n"
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

    # --------------------------------------------------------
    # ГРАНИЦЫ
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # МАРШРУТ
    # --------------------------------------------------------

    "Построить маршрут по маршрутным точкам": {
        "template": (
            "if len(_route_points) >= 2:\n"
            "    _coords = ';'.join(\n"
            "        f'{lon},{lat}'\n"
            "        for lat, lon in _route_points\n"
            "    )\n"
            "\n"
            "    _route_url = (\n"
            "        'https://router.project-osrm.org/route/v1/driving/'\n"
            "        + _coords\n"
            "        + '?overview=full&geometries=geojson'\n"
            "    )\n"
            "\n"
            "    _route_response = requests.get(\n"
            "        _route_url,\n"
            "        timeout=30\n"
            "    )\n"
            "    _route_response.raise_for_status()\n"
            "    _route_data = _route_response.json()\n"
            "\n"
            "    if _route_data.get('routes'):\n"
            "        _route = _route_data['routes'][0]\n"
            "        _distance_km = _route['distance'] / 1000\n"
            "        _duration_min = _route['duration'] / 60\n"
            "\n"
            "        _route_coords = [\n"
            "            [lat, lon]\n"
            "            for lon, lat\n"
            "            in _route['geometry']['coordinates']\n"
            "        ]\n"
            "\n"
            "        folium.PolyLine(\n"
            "            _route_coords,\n"
            "            color='blue',\n"
            "            weight=6,\n"
            "            opacity=0.8,\n"
            "            tooltip=(\n"
            "                f'Маршрут: {_distance_km:.2f} км | '\n"
            "                f'{_duration_min:.0f} мин.'\n"
            "            )\n"
            "        ).add_to({var1})\n"
            "\n"
            "        if _route_coords:\n"
            "            _middle = _route_coords[\n"
            "                len(_route_coords) // 2\n"
            "            ]\n"
            "\n"
            "            _info = (\n"
            "                '<div style=\"'\n"
            "                'background:white;'\n"
            "                'padding:10px 16px;'\n"
            "                'border:2px solid #333;'\n"
            "                'border-radius:10px;'\n"
            "                'font-size:15px;'\n"
            "                'font-weight:bold;'\n"
            "                'white-space:nowrap;'\n"
            "                'box-shadow:0 2px 8px rgba(0,0,0,.3);'\n"
            "                'text-align:center;'\n"
            "                'transform:translate(-50%,-50%);\">'\n"
            "                '🚗 Маршрут<br>'\n"
            "                '📏 ' + f'{_distance_km:.2f}' + ' км<br>'\n"
            "                '⏱ ' + f'{_duration_min:.0f}' + ' мин.'\n"
            "                '</div>'\n"
            "            )\n"
            "\n"
            "            folium.Marker(\n"
            "                location=_middle,\n"
            "                icon=folium.DivIcon(\n"
            "                    html=_info,\n"
            "                    icon_size=(180, 80),\n"
            "                    icon_anchor=(90, 40)\n"
            "                )\n"
            "            ).add_to({var1})\n"
            "    else:\n"
            "        print('OSRM не вернул маршрут.')\n"
            "else:\n"
            "    print(\n"
            "        'Для маршрута нужно минимум 2 маршрутные точки.'\n"
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
    },

    # --------------------------------------------------------
    # ЭКСПОРТ
    # --------------------------------------------------------

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
    }
}


# ============================================================
# HELPER-ФУНКЦИИ
# ============================================================

HELPERS = {

    "image_to_base64": (
        "def image_to_base64(path):\n"
        "    import base64\n"
        "    with open(path, 'rb') as img:\n"
        "        return base64.b64encode(img.read()).decode('ascii')\n"
    )
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
# РАБОТА СО СТРОКАМИ
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


def normalize_bool(value):
    value = value.strip().lower()

    if value in {
        "true",
        "1",
        "да",
        "yes",
        "y",
        "on"
    }:
        return "True"

    if value in {
        "false",
        "0",
        "нет",
        "no",
        "n",
        "off"
    }:
        return "False"

    return value


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


def replace_template_variables(template, values):
    result = template

    for i, value in enumerate(values, 1):
        result = result.replace(
            f"{{var{i}}}",
            value
        )

    unresolved = re.findall(
        r"\{var\d+\}",
        result
    )

    if unresolved:
        raise ValueError(
            "Незаменённые переменные: "
            + ", ".join(sorted(set(unresolved)))
        )

    return result


# ============================================================
# GUI КОНСТРУКТОРА
# ============================================================

def clear_input_area():
    for widget in input_widgets:
        try:
            widget.destroy()
        except Exception:
            pass

    input_widgets.clear()


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

    if path:
        entry.delete(0, "end")
        entry.insert(0, path)


def on_command_change(event=None):
    clear_input_area()

    selected = combo.get()

    if selected not in COMMANDS_DB:
        return

    command = COMMANDS_DB[selected]

    for index, variable_name in enumerate(
        command.get("vars", [])
    ):

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

        image_field = (
            "Путь к изображению" in variable_name
            and selected in {
                "Добавить маркер с фото из файла",
                "Добавить изображение из файла",
                "Добавить точку по поиску с локальным фото"
            }
        )

        if image_field:

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

            button = ctk.CTkButton(
                container,
                text="Обзор...",
                width=80,
                command=lambda e=entry: browse_image(e)
            )

            button.pack(
                side="left",
                padx=(5, 0)
            )

            input_widgets.extend([
                container,
                entry
            ])

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
# ДОБАВЛЕНИЕ КОМАНД
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
        w for w in input_widgets
        if isinstance(w, ctk.CTkEntry)
    ]

    if len(entries) != len(
        command.get("vars", [])
    ):
        messagebox.showerror(
            "Ошибка",
            "Количество полей не совпадает.",
            parent=constructor_window
        )
        return

    values = [
        e.get().strip()
        for e in entries
    ]

    if any(not v for v in values):
        messagebox.showwarning(
            "Внимание",
            "Заполните все поля.",
            parent=constructor_window
        )
        return

    # --------------------------------------------------------
    # GUI
    # --------------------------------------------------------

    if selected in {
        "Добавить кнопку",
        "Добавить метку",
        "Добавить чекбокс"
    }:
        values[1] = quote_value(values[1])

    if selected == "Добавить ComboBox":
        if not values[1].startswith("["):
            values[1] = repr([
                x.strip()
                for x in values[1].split(",")
                if x.strip()
            ])

    if selected in {
        "Добавить изображение по URL",
        "Добавить изображение из файла"
    }:
        values[1] = quote_value(values[1])

    # --------------------------------------------------------
    # МАРКЕР
    # --------------------------------------------------------

    if selected == "Добавить маркер":

        values[1] = safe_identifier(values[1])
        values[4] = quote_value(values[4])
        values[5] = quote_value(values[5])
        values[6] = normalize_bool(values[6])

    # --------------------------------------------------------
    # МАРКЕР С ЛОКАЛЬНЫМ ФОТО
    # --------------------------------------------------------

    if selected == "Добавить маркер с фото из файла":

        values[1] = safe_identifier(values[1])
        values[4] = quote_value(values[4])
        values[5] = quote_value(values[5])
        values[6] = quote_value(values[6])
        values[7] = normalize_bool(values[7])

    # --------------------------------------------------------
    # МАРКЕР С URL ФОТО
    # --------------------------------------------------------

    if selected == "Добавить маркер с фото по URL":

        values[1] = safe_identifier(values[1])
        values[4] = quote_value(values[4])
        values[5] = quote_value(values[5])
        values[6] = quote_value(values[6])
        values[7] = normalize_bool(values[7])

    # --------------------------------------------------------
    # ПОИСК
    # --------------------------------------------------------

    if selected == "Добавить точку по поиску":

        values[1] = safe_identifier(values[1])
        values[2] = quote_value(values[2])
        values[3] = quote_value(values[3])
        values[4] = quote_value(values[4])
        values[5] = normalize_bool(values[5])

    if selected == "Добавить точку по поиску с фото URL":

        values[1] = safe_identifier(values[1])
        values[2] = quote_value(values[2])
        values[3] = quote_value(values[3])
        values[4] = quote_value(values[4])
        values[5] = quote_value(values[5])
        values[6] = normalize_bool(values[6])

    if selected == "Добавить точку по поиску с локальным фото":

        values[1] = safe_identifier(values[1])
        values[2] = quote_value(values[2])
        values[3] = quote_value(values[3])
        values[4] = quote_value(values[4])
        values[5] = quote_value(values[5])
        values[6] = normalize_bool(values[6])

    # --------------------------------------------------------
    # ЛИНИЯ
    # --------------------------------------------------------

    if selected == "Добавить линию":
        values[2] = quote_value(values[2])

    # --------------------------------------------------------
    # ПОДПИСЬ
    # --------------------------------------------------------

    if selected == "Добавить подпись":
        values[3] = quote_value(values[3])
        values[4] = quote_value(values[4])

    # --------------------------------------------------------
    # ЭКСПОРТ
    # --------------------------------------------------------

    if selected == "Экспорт HTML":
        values[1] = quote_value(values[1])

    # --------------------------------------------------------
    # ГЕНЕРАЦИЯ
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

    used_imports.update(
        command.get("imports", [])
    )

    used_helpers.update(
        command.get("helpers", [])
    )


# ============================================================
# ОЧИСТКА КОДА
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
# ОТКРЫТИЕ PYTHON
# ============================================================

def open_py_file():

    path = filedialog.askopenfilename(
        parent=constructor_window,
        title="Открыть Python-файл",
        filetypes=[
            ("Python", "*.py"),
            ("Все файлы", "*.*")
        ]
    )

    if not path:
        return

    try:

        try:
            with open(
                path,
                "r",
                encoding="utf-8-sig"
            ) as f:
                code = f.read()

        except UnicodeDecodeError:

            with open(
                path,
                "r",
                encoding="cp1251"
            ) as f:
                code = f.read()

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

    used_imports.clear()
    used_helpers.clear()
    added_command_types.clear()

    checks = [

        (
            "folium",
            "import folium"
        ),

        (
            "requests",
            "import requests"
        ),

        (
            "osmnx",
            "import osmnx as ox"
        ),

        (
            "base64",
            "import base64"
        ),

        (
            "BytesIO(",
            "from io import BytesIO"
        ),

        (
            "Image.",
            "from PIL import Image"
        ),

        (
            "IFrame(",
            "from folium import IFrame"
        )
    ]

    for needle, imp in checks:

        if needle in code:
            used_imports.add(imp)

    if "image_to_base64(" in code:
        used_helpers.add(
            "image_to_base64"
        )

    if "ctk." in code:
        added_command_types.append(
            "gui"
        )

    if "folium" in code:
        added_command_types.append(
            "folium"
        )

    messagebox.showinfo(
        "Файл открыт",
        f"Python-файл загружен:\n\n{path}",
        parent=constructor_window
    )


# ============================================================
# УСТАНОВКА БИБЛИОТЕК
# ============================================================

def install_required_for_code():

    required = []

    if "folium" in used_imports:
        required.append(
            ("folium", "folium")
        )

    if any(
        "requests" in x
        for x in used_imports
    ):
        required.append(
            ("requests", "requests")
        )

    if any(
        "customtkinter" in x
        for x in used_imports
    ):
        required.append(
            ("customtkinter", "customtkinter")
        )

    if any(
        "PIL" in x
        for x in used_imports
    ):
        required.append(
            ("Pillow", "PIL")
        )

    if any(
        "osmnx" in x
        for x in used_imports
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

def generate_header(has_gui, has_folium):

    imports = set(used_imports)

    if has_gui:
        imports.add(
            "import customtkinter as ctk"
        )

    if has_folium:
        imports.add(
            "import folium"
        )

    order = [

        "import customtkinter as ctk",

        "import folium",

        "import requests",

        "import osmnx as ox",

        "import base64",

        "from io import BytesIO",

        "from PIL import Image",

        "from folium import IFrame"
    ]

    lines = [
        "# -*- coding: utf-8 -*-",
        ""
    ]

    for imp in order:

        if imp in imports:
            lines.append(imp)

    for imp in sorted(imports):

        if imp not in order:
            lines.append(imp)

    return "\n".join(lines) + "\n"


# ============================================================
# ПОЛНЫЙ СКРИПТ
# ============================================================

def generate_full_script(include_gui=True):

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
        (
            "gui" in added_command_types
            or "ctk." in user_code
        )
        and include_gui
    )

    has_folium = (
        "folium" in user_code
        or "folium" in added_command_types
    )

    # Автоматически определяем импорты.

    if "requests." in user_code:
        used_imports.add(
            "import requests"
        )

    if "ox." in user_code:
        used_imports.add(
            "import osmnx as ox"
        )

    if (
        "base64." in user_code
        or "image_to_base64(" in user_code
    ):
        used_imports.add(
            "import base64"
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

    parts = [
        generate_header(
            has_gui,
            has_folium
        )
    ]

    # --------------------------------------------------------
    # HELPERS
    # --------------------------------------------------------

    if used_helpers:

        parts.append(
            "# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ\n\n"
            + "\n".join(
                HELPERS[x]
                for x in used_helpers
                if x in HELPERS
            )
        )

    # --------------------------------------------------------
    # GUI
    # --------------------------------------------------------

    if has_gui:

        title = python_double_string(
            title_entry.get().strip()
            or "Моё приложение"
        )

        size = python_double_string(
            size_entry.get().strip()
            or "400x300"
        )

        parts.append(
            '# ГЛАВНОЕ ОКНО\n\n'
            'ctk.set_appearance_mode("Dark")\n'
            'ctk.set_default_color_theme("blue")\n'
            'root = ctk.CTk()\n'
            f'root.title("{title}")\n'
            f'root.geometry("{size}")\n'
            'frame = ctk.CTkFrame(root)\n'
            'frame.pack('
            'padx=20, pady=20, '
            'fill="both", expand=True'
            ')\n'
        )

    # --------------------------------------------------------
    # USER CODE
    # --------------------------------------------------------

    parts.append(
        "# КОД КОНСТРУКТОРА\n\n"
        + user_code
        + "\n"
    )

    # --------------------------------------------------------
    # MAINLOOP
    # --------------------------------------------------------

    if has_gui:
        parts.append(
            "root.mainloop()\n"
        )

    return "\n".join(parts)


# ============================================================
# СОХРАНЕНИЕ PYTHON
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
            str(e),
            parent=constructor_window
        )

        return

    path = filedialog.asksaveasfilename(
        parent=constructor_window,
        title="Сохранить Python-файл",
        defaultextension=".py",
        filetypes=[
            ("Python", "*.py"),
            ("Все файлы", "*.*")
        ]
    )

    if not path:
        return

    try:

        with open(
            path,
            "w",
            encoding="utf-8"
        ) as f:
            f.write(script)

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

    user_code = textbox.get(
        "1.0",
        "end"
    ).strip()

    if not user_code:

        messagebox.showwarning(
            "Внимание",
            "Сначала создайте карту.",
            parent=constructor_window
        )

        return

    maps = re.findall(
        r"^\s*([A-Za-z_]\w*)\s*=\s*folium\.Map\s*\(",
        user_code,
        re.MULTILINE
    )

    if not maps:

        messagebox.showerror(
            "Экспорт HTML",
            "Не найдена карта вида "
            "my_map = folium.Map(...).",
            parent=constructor_window
        )

        return

    map_name = maps[-1]

    path = filedialog.asksaveasfilename(
        parent=constructor_window,
        title="Экспортировать карту в HTML",
        defaultextension=".html",
        filetypes=[
            ("HTML", "*.html"),
            ("Все файлы", "*.*")
        ]
    )

    if not path:
        return

    old_text = textbox.get(
        "1.0",
        "end"
    )

    old_types = list(
        added_command_types
    )

    try:

        added_command_types[:] = [
            x
            for x in added_command_types
            if x != "gui"
        ]

        textbox.insert(
            "end",
            "\n"
            + map_name
            + ".save("
            + quote_value(path)
            + ")\n"
        )

        script = generate_full_script(
            include_gui=False
        )

        if script is None:
            return

        try:

            compile(
                script,
                "<export>",
                "exec"
            )

        except SyntaxError as e:

            messagebox.showerror(
                "Ошибка синтаксиса",
                str(e),
                parent=constructor_window
            )

            return

        if not install_required_for_code():
            return

        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".py",
            prefix="export_",
            delete=False,
            encoding="utf-8"
        ) as f:

            f.write(script)
            temp_path = f.name

        result = subprocess.run(
            [
                sys.executable,
                temp_path
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace"
        )

        try:
            Path(temp_path).unlink(
                missing_ok=True
            )
        except Exception:
            pass

        if result.returncode != 0:

            messagebox.showerror(
                "Ошибка экспорта",
                (
                    result.stderr
                    or result.stdout
                    or "Неизвестная ошибка"
                ).strip(),
                parent=constructor_window
            )

            return

        messagebox.showinfo(
            "Готово",
            "HTML сохранён:\n\n"
            + path,
            parent=constructor_window
        )

    finally:

        textbox.delete(
            "1.0",
            "end"
        )

        textbox.insert(
            "1.0",
            old_text
        )

        textbox.see("end")

        added_command_types[:] = old_types


# ============================================================
# ЗАПУСК КОДА
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
            str(e),
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
        ) as f:

            f.write(script)
            temp_path = f.name

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

                    Path(temp_path).unlink(
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
                Path(temp_path).unlink(
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
# ЗАГРУЗКА КОМАНД
# ============================================================

def load_commands_from_file():

    path = filedialog.askopenfilename(
        parent=constructor_window,
        title="Выберите TXT-файл",
        filetypes=[
            ("TXT", "*.txt"),
            ("Все файлы", "*.*")
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
        ) as f:

            for line in f:

                line = line.strip()

                if (
                    not line
                    or line.startswith("#")
                ):
                    continue

                parts = line.split(
                    "|",
                    3
                )

                if len(parts) < 3:
                    continue

                name, template, vars_text = parts[:3]

                command_type = (
                    parts[3].strip()
                    if len(parts) > 3
                    else "python"
                )

                COMMANDS_DB[
                    name.strip()
                ] = {
                    "template": template.strip(),
                    "vars": [
                        x.strip()
                        for x in vars_text.split(",")
                        if x.strip()
                    ],
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
# COMBOBOX
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
# ОКНО КОНСТРУКТОРА
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
    # НАСТРОЙКИ ОКНА
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

    combo.set(
        next(iter(COMMANDS_DB))
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
        font=("Consolas", 14)
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

    button_list = [

        (
            "Запустить код",
            run_code,
            140
        ),

        (
            "Экспорт HTML",
            export_html,
            140
        ),

        (
            "Открыть .py",
            open_py_file,
            130
        ),

        (
            "Сохранить .py",
            save_as_py,
            140
        ),

        (
            "Очистить код",
            clear_code,
            130
        ),

        (
            "Загрузить команды",
            load_commands_from_file,
            160
        )
    ]

    for text, command, width in button_list:

        ctk.CTkButton(
            buttons,
            text=text,
            command=command,
            width=width
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

    on_command_change()

    constructor_window.lift()
    constructor_window.focus_force()

    return constructor_window


# ============================================================
# MAIN
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