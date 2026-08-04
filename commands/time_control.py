from datetime import datetime
from ui.hud import set_status



def get_time(text):


    if (
        "который час" in text
        or
        "сколько времени" in text
    ):


        now=datetime.now()


        set_status(
            "Показываю время"
        )


        return (

            f"Сейчас "

            f"{now.hour} часов "

            f"{now.minute} минут"

        )


    return None