import os
from ui.hud import open_hud
import subprocess
import webbrowser
import urllib.parse
from pathlib import Path
from commands.app_launcher import (
    open_app,
    close_app,
    list_apps,
    scan_apps
)
from ui.hud import show_time
import core.state as state
import pyautogui
import psutil
import GPUtil
from datetime import datetime
from pycaw.pycaw import (
    AudioUtilities,
    IAudioEndpointVolume
)

from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from commands.file_control import file_command


# ===============================
# VOLUME
# ===============================


def get_volume():

    try:

        devices = AudioUtilities.GetSpeakers()

        interface = devices.Activate(
            IAudioEndpointVolume._iid_,
            CLSCTX_ALL,
            None
        )


        volume = cast(
            interface,
            POINTER(IAudioEndpointVolume)
        )


        return int(
            volume.GetMasterVolumeLevelScalar()
            *100
        )

    except:

        return 0





def set_volume(value):

    value=max(
        0,
        min(
            100,
            value
        )
    )


    devices = AudioUtilities.GetSpeakers()

    interface = devices.Activate(
        IAudioEndpointVolume._iid_,
        CLSCTX_ALL,
        None
    )


    volume=cast(
        interface,
        POINTER(IAudioEndpointVolume)
    )


    volume.SetMasterVolumeLevelScalar(
        value/100,
        None
    )


    return f"Громкость {value} процентов"





# ===============================
# SYSTEM INFO
# ===============================


def ram_info():

    ram=psutil.virtual_memory()

    return (
        f"Оперативная память. "
        f"Всего {round(ram.total/1024**3,1)} гигабайт. "
        f"Используется {round(ram.used/1024**3,1)}"
    )




def cpu_info():

    return (
        "Процессор загружен на "
        +
        str(
            psutil.cpu_percent(1)
        )
        +
        " процентов"
    )





def gpu_info():

    try:

        gpu=GPUtil.getGPUs()


        if gpu:

            return (
                "Видеокарта "
                +
                gpu[0].name
            )


        return "Видеокарта не найдена"


    except:

        return "Нет данных"





# ===============================
# OPEN PROGRAMS
# ===============================


def open_program(text):

    programs={

        "калькулятор":
            "calc.exe",

        "блокнот":
            "notepad.exe",

        "проводник":
            "explorer.exe",

        "диспетчер задач":
            "taskmgr.exe",

        "командная строка":
            "cmd.exe",

        "ютуб":
        "start https://youtube.com",

    "почта":
    "start https://mail.yandex.ru",

    "музыка":
    "start https://music.yandex.ru",
    }


    for name,program in programs.items():


        if name in text:


            subprocess.Popen(
                program,
                shell=True
            )


            return (
                "Открываю "
                +
                name
            )



    sites={

        "ютуб":
            "https://youtube.com",

        "гугл":
            "https://google.com",

        "почта":
            "https://mail.yandex.ru",

        "музыка":
            "https://music.yandex.ru"

    }



    for name,url in sites.items():

        if name in text:


            webbrowser.open(url)


            return (
                "Открываю "
                +
                name
            )



    return None





# ===============================
# SEARCH
# ===============================


def search_web(text):


    if (
        "найди" not in text
        and
        "поиск" not in text
    ):

        return None



    query=text


    for word in [

        "найди",
        "поиск",
        "в интернете",
        "в браузере"

    ]:

        query=query.replace(
            word,
            ""
        )


    query=query.strip()


    if query:


        url=(

            "https://www.google.com/search?q="

            +

            urllib.parse.quote(query)

        )


        webbrowser.open(url)


        return (
            "Ищу "
            +
            query
        )


    return None





# ===============================
# YOUTUBE
# ===============================


def youtube_control(text):


    if "youtubeпауза" in text:

        pyautogui.press(
            "space"
        )

        return "Ставлю паузу"



    if "youtube продолжи" in text:

        pyautogui.press(
            "space"
        )

        return "Продолжаю видео"



    if "youtube полный экран" in text:

        pyautogui.press(
            "f"
        )

        return "Полный экран"

    if "видео ютуб" in text or "видео youtube" in text:

        query = text.replace(
            "ютуб",
            ""
        ).replace(
            "youtube",
            ""
        ).strip()

        if query:

            url = (
                    "https://www.youtube.com/results?search_query="
                    +
                    urllib.parse.quote(query)
            )

            webbrowser.open(url)

            return (
                    "Ищу на YouTube: "
                    +
                    query
            )


        else:

            webbrowser.open(
                "https://youtube.com"
            )

            return "Открываю YouTube"
    if "закрой вкладку" in text:

        pyautogui.hotkey(
            "ctrl",
            "w"
        )

        return "Закрываю вкладку"



    if "новая вкладка" in text:

        pyautogui.hotkey(
            "ctrl",
            "t"
        )

        return "Новая вкладка"



    return None





# ===============================
# SCREENSHOT
# ===============================


def screenshot():

    path=Path(
        "temp/screen.png"
    )


    img=pyautogui.screenshot()


    img.save(
        path
    )


    return "Скриншот сохранён"





# ===============================
# MAIN ROUTER
# ===============================


def windows_command(text):


    text=text.lower()
    if (
            "покажи себя" in text
            or
            "раскройся" in text
            or
            "открой интерфейс" in text
    ):
        return open_hud()


    result = file_command(text)

    if result:
        return result

    # PROGRAM CONTROL
    # ==========================

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
    # ==========================
    # SIMPLE ACTIONS
    # ==========================

    if "обнови страницу" in text:
        pyautogui.press(
            "f5"
        )

        return "Обновляю страницу"

    if "назад" in text:
        pyautogui.hotkey(

            "alt",

            "left"

        )

        return "Возвращаю назад"

    if "вперед" in text:
        pyautogui.hotkey(

            "alt",

            "right"

        )

        return "Перехожу вперед"

    if "сверни окно" in text:
        pyautogui.hotkey(

            "win",

            "down"

        )

        return "Сворачиваю окно"

    if "разверни окно" in text:
        pyautogui.hotkey(

            "win",

            "up"

        )

        return "Разворачиваю окно"

    if (
            "который час" in text
            or
            "сколько времени" in text
    ):

        now = datetime.now().strftime(
            "%H:%M:%S"
        )

        if state.hud_visible:

            show_time(now)


        else:

            show_time_popup(now)

        return "Сейчас " + now

    if "какая дата" in text:

        return time.strftime(
            "%d.%m.%Y"
        )


    if "привет" in text:

        return "Здравствуйте"

    if "громче" in text:

        return set_volume(
            get_volume()+10
        )



    if "тише" in text:

        return set_volume(
            get_volume()-10
        )



    if "какая громкость" in text:

        return (
            f"Громкость {get_volume()} процентов"
        )



    if "оперативная память" in text:

        return ram_info()



    if "процессор" in text:

        return cpu_info()



    if "видеокарта" in text:

        return gpu_info()



    result=youtube_control(text)

    if result:

        return result



    result=search_web(text)

    if result:

        return result



    result=open_program(text)

    if result:

        return result



    if "скриншот" in text:

        return screenshot()



    if "выключи компьютер" in text:


        os.system(
            "shutdown /s /t 5"
        )


        return "Выключаю компьютер"



    if "перезагрузи компьютер" in text:


        os.system(
            "shutdown /r /t 5"
        )


        return "Перезагружаю компьютер"

    result = open_app(text)

    if result:
        return result

    return None