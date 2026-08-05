import json
from pathlib import Path
from dotenv import load_dotenv
from voice.tts import speak
import os
from pathlib import Path
from dotenv import load_dotenv
import os


ENV_FILE = Path(".env")


def first_start_setup():

    if ENV_FILE.exists():

        load_dotenv()
        return


    print()
    print("==============================")
    print("      JARVIS FIRST START")
    print("==============================")
    print()


    try:
        speak(
            "Здравствуйте. Я впервые запускаюсь. Давайте настроим меня."
        )
    except:
        pass


    try:

        speak(
            "Введите API ключ"
        )

    except:
        pass


    api_key = input(
        "API ключ: "
    )
    with open(
        ENV_FILE,
        "w",
        encoding="utf-8"
    ) as f:


        f.write(
f"""
GIGACHAT_CREDENTIALS={api_key}
GIGACHAT_API_PERS=GIGACHAT_API_PERS
GIGACHAT_MODEL=GigaChat-2
"""
        )


    try:

        speak(
            "Настройка завершена. Я готов к работе. Рекомендую перезагрузить меня , для завершения наастройки."
        )

    except:
        pass


    load_dotenv()

def get_setting(name, default=None):

    load_dotenv()

    return os.getenv(
        name,
        default
    )


BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(
    BASE_DIR / ".env"
)
CONFIG_FILE = BASE_DIR / "config.json"


DEFAULT_CONFIG = {

    "voice": "kseniya",

    "activation": [
        "джарвис",
        "ассистент"
    ],

    "language": "ru",

}







config = {}



def save_config():

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
def get_gigachat_config():

    return {

        "credentials": os.getenv(
            "GIGACHAT_CREDENTIALS"
        ),

        "scope": os.getenv(
            "GIGACHAT_SCOPE",
            "GIGACHAT_API_PERS"
        ),

        "model": os.getenv(
            "GIGACHAT_MODEL",
            "GigaChat"
        )

    }


import os
from pathlib import Path
from dotenv import load_dotenv



load_config()