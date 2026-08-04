import os
import json
import zipfile
import requests
import sounddevice as sd
import queue

from core.language import normalize_text
from pathlib import Path
from vosk import Model, KaldiRecognizer

from ui.hud import set_reactor_speed

import core.state as state

# ==============================
# PATHS
# ==============================

BASE_DIR = Path.cwd()

MODELS_DIR = BASE_DIR / "models"

MODELS_DIR.mkdir(
    exist_ok=True
)


# ==============================
# VOSK MODEL
# ==============================

MODEL_URL = (
    "https://alphacephei.com/vosk/models/"
    "vosk-model-small-ru-0.22.zip"
)


vosk_model = None



def download_model():

    archive = MODELS_DIR / "vosk.zip"


    if archive.exists():

        return archive


    print(
        "Скачиваю модель Vosk..."
    )


    r=requests.get(
        MODEL_URL,
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





def find_model():

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





def install_model():


    model=find_model()


    if model:

        return model



    archive=download_model()



    print(
        "Распаковка модели..."
    )


    with zipfile.ZipFile(
        archive
    ) as z:

        z.extractall(
            MODELS_DIR
        )


    archive.unlink()


    return find_model()





def load_vosk():

    global vosk_model


    if vosk_model:

        return True



    path=install_model()


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



# ==============================
# TEXT CLEAN
# ==============================


NUMBERS={

    "ноль":0,
    "один":1,
    "два":2,
    "три":3,
    "четыре":4,
    "пять":5,
    "десять":10,
    "двадцать":20,
    "тридцать":30,
    "сорок":40,
    "пятьдесят":50,
    "сто":100

}



def words_to_number(text):

    for word,num in NUMBERS.items():

        if word in text:

            return num


    return None




def clean_text(text):

    text=text.lower()


    trash=[
        "а",
        "эм",
        "ну"
    ]


    for x in trash:

        text=text.replace(
            " "+x+" ",
            " "
        )


    return " ".join(
        text.split()
    )





# ==============================
# LISTEN
# ==============================


def listen():
    if not state.microphone_enabled:
        return ""
    if not load_vosk():

        return ""



    recognizer=KaldiRecognizer(

        vosk_model,

        16000

    )


    print(
        "🎤 Слушаю..."
    )
    set_reactor_speed(20)


    def callback(
        indata,
        frames,
        time,
        status
    ):
        state.audio_queue.put(
            bytes(indata)
        )




    with sd.RawInputStream(

        samplerate=16000,

        blocksize=4000,

        dtype="int16",

        channels=1,

        callback=callback

    ):


        while True:

            data = state.audio_queue.get()



            if recognizer.AcceptWaveform(
                data
            ):


                result=json.loads(

                    recognizer.Result()

                )


                text=result.get(
                    "text",
                    ""
                )


                text=normalize_text(text)


                if len(text)>1:


                    print(
                        "USER:",
                        text
                    )

                    set_reactor_speed(5)
                    return text