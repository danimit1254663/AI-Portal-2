import time
import logging
import traceback
from core.config import first_start_setup
from ui.hud import (
    open_hud,
    set_status,
    set_command,
    set_answer
)
from ui.hud import (
    open_hud,
    hide_hud,
    set_status,
    set_command,
    set_answer
)
from ui.hud import open_hud
from core.config import config


from voice.vosk_engine import listen
import core.state as state

from voice.tts import speak


from commands.windows import windows_command


from ai.giga import GigaAI


from ai.memory import remember
import os
import sys
import subprocess


VENV_DIR = "venv"


def create_venv():
    print("Создание виртуального окружения...")

    subprocess.check_call([
        sys.executable,
        "-m",
        "venv",
        VENV_DIR
    ])


def get_venv_python():
    if os.name == "nt":
        return os.path.join(VENV_DIR, "Scripts", "python.exe")
    else:
        return os.path.join(VENV_DIR, "bin", "python")


def install_requirements():
    python = get_venv_python()

    print("Установка зависимостей...")

    subprocess.check_call([
        python,
        "-m",
        "pip",
        "install",
        "-r",
        "requirements.txt"
    ])


def check_environment():
    python = get_venv_python()

    if not os.path.exists(python):
        create_venv()

    install_requirements()


if __name__ == "__main__":

    check_environment()

    print("AI Portal запущен")

    # дальше твой код
SESSION_TIME = 20


# ======================================
# LOG
# ======================================


logging.basicConfig(

    filename="assistant.log",

    level=logging.INFO,

    format="%(asctime)s %(levelname)s %(message)s"

)










# ======================================
# ACTIVATION
# ======================================


def check_activation(text):


    triggers=config.get(

        "activation",

        [

            "джарвис",

            "ассистент"

        ]

    )


    for word in triggers:


        if word in text:


            return True



    return False






def remove_activation(text):


    triggers=config.get(

        "activation",

        [

            "джарвис",

            "ассистент"

        ]

    )


    for word in triggers:


        text=text.replace(

            word,

            ""

        )


    return text.strip()






# ======================================
# COMMAND PROCESSOR
# ======================================


def process_command(text):


    if not text:

        return None



    # память

    mem=remember(text)


    if mem:

        return mem
    if (
            "сон" in text
            or
            "усни" in text
    ):
        state.microphone_enabled = False

        return "Перехожу в режим сна"
    if (
            "проснись" in text
    ):
        state.microphone_enabled = True

        return "Микрофон включен"
    if (
            "спрячься" in text
            or
            "скройся" in text
            or
            "убери интерфейс" in text
    ):
        return hide_hud()
    # Windows команды

    result=windows_command(text)


    if result:

        return result





    # AI

    return ai.ask(text)






# ======================================
# WAIT WORD
# ======================================


def wait_activation():

    while assistant_running:

        text = listen()


        if not text:
            continue



        print(
            "HEARD:",
            text
        )



        triggers = config.get(

            "activation",

            [
                "джарвис",
                "ассистент"
            ]

        )



        for trigger in triggers:


            if trigger in text:


                command = text.replace(

                    trigger,

                    ""

                ).strip()



                # например:
                # "джарвис открой браузер"

                if command:

                    return command



                # только слово Джарвис

                return ""



    return None





# ======================================
# SESSION MODE
# ======================================


def session():

    global assistant_running


    last_command = time.time()


    while assistant_running:


        try:


            command = listen()



            if not command:

                if time.time() - last_command > SESSION_TIME:

                    return


                continue




            print(
                "COMMAND:",
                command
            )


            last_command = time.time()



            if command in [

                "стоп",

                "спать",

                "отмена"

            ]:


                speak(

                    "Переход в ожидание"

                )

                return





            answer = process_command(

                command

            )



            if answer:


                print(

                    "JARVIS:",

                    answer

                )


                speak(

                    answer

                )



        except Exception as e:


            logging.error(

                "SESSION ERROR "

                + str(e)

            )

            return




# ======================================
# INIT
# ======================================


assistant_running=True


ai = GigaAI()



SESSION_TIME = 15
# ======================================
# MAIN LOOP
# ======================================


def voice_loop():

    global assistant_running



    print()

    print("======================")
    print(" JARVIS READY ")
    print(" Скажите Джарвис ")
    print("======================")



    while assistant_running:


        try:


            command = wait_activation()



            if command is None:

                continue




            # если сказали только Джарвис

            if command == "":


                speak(

                    "Слушаю"

                )


                command = listen()



                if not command:

                    continue





            print(

                "COMMAND:",

                command

            )



            if command in [

                "стоп",

                "выход",

                "закройся"

            ]:


                speak(

                    "Завершаю работу"

                )


                assistant_running=False

                break





            answer = process_command(

                command

            )


            if answer:
                set_command(command)

                set_answer(answer)

                speak(answer)




            # после выполнения
            # сразу обратно ждём слово Джарвис


        except Exception as e:


            logging.error(

                str(e)

            )

            traceback.print_exc()

# ======================================
# START
# ======================================


def main():
    first_start_setup()
    print(

        """

============================

 AI VOICE ASSISTANT PRO

============================

        """

    )



    print(

        "Запуск..."

    )

    open_hud()

    speak(

        "Ассистент запущен"

    )



    voice_loop()






if __name__=="__main__":


    main()