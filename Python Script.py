# ==========================================================
# AI VOICE ASSISTANT PRO v2
# PART 1/6
# CORE ENGINE
# ==========================================================
import  urllib
import os
import sys
import json
import time
import uuid
import queue
import shutil
import logging
import threading
import platform
import subprocess
import tempfile
from pathlib import Path
import win32gui
import win32con
import requests
import urllib3
import psutil
from tensorflow.python._pywrap_tfe import TFE_Executor

# ==========================================================
# LOGGING
# ==========================================================

logging.basicConfig(
    filename="assistant.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

urllib3.disable_warnings(
    urllib3.exceptions.InsecureRequestWarning
)


# ==========================================================
# PATHS
# ==========================================================

BASE_DIR = Path.cwd()

MODELS_DIR = BASE_DIR / "models"
CACHE_DIR = BASE_DIR / "cache"
TEMP_DIR = BASE_DIR / "temp"

CONFIG_FILE = BASE_DIR / "config.json"
MEMORY_FILE = BASE_DIR / "memory.json"


for folder in [
    MODELS_DIR,
    CACHE_DIR,
    TEMP_DIR
]:
    folder.mkdir(
        exist_ok=True
    )


# ==========================================================
# CONFIG
# =========================================================
DEFAULT_CONFIG = {

    "voice": "kseniya",

    "activation": [
        "джарвис",
        "ассистент",

    ],

    "language": "ru"

}


config = {}


def save_config():

    try:

        with open(
            CONFIG_FILE,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                config,
                f,
                indent=4,
                ensure_ascii=False
            )


    except Exception as e:

        logging.error(
            f"CONFIG SAVE ERROR {e}"
        )



def load_config():

    global config


    if not CONFIG_FILE.exists():

        config = DEFAULT_CONFIG.copy()

        save_config()

        return



    try:

        with open(
            CONFIG_FILE,
            "r",
            encoding="utf-8"
        ) as f:

            config=json.load(f)



    except:

        config=DEFAULT_CONFIG.copy()

        save_config()



load_config()



CURRENT_VOICE = config.get(
    "voice",
    "kseniya"
)



RU_VOICES = [

    "aidar",
    "baya",
    "kseniya",
    "eugene"

]



# ==========================================================
# MEMORY
# ==========================================================


memory={}



def load_memory():

    global memory


    if not MEMORY_FILE.exists():

        memory={}

        return



    try:

        with open(
            MEMORY_FILE,
            "r",
            encoding="utf-8"
        ) as f:

            memory=json.load(f)


    except:

        memory={}




def save_memory():

    try:

        with open(
            MEMORY_FILE,
            "w",
            encoding="utf-8"
        ) as f:


            json.dump(
                memory,
                f,
                indent=4,
                ensure_ascii=False
            )


    except Exception as e:

        logging.error(
            f"MEMORY ERROR {e}"
        )



load_memory()



def remember(text):

    """
    Простая память пользователя
    """

    text=text.lower()



    if "меня зовут" in text:

        name=text.split(
            "меня зовут",
            1
        )[1].strip()


        if name:

            memory["name"]=name

            save_memory()

            return "Запомнил ваше имя"



    if "запомни" in text:

        fact=text.split(
            "запомни",
            1
        )[1].strip()


        if fact:

            memory.setdefault(
                "facts",
                []
            )


            memory["facts"].append(
                fact
            )


            save_memory()

            return "Запомнил"



    return None





def memory_context():

    result=[]


    if "name" in memory:

        result.append(
            "Имя пользователя: "
            +
            memory["name"]
        )


    for fact in memory.get(
        "facts",
        []
    ):

        result.append(
            "Факт: "
            +
            fact
        )


    return "\n".join(result)



# ==========================================================
# GLOBAL QUEUES
# ==========================================================


audio_queue = queue.Queue()

tts_queue = queue.Queue()



assistant_running=True



# ==========================================================
# SYSTEM CHECK
# ==========================================================


def check_environment():

    print(
        "Проверка системы..."
    )


    print(
        "Python:",
        sys.version.split()[0]
    )


    print(
        "Windows:",
        platform.platform()
    )


    print(
        "CPU:",
        platform.processor()
    )



    ram=psutil.virtual_memory()


    print(
        "RAM:",
        round(
            ram.total/1024**3,
            1
        ),
        "GB"
    )


    logging.info(
        "SYSTEM CHECK OK"
    )





def clean_temp():

    if not TEMP_DIR.exists():

        return



    for file in TEMP_DIR.iterdir():

        try:

            if file.is_file():

                file.unlink()


        except:

            pass





def first_start():

    print(
        "AI Voice Assistant PRO v2"
    )

    print(
        "Инициализация..."
    )


    logging.info(
        "FIRST START"
    )





# ==========================================================
# SAFE PROCESS START
# ==========================================================


def start_program(path):

    try:

        subprocess.Popen(
            path,
            shell=True
        )

        return True


    except Exception as e:

        logging.error(
            str(e)
        )

        return False





# ==========================================================
# PLACEHOLDERS
# ==========================================================

# следующие части добавят:
#
# PART 2:
# VOSK + числа + английские слова
#
# PART 3:
# SILERO TTS
#
# PART 4:
# GIGACHAT PRO
#
# PART 5:
# WINDOWS COMMANDS
#
# PART 6:
# MAIN LOOP


print(
    "CORE LOADED"
)
# ==========================================================
# AI VOICE ASSISTANT PRO v2
# PART 2/6
# VOSK PRO RECOGNITION
# ==========================================================

import zipfile
import sounddevice as sd
import soundfile as sf

from vosk import Model, KaldiRecognizer



# ==========================================================
# VOSK SETTINGS
# ==========================================================


VOSK_MODEL_URL = (
    "https://alphacephei.com/vosk/models/"
    "vosk-model-small-ru-0.22.zip"
)


vosk_model=None



# ==========================================================
# DOWNLOAD MODEL
# ==========================================================


def download_vosk():

    archive=MODELS_DIR / "vosk.zip"


    if archive.exists():

        return archive



    print(
        "Скачиваю модель распознавания..."
    )


    try:

        r=requests.get(
            VOSK_MODEL_URL,
            stream=True,
            timeout=120
        )


        with open(
            archive,
            "wb"
        ) as f:


            for chunk in r.iter_content(
                1024*1024
            ):

                if chunk:

                    f.write(chunk)



        return archive



    except Exception as e:

        logging.error(
            f"VOSK DOWNLOAD {e}"
        )

        return None





# ==========================================================
# FIND MODEL
# ==========================================================


def find_vosk():

    for root,dirs,files in os.walk(
        MODELS_DIR
    ):

        if (
            "am" in dirs
            and
            "conf" in dirs
        ):

            return root


    return None





# ==========================================================
# INSTALL
# ==========================================================


def install_vosk():


    model=find_vosk()


    if model:

        return model



    archive=download_vosk()


    if not archive:

        return None



    print(
        "Распаковка Vosk..."
    )


    with zipfile.ZipFile(
        archive,
        "r"
    ) as z:

        z.extractall(
            MODELS_DIR
        )


    archive.unlink()



    return find_vosk()





# ==========================================================
# LOAD
# ==========================================================


def load_vosk():


    global vosk_model


    if vosk_model:

        return True



    path=install_vosk()


    if not path:

        return False



    print(
        "Загрузка Vosk..."
    )


    vosk_model=Model(
        path
    )


    print(
        "Vosk готов"
    )


    return True





# ==========================================================
# NUMBER ENGINE
# ==========================================================


NUMBERS={

    "ноль":0,

    "один":1,
    "одна":1,

    "два":2,
    "две":2,

    "три":3,
    "четыре":4,

    "пять":5,
    "шесть":6,
    "семь":7,
    "восемь":8,
    "девять":9,

    "десять":10,

    "двадцать":20,
    "тридцать":30,
    "сорок":40,

    "пятьдесят":50,
    "шестьдесят":60,
    "семьдесят":70,
    "восемьдесят":80,
    "девяносто":90

}



NUMBER_FIX={

    "пять десят":
        "пятьдесят",

    "шесть десят":
        "шестьдесят",

    "семь десят":
        "семьдесят",

    "восемь десят":
        "восемьдесят",

    "пять десять":
        "пятьдесят",

    "шесть десять":
        "шестьдесят"

}




def fix_numbers(text):


    for a,b in NUMBER_FIX.items():

        text=text.replace(
            a,
            b
        )


    return text

def words_to_number(text):

    words = text.split()

    result = None

    for word in words:
        if word in NUMBERS:
            result = NUMBERS[word]

    return result



# ==========================================================
# ENGLISH FIX
# ==========================================================


EN_FIX={

    "хром":
        "chrome",

    "гугл":
        "google",

    "ютуб":
        "youtube",

    "дискорд":
        "discord",

    "виндовс":
        "windows",

    "браузер":
        "browser"

}




def fix_english(text):


    for a,b in EN_FIX.items():

        text=text.replace(
            a,
            b
        )


    return text





# ==========================================================
# CLEAN RESULT
# ==========================================================


def clean_voice(text):


    text=text.lower().strip()



    garbage=[

        "а",
        "э",
        "эм",
        "ну"

    ]


    for g in garbage:

        text=text.replace(
            " "+g+" ",
            " "
        )



    text=fix_numbers(
        text
    )


    text=fix_english(
        text
    )



    return " ".join(
        text.split()
    )





# ==========================================================
# LISTEN
# ==========================================================


def listen():


    global vosk_model



    if not vosk_model:

        if not load_vosk():

            return ""




    print(
        "🎤 Слушаю..."
    )



    recognizer=KaldiRecognizer(

        vosk_model,

        16000

    )


    recognizer.SetWords(True)



    def callback(
        indata,
        frames,
        time,
        status
    ):


        audio_queue.put(
            bytes(indata)
        )





    try:


        with sd.RawInputStream(

            samplerate=16000,

            blocksize=4000,

            dtype="int16",

            channels=1,

            callback=callback

        ):


            while assistant_running:


                data=audio_queue.get()



                if recognizer.AcceptWaveform(data):


                    result=json.loads(

                        recognizer.Result()

                    )


                    text=result.get(
                        "text",
                        ""
                    )


                    text=clean_voice(
                        text
                    )


                    if len(text)>1:


                        print(
                            "USER:",
                            text
                        )


                        return text



    except Exception as e:


        logging.error(
            f"LISTEN ERROR {e}"
        )


    return ""
# ==========================================================
# AI VOICE ASSISTANT PRO v2
# PART 3/6
# SILERO TTS PRO
# ==========================================================

import torch
import pygame
import uuid
import re
import numpy as np

from num2words import num2words



# ==========================================================
# AUDIO INIT
# ==========================================================


pygame.init()


if pygame.mixer.get_init() is None:

    pygame.mixer.init()



SAMPLE_RATE = 48000



tts_model_ru=None
tts_model_en=None

tts_ready=False



# ==========================================================
# LOAD SILERO
# ==========================================================


def load_tts():


    global tts_model_ru
    global tts_model_en
    global tts_ready



    if tts_ready:

        return True



    try:


        print(
            "Загрузка русского голоса..."
        )



        os.environ["TORCH_HOME"]=str(
            CACHE_DIR
        )



        tts_model_ru,_=torch.hub.load(


            "snakers4/silero-models",


            "silero_tts",


            language="ru",


            speaker="v5_ru",


            trust_repo=True


        )



        print(
            "RU готов"
        )




        print(
            "Загрузка английского голоса..."
        )



        tts_model_en,_=torch.hub.load(


            "snakers4/silero-models",


            "silero_tts",


            language="en",


            speaker="v3_en",


            trust_repo=True


        )



        print(
            "EN готов"
        )



        tts_ready=True


        return True



    except Exception as e:


        logging.error(
            f"TTS LOAD ERROR {e}"
        )


        return False





# ==========================================================
# LANGUAGE DETECTOR
# ==========================================================


def detect_language(text):


    text=text.lower()



    english=0
    russian=0



    for c in text:


        if "а" <= c <= "я" or c=="ё":

            russian+=1


        elif "a" <= c <= "z":

            english+=1



    if english>russian:

        return "en"


    return "ru"





# ==========================================================
# SPLIT MIXED TEXT
# ==========================================================


def split_voice_text(text):


    words=text.split()


    if not words:

        return []



    result=[]

    current=[]


    lang=detect_language(
        words[0]
    )



    for word in words:


        word_lang=detect_language(
            word
        )


        if word_lang!=lang:


            result.append(

                (
                    lang,
                    " ".join(current)
                )

            )


            current=[word]

            lang=word_lang


        else:

            current.append(word)



    if current:


        result.append(

            (
                lang,
                " ".join(current)
            )

        )


    return result





# ==========================================================
# NUMBER TO WORD
# ==========================================================


def prepare_numbers(text):


    def repl(match):

        number=int(
            match.group()
        )


        try:

            return num2words(
                number,
                lang="ru"
            )

        except:

            return match.group()



    return re.sub(

        r"\d+",

        repl,

        text

    )





# ==========================================================
# PLAY AUDIO
# ==========================================================


def play_audio(audio):


    filename=TEMP_DIR / (

        str(uuid.uuid4())

        +

        ".wav"

    )



    sf.write(

        filename,

        audio.numpy(),

        SAMPLE_RATE

    )



    pygame.mixer.music.stop()



    pygame.mixer.music.load(

        str(filename)

    )


    pygame.mixer.music.play()



    while pygame.mixer.music.get_busy():

        pygame.time.wait(
            50
        )



    pygame.mixer.music.stop()


    pygame.mixer.music.unload()



    try:

        filename.unlink()

    except:

        pass





# ==========================================================
# SPEAK PART
# ==========================================================


def speak_part(text,lang):


    if lang=="ru":


        model=tts_model_ru


        speaker=config.get(
            "voice",
            "kseniya"
        )


        if speaker not in RU_VOICES:

            speaker="kseniya"



        text=prepare_numbers(
            text
        )



    else:


        model=tts_model_en


        speaker="en_0"



    audio=model.apply_tts(


        text=text,


        speaker=speaker,


        sample_rate=SAMPLE_RATE,


        put_accent=True,


        put_yo=True


    )



    play_audio(
        audio
    )





# ==========================================================
# PUBLIC SPEAK
# ==========================================================


def speak(text):


    if not text:

        return



    if not load_tts():

        return



    parts=split_voice_text(
        text
    )



    for lang,part in parts:


        speak_part(

            part,

            lang

        )





print(
    "TTS SYSTEM READY"
)
# ==========================================================
# AI VOICE ASSISTANT PRO v2
# PART 4/6
# GIGACHAT PRO + MEMORY ENGINE
# ==========================================================

import base64



# ==========================================================
# ENV
# ==========================================================

from dotenv import load_dotenv


load_dotenv()



GIGACHAT_CLIENT_ID=os.getenv(
    "GIGACHAT_CLIENT_ID"
)


GIGACHAT_CLIENT_SECRET=os.getenv(
    "GIGACHAT_CLIENT_SECRET"
)


GIGACHAT_SCOPE=os.getenv(

    "GIGACHAT_SCOPE",

    "GIGACHAT_API_PERS"

)



TOKEN_URL=(

    "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"

)


CHAT_URL=(

    "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"

)



http=requests.Session()



# ==========================================================
# GIGACHAT CLASS
# ==========================================================


class GigaChat:


    def __init__(self):

        self.token=None

        self.expire=0





    def get_token(self):


        try:


            auth=base64.b64encode(

                (

                GIGACHAT_CLIENT_ID

                +

                ":"

                +

                GIGACHAT_CLIENT_SECRET

                ).encode()

            ).decode()



            headers={


                "Authorization":

                    "Basic "+auth,


                "RqUID":

                    str(uuid.uuid4()),


                "Content-Type":

                    "application/x-www-form-urlencoded"


            }



            data={

                "scope":

                    GIGACHAT_SCOPE

            }



            r=http.post(


                TOKEN_URL,


                headers=headers,


                data=data,


                verify=False,


                timeout=30


            )



            r.raise_for_status()



            result=r.json()



            self.token=result.get(

                "access_token"

            )



            self.expire=time.time()+1700



            logging.info(

                "GigaChat token OK"

            )



        except Exception as e:


            logging.error(

                "TOKEN ERROR "+str(e)

            )



            self.token=None





    def check(self):


        if (

            self.token is None

            or

            time.time()>self.expire

        ):


            self.get_token()





gigachat=GigaChat()





# ==========================================================
# AI MEMORY
# ==========================================================


conversation=[


{

"role":"system",

"content":

"""
Ты голосовой помощник Windows.

Правила:

- Отвечай только на русском.
- Ответ короткий.
- Не используй длинные списки.
- Ответ должен хорошо звучать голосом.
- Помогай с компьютером.
- Не говори что ты ИИ.
"""

}

]



MAX_HISTORY=15





# ==========================================================
# AI REQUEST
# ==========================================================


def ask_ai(text):


    global conversation



    # сохранить факты

    memory_answer=remember(
        text
    )


    if memory_answer:

        return memory_answer





    context=memory_context()



    user_text=text



    if context:


        user_text=(

            "Информация о пользователе:\n"

            +

            context

            +

            "\n\nЗапрос:\n"

            +

            text

        )





    conversation.append(

        {

            "role":

                "user",


            "content":

                user_text

        }

    )





    if len(conversation)>MAX_HISTORY:


        conversation=(

            [

                conversation[0]

            ]

            +

            conversation[-MAX_HISTORY:]

        )







    try:



        gigachat.check()



        if not gigachat.token:


            return (

                "Нет подключения к GigaChat"

            )





        headers={


            "Authorization":

                "Bearer "+gigachat.token,


            "Content-Type":

                "application/json"


        }





        payload={


            "model":

                "GigaChat",


            "messages":

                conversation,


            "temperature":

                0.4,


            "max_tokens":

                300


        }





        r=http.post(


            CHAT_URL,


            headers=headers,


            json=payload,


            verify=False,


            timeout=60


        )





        if r.status_code==401:


            gigachat.get_token()


            return ask_ai(text)







        if r.status_code!=200:


            logging.error(

                r.text

            )


            return (

                "Ошибка ответа GigaChat"

            )







        answer=(

            r.json()

            ["choices"]

            [0]

            ["message"]

            ["content"]

        )




        answer=answer.strip()





        conversation.append(

            {

                "role":

                    "assistant",


                "content":

                    answer

            }

        )




        return answer





    except Exception as e:


        logging.error(

            "AI ERROR "+str(e)

        )


        return (

            "Не удалось получить ответ"

        )





print(
    "GIGACHAT ENGINE READY"
)
# ==========================================================
# AI VOICE ASSISTANT PRO v2
# PART 5/6
# WINDOWS PRO CONTROL
# ==========================================================

import pyautogui
import GPUtil

from pycaw.pycaw import (
    AudioUtilities,
    IAudioEndpointVolume
)

from ctypes import (
    cast,
    POINTER
)

from comtypes import CLSCTX_ALL



# ==========================================================
# VOLUME CONTROL
# ==========================================================


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

        level = volume.GetMasterVolumeLevelScalar()

        return int(level * 100)


    except Exception as e:

        logging.error("GET VOLUME ERROR " + str(e))

        return None




def set_volume(value):

    try:

        if value < 0:
            value = 0

        if value > 100:
            value = 100


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


        volume.SetMasterVolumeLevelScalar(
            value / 100,
            None
        )


        return f"Громкость {value} процентов"


    except Exception as e:

        logging.error(
            "SET VOLUME ERROR " + str(e)
        )

        return "Ошибка управления громкостью"

# ==========================================================
# HARDWARE INFO
# ==========================================================


def ram_info():


    ram=psutil.virtual_memory()


    return (

        f"Оперативная память. "

        f"Всего {round(ram.total/1024**3,1)} гигабайт. "

        f"Используется {round(ram.used/1024**3,1)} гигабайт."

    )





def cpu_info():


    return (

        "Процессор "

        +

        platform.processor()

        +

        ". Загрузка "

        +

        str(
            psutil.cpu_percent(1)
        )

        +

        " процентов"

    )





def disk_info():


    disk=psutil.disk_usage(
        "C:\\"
    )


    return (

        f"На диске C свободно "

        f"{round(disk.free/1024**3,1)} гигабайт"

    )





def gpu_info():


    try:


        gpu=GPUtil.getGPUs()


        if not gpu:

            return "Видеокарта не найдена"



        return (

            "Видеокарта "

            +

            gpu[0].name

            +

            ". Загрузка "

            +

            str(
                round(
                    gpu[0].load*100
                )
            )

            +

            " процентов"

        )


    except:


        return "Нет данных о видеокарте"







# ==========================================================
# APPLICATION CONTROL
# ==========================================================
def activate_browser():

    windows = []

    def callback(hwnd, extra):

        title = win32gui.GetWindowText(hwnd).lower()

        if (
            "youtube" in title
            or
            "chrome" in title
            or
            "яндекс" in title
        ):
            windows.append(hwnd)


    win32gui.EnumWindows(
        callback,
        None
    )


    if windows:

        hwnd = windows[0]

        win32gui.ShowWindow(
            hwnd,
            win32con.SW_RESTORE
        )

        win32gui.SetForegroundWindow(
            hwnd
        )

        return True


    return False

PROGRAMS={


    "chrome":

        "start chrome",


    "google":

        "start chrome",


    "youtube":

        "start https://youtube.com",


    "discord":

        "start discord",


    "telegram":

        "start telegram",


    "калькулятор":

        "calc",


    "блокнот":

        "notepad"



}










# ==========================================================
# APPLICATION LAUNCHER PRO
# ==========================================================

import webbrowser


def open_program(text):

    text = text.lower()


    # ==============================
    # WINDOWS PROGRAMS
    # ==============================

    apps = {

        "калькулятор":
            "calc.exe",

        "калькулятор windows":
            "calc.exe",
        "блокнот":
            "notepad.exe",

        "проводник":
            "explorer.exe",

        "мой компьютер":
            "explorer.exe",

        "диспетчер задач":
            "taskmgr.exe",

        "cmd":
            "cmd.exe",

        "командная строка":
            "cmd.exe",

    }


    for name, command in apps.items():

        if name in text:

            subprocess.Popen(
                command,
                shell=True
            )

            return "Открываю " + name



    # ==============================
    # BROWSERS
    # ==============================

    # ==================================================
    # САЙТЫ + ПОИСК
    # ==================================================

    # Поиск в браузере
    if "найди" in text or "поиск" in text:

        query = text

        remove_words = [
            "найди",
            "поиск",
            "в интернете",
            "в браузере",
            "браузере"
        ]

        for word in remove_words:
            query = query.replace(word, "")

        query = query.strip()

        if query:
            url = (
                    "https://www.google.com/search?q="
                    +
                    urllib.parse.quote(query)
            )

            webbrowser.open(url)

            return (
                    "Ищу в браузере "
                    +
                    query
            )

    # Поиск видео YouTube
    if "ютуб" in text or "видео" in text:

        query = text

        remove_words = [
            "ютуб",
            "youtube",
            "найди",
            "видео",
            "посмотри"
        ]

        for word in remove_words:
            query = query.replace(
                word,
                ""
            )

        query = query.strip()

        if query:
            url = (

                    "https://www.youtube.com/results?search_query="

                    +

                    urllib.parse.quote(query)

            )

            webbrowser.open(url)

            return (

                    "Ищу видео на ютубе "

                    +

                    query

            )

    websites = {

        "яндекс музыку":
            "https://music.yandex.ru",

        "музыку":
            "https://music.yandex.ru",

        "яндекс диск":
            "https://disk.yandex.ru",

        "диск":
            "https://disk.yandex.ru",

        "почту":
            "https://mail.yandex.ru",

        "яндекс почту":
            "https://mail.yandex.ru",

        "ютуб":
            "https://youtube.com",

        "гугл":
            "https://google.com"

    }

    for name, url in websites.items():

        if name in text:
            webbrowser.open(url)

            return (

                    "Открываю "

                    +

                    name

            )




    # ==============================
    # WINDOWS FOLDERS
    # ==============================


    folders = {


        "документы":
            Path.home() / "Documents",


        "загрузки":
            Path.home() / "Downloads",


        "рабочий стол":
            Path.home() / "Desktop",


        "фото":
            Path.home() / "Pictures",


        "изображения":
            Path.home() / "Pictures",


        "видео":
            Path.home() / "Videos",


        "мои файлы":
            Path.home(),


        "домашняя папка":
            Path.home(),


        "музыка папка":
            Path.home() / "Music"

    }



    for name,path in folders.items():

        if name in text:


            subprocess.Popen(
                [
                    "explorer",
                    str(path)
                ]
            )


            return "Открываю " + name




    return None
# ==========================================================
# CLOSE APPLICATION PRO
# ==========================================================


def close_program(text):

    text=text.lower()


    if "закрой программу" in text:

        pyautogui.hotkey(
            "alt",
            "f4"
        )

        return "Закрываю программу"



    programs={

        "хром":
        "chrome.exe",

        "браузер":
        "yandex.exe",

        "дискорд":
        "Discord.exe",

        "телеграм":
        "Telegram.exe",

        "блокнот":
        "notepad.exe"

    }


    for name,process in programs.items():

        if name in text:

            os.system(
                "taskkill /f /im "+process
            )

            return "Закрываю "+name


    return None



# ==========================================================
# SCREENSHOT
# ==========================================================


def screenshot():


    path=TEMP_DIR / (

        "screen.png"

    )


    img=pyautogui.screenshot()


    img.save(
        path
    )


    return (

        "Скриншот сохранён"

    )





# ==========================================================
# CLOSE TAB / BROWSER
# ==========================================================

def close_tab(text):

    text=text.lower()


    if (
        "закрой вкладку" in text
        or
        "закрой эту вкладку" in text
    ):

        pyautogui.hotkey(
            "ctrl",
            "w"
        )

        return "Закрываю вкладку"



    if (
        "новая вкладка" in text
        or
        "открой вкладку" in text
    ):

        pyautogui.hotkey(
            "ctrl",
            "t"
        )

        return "Открываю новую вкладку"



    if "переключи вкладку" in text:

        pyautogui.hotkey(
            "ctrl",
            "tab"
        )

        return "Переключаю вкладку"



    if "закрой браузер" in text:

        pyautogui.hotkey(
            "alt",
            "f4"
        )

        return "Закрываю браузер"



    return None

# ==========================================================
# WINDOWS COMMAND PROCESSOR
# ==========================================================


def windows_command(text):
    text=text.lower()
    # =========================================
    # YOUTUBE CONTROL PRO
    # =========================================

    if (
        "ютуб пауза" in text
        or "youtube пауза" in text
        or "ютуб стоп" in text
        or "youtube стоп" in text
    ):
        pyautogui.press("space")

        return "Ютуб поставлен на паузу"



    if (
        "ютуб продолжи" in text
        or "youtube продолжи" in text
        or "ютуб продолжить" in text
        or "youtube продолжить" in text
        or "ютуб включи" in text
    ):

        pyautogui.press("space")

        return "Продолжаю видео"



    if (
        "ютуб следующее" in text
        or "youtube следующее" in text
        or "ютуб далее" in text
        or "youtube далее" in text
        or "ютуб дальше" in text
    ):

        pyautogui.click()
        time.sleep(0.2)

        pyautogui.hotkey(
            "shift",
            "n"
        )

        return "Следующее видео"



    if (
        "ютуб предыдущее" in text
        or "youtube предыдущее" in text
        or "ютуб назад" in text or "youtube назад" in text
    ):

        pyautogui.click()
        time.sleep(0.2)

        pyautogui.hotkey(
            "shift",
            "p"
        )

        return "Предыдущее видео"



    if (
        "ютуб полный экран" in text
        or "youtube полный экран" in text
        or "ютуб на весь экран" in text or "ютуб на весь экран" in text
    ):

        pyautogui.click()
        time.sleep(0.2)

        pyautogui.press(
            "f"
        )

        return "Включаю полный экран"



    if (
        "ютуб выйти из полного экрана" in text
        or "youtube выйти из полного экрана" in text
        or "ютуб маленький экран" in text
    ):

        pyautogui.press(
            "f"
        )

        return "Выключаю полный экран"



    if (
        "ютуб громче" in text
        or "youtube громче" in text
    ):

        pyautogui.click()

        for i in range(5):
            pyautogui.press("up")

        return "Делаю громче"



    if (
        "ютуб тише" in text
        or "youtube тише" in text
    ):

        pyautogui.click()

        for i in range(5):
            pyautogui.press("down")

        return "Делаю тише"



    if (
        "ютуб вперед" in text
        or "youtube вперед"
        in text
    ):

        pyautogui.click()
        pyautogui.press("right")

        return "Перематываю вперед"



    if (
        "ютуб назад" in text
    ):

        pyautogui.click()
        pyautogui.press("left")

        return "Перематываю назад"

    # ==========================
    # ГРОМКОСТЬ
    # ==========================

    if (
            "громкость" in text
            or
            "звук" in text
    ):

        numbers = re.findall(
            r"\d+",
            text
        )

        if numbers:
            return set_volume(
                int(numbers[0])
            )

        word_number = words_to_number(text)

        if word_number is not None:
            return set_volume(
                word_number
            )

    if "увеличь звук" in text:


        v=get_volume()


        if v is not None:

            return set_volume(
                min(
                    100,
                    v+10
                )
            )
    if "громче" in text:

        v = get_volume()

        if v is not None:
            return set_volume(
                v + 10
            )







    if "уменьши звук" in text:


        v=get_volume()


        if v is not None:

            return set_volume(
                max(
                    0,
                    v-10
                )
            )
    if "тише" in text:

        v = get_volume()

        if v is not None:
            return set_volume(
                v - 10
            )
    if "какая громкость" in text:
        v = get_volume()

        return f"Сейчас громкость {v} процентов"





    if "оперативная память" in text:


        return ram_info()





    if "процессор" in text:


        return cpu_info()





    if "видеокарта" in text:


        return gpu_info()





    if "память" in text:


        return disk_info()





    if "скриншот" in text:


        return screenshot()






    result=open_program(text)


    if result:

        return result

    result = close_tab(text)

    if result:
        return result

    result=close_program(text)



    if result:

        return result

    if (
            "выключи компьютер" in text
            or
            "выключи пк" in text
            or
            "заверши работу компьютера" in text
    ):
        speak("Выключаю компьютер")

        os.system(
            "shutdown /s /t 5"
        )

        return "Выключаю компьютер"

    if (
            "перезагрузи компьютер" in text
            or
            "перезагрузи пк" in text
            or
            "перезапусти компьютер" in text
    ):
        speak("Перезагружаю компьютер")

        os.system(
            "shutdown /r /t 5"
        )

        return "Перезагружаю компьютер"



print(
    "WINDOWS CONTROL READY"
)
# ==========================================================
# AI VOICE ASSISTANT PRO v2
# PART 6/6
# MAIN ENGINE
# ==========================================================


import traceback



# ==========================================================
# ACTIVATION
# ==========================================================


def remove_activation(text):

    text = text.lower()

    triggers = config.get(
        "activation",
        [
            "джарвис",
            "ассистент",
            "эй",
            "пятница"
        ]
    )


    for trigger in triggers:

        if trigger in text:

            text = text.replace(
                trigger,
                ""
            )


    text = " ".join(
        text.split()
    )


    if text:
        return text


    return None






# ==========================================================
# COMMAND ROUTER
# ==========================================================


def process_command(text):


    if not text:

        return None





    # память

    mem=remember(
        text
    )


    if mem:

        return mem





    # Windows команды

    result=windows_command(

        text

    )


    if result:

        return result





    # AI

    return ask_ai(

        text

    )









# ==========================================================
# VOICE LOOP
# ==========================================================

def wait_activation():
    """
    Ждёт только ключевое слово.
    """
    while assistant_running:

        text = listen()

        if not text:
            continue

        triggers = [
            "джарвис",
            "эй",
            "ассистент",
            "компьютер",
            "пятница"
        ]

        for trigger in triggers:
            if trigger in text:
                return


def voice_loop():

    global assistant_running

    print()
    print("================================")
    print(" ASSISTANT READY")
    print(" Скажите: Джарвис")
    print("================================")

    while assistant_running:

        try:

            # ждём активацию
            wait_activation()

            speak("Слушаю")

            # слушаем только команду
            command = listen()

            if not command:
                continue

            print("COMMAND:", command)

            if command in [
                "выход",
                "стоп",
                "закройся"
            ]:
                speak("Завершаю работу")
                assistant_running = False
                break

            answer = process_command(command)

            if answer:
                print("AI:", answer)
                speak(answer)

        except Exception as e:
            logging.error("LOOP ERROR " + str(e))
            traceback.print_exc()








# ==========================================================
# STARTUP
# ==========================================================


def main():


    logging.info(

        "ASSISTANT START"

    )



    print(

"""
=====================================

     AI VOICE ASSISTANT PRO v2

=====================================
"""

    )



    try:


        check_environment()


        clean_temp()


        first_start()



        load_vosk()



        print(

            "Система готова"

        )



        speak(

            "Ассистент запущен"

        )



        voice_loop()




    except KeyboardInterrupt:


        print(

            "Остановка"

        )




    except Exception as e:


        logging.exception(e)


        print(

            "КРИТИЧЕСКАЯ ОШИБКА"

        )

        print(e)




    finally:


        clean_temp()



        logging.info(

            "ASSISTANT STOP"

        )







# ==========================================================
# RUN
# ==========================================================


if __name__=="__main__":


    main()
