# -*- coding: utf-8 -*-

import sys
import subprocess
import tempfile
import threading
import time
import re
import json
import base64
from pathlib import Path
from tkinter import filedialog, messagebox


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
        try:
            return install_package(package_name)
        except Exception:
            return False


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

    # --------------------------------------------------------
    # ИЗОБРАЖЕНИЕ CUSTOMTKINTER
    # --------------------------------------------------------

    "Добавить изображение CustomTkinter": {
        "template": (
            "_img_data = image_to_base64({var2})\n"
            "_img = ctk.CTkImage(\n"
            "    light_image=Image.open({var2}),\n"
            "    dark_image=Image.open({var2}),\n"
            "    size=({var3}, {var4})\n"
            ")\n"
            "{var1} = ctk.CTkLabel(\n"
            "    frame,\n"
            "    text=\"\",\n"
            "    image=_img\n"
            ")\n"
            "{var1}.pack(pady=5)"
        ),
        "vars": [
            "Имя переменной",
            "Путь к изображению",
            "Ширина",
            "Высота"
        ],
        "type": "gui",
        "imports": [
            "import customtkinter as ctk",
            "from PIL import Image"
        ],
        "helpers": [
            "image_to_base64"
        ]
    },

    # ========================================================
    # FOLIUM
    # ========================================================

    "Создать карту Folium": {
        "template": (
            "{var1} = folium.Map("
            "location=[{var2}, {var3}], "
            "zoom_start={var4}, "
            "control_scale=True"
            ")"
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
    # ОБЫЧНАЯ ТОЧКА
    # --------------------------------------------------------

    "Добавить маркер Folium": {
        "template": (
            "# Маршрутная точка: {var6}\n"
            "folium.Marker(\n"
            "    location=[{var2}, {var3}],\n"
            "    tooltip={var4},\n"
            "    popup={var5}\n"
            ").add_to({var1})\n"
            "\n"
            "if {var6}:\n"
            "    _route_points.append([{var2}, {var3}])"
        ),
        "vars": [
            "Переменная карты",
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
    # ТОЧКА С ФОТО ИЗ ФАЙЛА
    # --------------------------------------------------------

    "Добавить маркер с фото из файла": {
        "template": (
            "_img64 = image_to_base64({var5})\n"
            "\n"
            "_html = f'''"
            "<div style=\"width:320px;\">"
            "<h3 style=\"text-align:center;\">"
            "{var4}"
            "</h3>"
            "<img src=\"data:image/png;base64,"
            "{_img64}\" "
            "width=\"300\" "
            "style=\"display:block;"
            "margin:auto;"
            "border-radius:10px;\">"
            "<p style=\"text-align:center;"
            "font-size:15px;\">"
            "{var6}"
            "</p>"
            "</div>"
            "'''\n"
            "\n"
            "_popup = folium.Popup("
            "IFrame("
            "_html, "
            "width=340, "
            "height=350"
            "), "
            "max_width=340"
            ")\n"
            "\n"
            "folium.Marker("
            "location=[{var2}, {var3}], "
            "popup=_popup, "
            "tooltip={var4}"
            ").add_to({var1})\n"
            "\n"
            "if {var7}:\n"
            "    _route_points.append([{var2}, {var3}])"
        ),
        "vars": [
            "Переменная карты",
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

    # --------------------------------------------------------
    # ТОЧКА С ФОТО ПО URL
    # --------------------------------------------------------

    "Добавить маркер с фото по URL": {
        "template": (
            "_html = f'''"
            "<div style=\"width:320px;\">"
            "<h3 style=\"text-align:center;\">"
            "{var4}"
            "</h3>"
            "<img src=\"{var5}\" "
            "width=\"300\" "
            "style=\"display:block;"
            "margin:auto;"
            "border-radius:10px;\">"
            "<p style=\"text-align:center;"
            "font-size:15px;\">"
            "{var6}"
            "</p>"
            "</div>"
            "'''\n"
            "\n"
            "_popup = folium.Popup("
            "IFrame("
            "_html, "
            "width=340, "
            "height=350"
            "), "
            "max_width=340"
            ")\n"
            "\n"
            "folium.Marker("
            "location=[{var2}, {var3}], "
            "popup=_popup, "
            "tooltip={var4}"
            ").add_to({var1})\n"
            "\n"
            "if {var7}:\n"
            "    _route_points.append([{var2}, {var3}])"
        ),
        "vars": [
            "Переменная карты",
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
    # ЛИНИЯ
    # --------------------------------------------------------

    "Добавить линию Folium": {
        "template": (
            "folium.PolyLine("
            "{var2}, "
            "color={var3}, "
            "weight={var4}, "
            "opacity={var5}"
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
    # ПОДПИСЬ РАССТОЯНИЯ
    # --------------------------------------------------------

    "Добавить подпись расстояния": {
        "template": (
            "folium.Marker("
            "location=[{var2}, {var3}], "
            "icon=folium.DivIcon("
            "html=f'''"
            "<div style=\""
            "color:{var5};"
            "font-size:{var6}px;"
            "font-weight:bold;"
            "white-space:nowrap;"
            "\">"
            "{var4}"
            "</div>"
            "'''"
            ")"
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
    # ПОКАЗАТЬ КАРТУ ПО ГРАНИЦАМ
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
    # ЕДИНАЯ ФУНКЦИЯ ПОСТРОЕНИЯ МАРШРУТА
    # --------------------------------------------------------

    "Соединить маршрутные точки": {
        "template": (
            "if len(_route_points) >= 2:\n"
            "    _coords_string = ';'.join(\n"
            "        f\"{lon},{lat}\"\n"
            "        for lat, lon in _route_points\n"
            "    )\n"
            "\n"
            "    _url = (\n"
            "        \"https://router.project-osrm.org/\"\n"
            "        \"route/v1/driving/\"\n"
            "        + _coords_string\n"
            "        + \"?overview=full&geometries=geojson\"\n"
            "    )\n"
            "\n"
            "    _response = requests.get(\n"
            "        _url,\n"
            "        timeout=30\n"
            "    )\n"
            "\n"
            "    _response.raise_for_status()\n"
            "\n"
            "    _route_data = _response.json()\n"
            "\n"
            "    if _route_data.get('routes'):\n"
            "        _route = _route_data['routes'][0]\n"
            "\n"
            "        _route_distance_km = (\n"
            "            _route['distance'] / 1000\n"
            "        )\n"
            "\n"
            "        _route_coordinates = [\n"
            "            [lat, lon]\n"
            "            for lon, lat\n"
            "            in _route['geometry']['coordinates']\n"
            "        ]\n"
            "\n"
            "        folium.PolyLine(\n"
            "            _route_coordinates,\n"
            "            color={var1},\n"
            "            weight={var2},\n"
            "            opacity={var3},\n"
            "            tooltip=(\n"
            "                f'Маршрут: '\n"
            "                f'{_route_distance_km:.2f} км'\n"
            "            )\n"
            "        ).add_to({var4})\n"
            "\n"
            "        print(\n"
            "            f'Расстояние маршрута: '\n"
            "            f'{_route_distance_km:.2f} км'\n"
            "        )\n"
            "    else:\n"
            "        print('OSRM не вернул маршрут.')\n"
            "else:\n"
            "    print(\n"
            "        'Для построения маршрута нужно '\n"
            "        'минимум 2 маршрутные точки.'\n"
            "    )"
        ),
        "vars": [
            "Цвет маршрута",
            "Толщина маршрута",
            "Прозрачность маршрута",
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

    "Экспортировать карту HTML": {
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
# HELPER-КОД
# ============================================================

HELPERS = {

    "image_to_base64": '''
def image_to_base64(path):
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
# ЭКРАНИРОВАНИЕ PYTHON-СТРОК
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
# ВЫБОР ИЗОБРАЖЕНИЯ
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
            width=240,
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

        # ----------------------------------------------------
        # Изображение из файла
        # ----------------------------------------------------

        is_image_file = (
            (
                selected == "Добавить маркер с фото из файла"
                and "Путь" in variable_name
            )
            or
            (
                selected == "Добавить изображение CustomTkinter"
                and "Путь" in variable_name
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

            entry.pack(
                side="left"
            )

            browse_button = ctk.CTkButton(
                container,
                text="Обзор",
                width=70,
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
                width=300
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
# ЗАМЕНА ШАБЛОННЫХ ПЕРЕМЕННЫХ
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
            "В шаблоне остались незаменённые "
            "переменные:\n\n"
            + "\n".join(sorted(set(unresolved)))
        )

    return result


# ============================================================
# ДОБАВЛЕНИЕ КОМАНДЫ
# ============================================================

def add_command():

    selected = combo.get()

    if selected not in COMMANDS_DB:

        messagebox.showwarning(
            "Внимание",
            "Выберите команду!",
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
                "Заполните все поля!",
                parent=constructor_window
            )

            return

        values.append(value)

    # ========================================================
    # GUI
    # ========================================================

    if selected in (
        "Добавить кнопку",
        "Добавить метку",
        "Добавить чекбокс"
    ):

        text_index = 1

        if not values[text_index].startswith(
            ("'", '"')
        ):

            values[text_index] = (
                "'"
                + python_string(values[text_index])
                + "'"
            )

    if selected == "Добавить ComboBox":

        raw = values[1]

        if not raw.startswith("["):

            items = [
                x.strip()
                for x in raw.split(",")
                if x.strip()
            ]

            values[1] = repr(items)

    # ========================================================
    # FOLIUM
    # ========================================================

    if selected == "Добавить маркер Folium":

        for index in (3, 4):

            if not values[index].startswith(
                ("'", '"')
            ):

                values[index] = (
                    "'"
                    + python_string(values[index])
                    + "'"
                )

        # True / False
        values[5] = values[5].strip()

        if values[5].lower() in (
            "да",
            "yes",
            "true",
            "1"
        ):

            values[5] = "True"

        elif values[5].lower() in (
            "нет",
            "no",
            "false",
            "0"
        ):

            values[5] = "False"

    if selected == "Добавить маркер с фото из файла":

        for index in (3, 4, 5):

            if not values[index].startswith(
                ("'", '"')
            ):

                values[index] = (
                    "'"
                    + python_string(values[index])
                    + "'"
                )

        if values[6].lower() in (
            "да",
            "yes",
            "true",
            "1"
        ):

            values[6] = "True"

        elif values[6].lower() in (
            "нет",
            "no",
            "false",
            "0"
        ):

            values[6] = "False"

    if selected == "Добавить маркер с фото по URL":

        for index in (3, 4, 5):

            if not values[index].startswith(
                ("'", '"')
            ):

                values[index] = (
                    "'"
                    + python_string(values[index])
                    + "'"
                )

        if values[6].lower() in (
            "да",
            "yes",
            "true",
            "1"
        ):

            values[6] = "True"

        elif values[6].lower() in (
            "нет",
            "no",
            "false",
            "0"
        ):

            values[6] = "False"

    # ========================================================
    # CustomTkinter IMAGE
    # ========================================================

    if selected == "Добавить изображение CustomTkinter":

        if not values[1].startswith(
            ("'", '"')
        ):

            values[1] = (
                "'"
                + python_string(values[1])
                + "'"
            )

    # ========================================================
    # ГЕНЕРАЦИЯ
    # ========================================================

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
# ОЧИСТКА
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
# ПРОВЕРКА БИБЛИОТЕК
# ============================================================

def install_required_for_code():

    required = []

    if "folium" in used_imports:
        required.append(("folium", "folium"))

    if any(
        "requests" in imp
        for imp in used_imports
    ):
        required.append(("requests", "requests"))

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
            ("pillow", "PIL")
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

    lines = [
        "# -*- coding: utf-8 -*-",
        ""
    ]

    preferred_order = [
        "import customtkinter as ctk",
        "import folium",
        "import requests",
        "import base64",
        "from folium import IFrame",
        "from PIL import Image"
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
# FULL SCRIPT
# ============================================================

def generate_full_script(html_output=None):

    user_code = textbox.get(
        "1.0",
        "end"
    ).strip()

    if not user_code:

        messagebox.showwarning(
            "Внимание",
            "Сначала добавьте код!",
            parent=constructor_window
        )

        return None

    has_gui = (
        "gui" in added_command_types
    )

    has_folium = (
        "folium" in added_command_types
    )

    # --------------------------------------------------------
    # Автоматически определяем Folium
    # --------------------------------------------------------

    if (
        "folium." in user_code
        or "folium " in user_code
    ):

        has_folium = True

        used_imports.add(
            "import folium"
        )

    if "requests." in user_code:

        used_imports.add(
            "import requests"
        )

    if "base64." in user_code:

        used_imports.add(
            "import base64"
        )

    if "IFrame(" in user_code:

        used_imports.add(
            "from folium import IFrame"
        )

    if "Image.open" in user_code:

        used_imports.add(
            "from PIL import Image"
        )

    # --------------------------------------------------------
    # Маршрутные точки
    # --------------------------------------------------------

    route_header = ""

    if has_folium:

        route_header = '''
# ============================================================
# МАРШРУТНЫЕ ТОЧКИ
# ============================================================

_route_points = []
'''

    # --------------------------------------------------------
    # Helpers
    # --------------------------------------------------------

    helper_text = ""

    for helper_name in used_helpers:

        if helper_name in HELPERS:

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
    # Route points
    # --------------------------------------------------------

    if route_header:

        parts.append(
            route_header
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
    # User code
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
    # HTML EXPORT
    # --------------------------------------------------------

    if html_output:

        safe_html = python_double_string(
            html_output
        )

        parts.append(
            f'''
# ============================================================
# ЭКСПОРТ HTML
# ============================================================

if "folium" in globals():

    try:

        _html_output = r"{safe_html}"

        _map_candidates = [
            value
            for name, value in globals().items()
            if isinstance(value, folium.Map)
        ]

        if _map_candidates:

            _map_candidates[-1].save(
                _html_output
            )

            print(
                "HTML сохранён:",
                _html_output
            )

        else:

            print(
                "Не найдена переменная folium.Map."
            )

    except Exception as _html_error:

        print(
            "Ошибка экспорта HTML:",
            _html_error
        )
'''
        )

    # --------------------------------------------------------
    # GUI mainloop
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
            "Ошибка",
            str(e),
            parent=constructor_window
        )


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

                    Path(temp_path).unlink(
                        missing_ok=True
                    )

                    if not Path(temp_path).exists():
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
# ЭКСПОРТ HTML
# ============================================================

def export_html():

    if "folium" not in added_command_types:

        messagebox.showwarning(
            "Folium не используется",
            "Добавьте хотя бы одну команду Folium.",
            parent=constructor_window
        )

        return

    output_path = filedialog.asksaveasfilename(
        parent=constructor_window,
        title="Экспортировать карту в HTML",
        defaultextension=".html",
        filetypes=[
            ("HTML", "*.html"),
            ("Все файлы", "*.*")
        ]
    )

    if not output_path:
        return

    if not install_required_for_code():
        return

    script = generate_full_script(
        html_output=output_path
    )

    if script is None:
        return

    try:

        compile(
            script,
            "<html_export>",
            "exec"
        )

    except SyntaxError as e:

        messagebox.showerror(
            "Ошибка синтаксиса",
            str(e),
            parent=constructor_window
        )

        return

    temp_path = None

    try:

        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".py",
            prefix="folium_export_",
            delete=False,
            encoding="utf-8"
        ) as temp:

            temp.write(script)
            temp_path = temp.name

        def export_worker():

            try:

                process = subprocess.run(
                    [
                        sys.executable,
                        temp_path
                    ],
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    errors="replace"
                )

                if process.returncode == 0:

                    constructor_window.after(
                        0,
                        lambda: messagebox.showinfo(
                            "HTML экспортирован",
                            "Карта сохранена:\n\n"
                            + output_path,
                            parent=constructor_window
                        )
                    )

                else:

                    error_text = (
                        process.stderr
                        or process.stdout
                        or "Неизвестная ошибка"
                    )

                    constructor_window.after(
                        0,
                        lambda: messagebox.showerror(
                            "Ошибка экспорта",
                            error_text,
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

                    for _ in range(10):

                        try:

                            Path(temp_path).unlink(
                                missing_ok=True
                            )

                            break

                        except Exception:

                            time.sleep(0.3)

        threading.Thread(
            target=export_worker,
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
            "Ошибка",
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
        ) as file:

            for line in file:

                line = line.strip()

                if not line:
                    continue

                if line.startswith("#"):
                    continue

                parts = line.split("|", 3)

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
# КОНСТРУКТОР
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
        "900x850"
    )

    constructor_window.minsize(
        750,
        650
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
        10,
        weight=1
    )

    frame.columnconfigure(
        1,
        weight=1
    )

    # ========================================================
    # ЗАГОЛОВОК
    # ========================================================

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

    # ========================================================
    # НАСТРОЙКИ
    # ========================================================

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

    # ========================================================
    # КОМАНДА
    # ========================================================

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
        width=350,
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
            next(iter(COMMANDS_DB))
        )

    # ========================================================
    # ДОБАВИТЬ
    # ========================================================

    ctk.CTkButton(
        frame,
        text="Добавить код",
        command=add_command,
        width=150
    ).grid(
        row=3,
        column=1,
        sticky="w",
        padx=10,
        pady=10
    )

    # ========================================================
    # РЕДАКТОР
    # ========================================================

    textbox = ctk.CTkTextbox(
        frame,
        wrap="none",
        font=(
            "Consolas",
            14
        )
    )

    textbox.grid(
        row=10,
        column=0,
        columnspan=2,
        sticky="nsew",
        padx=10,
        pady=10
    )

    # ========================================================
    # КНОПКИ
    # ========================================================

    buttons = ctk.CTkFrame(
        frame,
        fg_color="transparent"
    )

    buttons.grid(
        row=11,
        column=0,
        columnspan=2,
        pady=10
    )

    ctk.CTkButton(
        buttons,
        text="Открыть код",
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
        text="Сохранить .py",
        command=save_as_py,
        width=140
    ).pack(
        side="left",
        padx=4
    )

    ctk.CTkButton(
        buttons,
        text="Очистить",
        command=clear_code,
        width=120
    ).pack(
        side="left",
        padx=4
    )

    ctk.CTkButton(
        buttons,
        text="Загрузить TXT",
        command=load_commands_from_file,
        width=130
    ).pack(
        side="left",
        padx=4
    )

    # ========================================================
    # ЗАКРЫТИЕ
    # ========================================================

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

    # ========================================================
    # ИНИЦИАЛИЗАЦИЯ
    # ========================================================

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
        "450x300"
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