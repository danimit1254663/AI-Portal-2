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
            "Как мне вас называть?"
        )

    except:
        pass


    name = input(
        "Ваше имя: "
    )


    try:

        speak(
            "Введите API ключ"
        )

    except:
        pass


    api_key = input(
        "API ключ: "
    )


    try:

        speak(
            "Включить интерфейс HUD при запуске?"
        )

    except:
        pass


    hud = input(
        "HUD да или нет: "
    )


    try:

        speak(
            "Включить постоянное прослушивание микрофона?"
        )

    except:
        pass


    microphone = input(
        "Микрофон да или нет: "
    )


    with open(
        ENV_FILE,
        "w",
        encoding="utf-8"
    ) as f:


        f.write(
f"""USERNAME={name}
API_KEY={api_key}
HUD={hud}
MICROPHONE={microphone}
"""
        )


    try:

        speak(
            "Настройка завершена. Я готов к работе."
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


ENV_FILE = Path(".env")


def setup_env():

    if not ENV_FILE.exists():

        print("==============================")
        print(" JARVIS FIRST START ")
        print("==============================")

        print(
            "Файл .env не найден."
        )

        api_key = input(
            "Введите API ключ: "
        )


        with open(
            ENV_FILE,
            "w",
            encoding="utf-8"
        ) as f:

            f.write(
                f"API_KEY={api_key}\n"
            )


        print(
            "Настройка завершена."
        )


    load_dotenv()



def get_api_key():

    return os.getenv(
        "API_KEY"
    )
load_config()