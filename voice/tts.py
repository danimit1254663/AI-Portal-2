import os
import uuid
import pygame
import torch
import soundfile as sf
import re

from num2words import num2words
from pathlib import Path


# ==========================
# PATHS
# ==========================

BASE_DIR = Path.cwd()

TEMP_DIR = BASE_DIR / "temp"
CACHE_DIR = BASE_DIR / "cache"


TEMP_DIR.mkdir(
    exist_ok=True
)

CACHE_DIR.mkdir(
    exist_ok=True
)



# ==========================
# AUDIO
# ==========================

SAMPLE_RATE = 48000


pygame.init()

pygame.mixer.init()



# ==========================
# MODEL
# ==========================

tts_model = None

tts_ready = False



def load_tts():

    global tts_model
    global tts_ready


    if tts_ready:

        return True



    try:

        print(
            "Загрузка Silero TTS..."
        )


        os.environ[
            "TORCH_HOME"
        ] = str(CACHE_DIR)



        tts_model, _ = torch.hub.load(

            repo_or_dir=
            "snakers4/silero-models",

            model=
            "silero_tts",

            language=
            "ru",

            speaker=
            "v5_ru",

            trust_repo=True

        )



        tts_ready=True


        print(
            "Silero TTS готов"
        )


        return True



    except Exception as e:

        print(
            "TTS ERROR:",
            e
        )

        return False





# ==========================
# PLAY
# ==========================

def play_audio(audio):


    filename = TEMP_DIR / (

        str(uuid.uuid4())

        +

        ".wav"

    )


    sf.write(

        filename,

        audio.numpy(),

        SAMPLE_RATE

    )



    pygame.mixer.music.load(

        str(filename)

    )


    pygame.mixer.music.play()



    while pygame.mixer.music.get_busy():

        pygame.time.wait(
            100
        )



    pygame.mixer.music.stop()


    pygame.mixer.music.unload()



    try:

        filename.unlink()

    except:

        pass




def prepare_numbers(text):

    def replace_number(match):

        number = int(match.group())

        try:
            return num2words(
                number,
                lang="ru"
            )

        except:
            return match.group()


    return re.sub(
        r"\d+",
        replace_number,
        text
    )
# ==========================
# SPEAK
# ==========================


def speak(text):


    if not text:

        return


    if not load_tts():

        return


    text = prepare_numbers(text)


    print(
        "JARVIS:",
        text
    )


    audio = tts_model.apply_tts(

        text=text,

        speaker="kseniya",

        sample_rate=SAMPLE_RATE,

        put_accent=True,

        put_yo=True

    )


    play_audio(
        audio
    )