import json
from pathlib import Path
from dotenv import load_dotenv

import os



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



load_config()