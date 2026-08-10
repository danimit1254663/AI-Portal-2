# commands/windows.py
import os
import subprocess
import webbrowser
import urllib.parse
from pathlib import Path
from datetime import datetime

from ui.hud import open_hud
from commands.app_launcher import open_app, close_app, list_apps, scan_apps
from commands.file_control import file_command
import core.state as state
import pyautogui
import psutil

try:
    import GPUtil
except ImportError:
    GPUtil = None

from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL


def get_volume():
    try:
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        return int(volume.GetMasterVolumeLevelScalar() * 100)
    except Exception:
        return 0


def set_volume(value):
    value = max(0, min(100, value))
    try:
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        volume.SetMasterVolumeLevelScalar(value / 100.0, None)
        return f"Громкость установлена на {value}%"
    except Exception as e:
        return f"Не удалось изменить громкость: {e}"


def ram_info():
    ram = psutil.virtual_memory()
    return (
        f"Оперативная память: всего {round(ram.total / 1024**3, 1)} ГБ, "
        f"используется {round(ram.used / 1024**3, 1)} ГБ"
    )


def cpu_info():
    return f"Процессор загружен на {psutil.cpu_percent(interval=1)}%"


def gpu_info():
    if GPUtil is None:
        return "Библиотека GPUtil не установлена"
    try:
        gpus = GPUtil.getGPUs()
        if gpus:
            return f"Видеокарта: {gpus[0].name}"
        return "Видеокарта не найдена"
    except Exception:
        return "Нет данных о видеокарте"


def open_program(text):
    programs = {
        "калькулятор": "calc.exe",
        "блокнот": "notepad.exe",
        "проводник": "explorer.exe",
        "диспетчер задач": "taskmgr.exe",
        "командная строка": "cmd.exe",
    }
    for name, program in programs.items():
        if name in text:
            subprocess.Popen(program, shell=True)
            return f"Открываю {name}"

    sites = {
        "youtube": "https://youtube.com",
        "гугл": "https://google.com",
        "почту": "https://mail.yandex.ru",
        "музыку": "https://music.yandex.ru",
    }
    for name, url in sites.items():
        if name in text:
            webbrowser.open(url)
            return f"Открываю {name}"
    return None


def search_web(text):
    if "ищи" not in text and "поиск" not in text:
        return None
    query = text
    for word in ["джарвис гугли", "джарвис поиск", "джарвис в интернете", "джарвис в браузере"]:
        query = query.replace(word, "")
    query = query.strip()
    if query:
        url = "https://www.google.com/search?q=" + urllib.parse.quote(query)
        webbrowser.open(url)
        return f"Ищу в Google: {query}"
    return None


def youtube_control(text):
    if any(x in text for x in ["youtube пауза", "пауза ютуб"]):
        pyautogui.press("space")
        return "Ставлю на паузу"
    if any(x in text for x in ["youtube продолжи", "продолжи ютуб"]):
        pyautogui.press("space")
        return "Продолжаю видео"
    if any(x in text for x in ["youtube полный экран", "полный экран ютуб"]):
        pyautogui.press("f")
        return "Полный экран"
    if "видео ютуб" in text or "видео youtube" in text:
        query = text.replace("ютуб", "").replace("youtube", "").strip()
        base_url = "https://www.youtube.com/results?search_query="
        if query:
            url = base_url + urllib.parse.quote(query)
            webbrowser.open(url)
            return f"Ищу на YouTube: {query}"
        else:
            webbrowser.open("https://youtube.com")
            return "Открываю YouTube"
    if "закрой вкладку" in text:
        pyautogui.hotkey("ctrl", "w")
        return "Закрываю вкладку"
    if "новая вкладка" in text:
        pyautogui.hotkey("ctrl", "t")
        return "Новая вкладка"
    return None


def screenshot():
    path = Path("temp/screen.png")
    path.parent.mkdir(parents=True, exist_ok=True)
    img = pyautogui.screenshot()
    img.save(path)
    return f"Скриншот сохранён: {path.absolute()}"


def windows_command(text):
    text = text.lower()

    # Интерфейс
    if any(x in text for x in ["покажи себя", "раскройся", "открой интерфейс"]):
        return open_hud()

    result = file_command(text)
    if result:
        return result

    # Приложения
    if "обнови список программ" in text:
        return scan_apps()
    result = list_apps(text)
    if result:
        return result
    result = close_app(text)
    if result:
        return result
    result = open_app(text)
    if result:
        return result

    # Простые действия
    actions = {
        "обнови страницу": ("f5", "Обновляю страницу"),
        "назад": (("alt", "left"), "Возвращаю назад"),
        "вперед": (("alt", "right"), "Перехожу вперёд"),
        "сверни окно": (("win", "down"), "Сворачиваю окно"),
        "разверни окно": (("win", "up"), "Разворачиваю окно"),
    }
    for key, (keys, msg) in actions.items():
        if key in text:
            if isinstance(keys, tuple):
                pyautogui.hotkey(*keys)
            else:
                pyautogui.press(keys)
            return msg

    # Время и дата
    if any(x in text for x in ["который час", "сколько времени"]):
        now = datetime.now().strftime("%H:%M:%S")
        if any(x in text for x in ["который час", "сколько времени"]):
            now = datetime.now().strftime("%H:%M:%S")
            return f"Сейчас {now}"
    if "какая дата" in text:
        import time
        return time.strftime("%d.%m.%Y")

    if "привет" in text:
        return "Здравствуйте!"

    # Громкость
    if "громче" in text:
        current = get_volume()
        new_vol = min(100, current + 10)
        return set_volume(new_vol)
    if "тише" in text:
        current = get_volume()
        new_vol = max(0, current - 10)
        return set_volume(new_vol)
    if "какая громкость" in text:
        return f"Текущая громкость: {get_volume()}%"

    # Системные данные
    if "оперативная память" in text:
        return ram_info()
    if "процессор" in text:
        return cpu_info()
    if "видеокарта" in text:
        return gpu_info()

    # YouTube и поиск
    result = youtube_control(text)
    if result:
        return result
    result = search_web(text)
    if result:
        return result
    result = open_program(text)
    if result:
        return result

    # Скриншот
    if "скриншот" in text:
        return screenshot()

    # Опасные команды — возвращаем специальный маркер, а не выполняем
    if "выключи компьютер" in text or "выключи комп" in text:
        return "__SHUTDOWN_REQUEST__"
    if "перезагрузи компьютер" in text or "перезагрузи комп" in text:
        return "__REBOOT_REQUEST__"

    return None
