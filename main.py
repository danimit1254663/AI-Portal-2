
# ============================================================
# JARVIS - main.py
# ============================================================

import time
import logging
import traceback
import os
import threading
import queue
import serial

from datetime import datetime
from dotenv import load_dotenv

from core.config import first_start_setup, config

from ui.hud import (
    open_hud,
    hide_hud,
    set_status,
    set_command,
    set_answer
)

from voice.vosk_engine import listen
from voice.tts import speak

import core.state as state

from ai.giga import GigaAI
from ai.memory import remember

from commands.windows import windows_command

from Telegram_bot import Tg_bot, ask_start


# ============================================================
# НАСТРОЙКИ
# ============================================================

load_dotenv()

assistant_running = True

ai = GigaAI()

SERIAL_PORT = "COM4"
SERIAL_BAUDRATE = 9600

arduino = None


# ============================================================
# LCD QUEUE
# ============================================================

lcd_queue = queue.Queue()


# ============================================================
# LOGGING
# ============================================================

logging.basicConfig(
    filename="assistant.log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)


# ============================================================
# РУССКИЕ БУКВЫ CGRAM
# ============================================================

CUSTOM_RUSSIAN = set(
    "БГДЖЗИЙЛПУФЦЧШЩЪЫЬЭЮЯ"
    "бвгджзийклмноптфцчшщъыьэюя"
    "Ёё"
)


# ============================================================
# РАЗБИВКА ТЕКСТА НА LCD 16x2
#
# Максимум:
# 16 символов в строке
# 2 строки
# максимум 8 разных CGRAM-букв
# ============================================================

def make_lcd_pages(text):

    if not text:
        return []

    text = str(text)

    text = text.replace("\r", " ")
    text = text.replace("\n", " ")

    words = text.split()

    if not words:
        return []

    pages = []

    current_line1 = ""
    current_line2 = ""

    current_glyphs = set()


    def flush_page():

        nonlocal current_line1
        nonlocal current_line2
        nonlocal current_glyphs

        if current_line1 or current_line2:

            pages.append(
                (
                    current_line1,
                    current_line2
                )
            )

        current_line1 = ""
        current_line2 = ""
        current_glyphs = set()


    def word_glyphs(word):

        return {
            c
            for c in word
            if c in CUSTOM_RUSSIAN
        }


    for word in words:

        # ----------------------------------------------------
        # Очень длинное слово
        # ----------------------------------------------------

        if len(word) > 16:

            if current_line1 or current_line2:

                flush_page()


            while len(word) > 16:

                pages.append(
                    (
                        word[:16],
                        ""
                    )
                )

                word = word[16:]


            if not word:
                continue


        new_glyphs = (
            current_glyphs
            | word_glyphs(word)
        )


        # ----------------------------------------------------
        # Больше 8 CGRAM-букв
        # ----------------------------------------------------

        if len(new_glyphs) > 8:

            flush_page()

            new_glyphs = word_glyphs(word)


        # ----------------------------------------------------
        # Первая строка
        # ----------------------------------------------------

        if current_line1:

            candidate = (
                current_line1
                + " "
                + word
            )

        else:

            candidate = word


        if len(candidate) <= 16:

            current_line1 = candidate

            current_glyphs = new_glyphs

            continue


        # ----------------------------------------------------
        # Вторая строка
        # ----------------------------------------------------

        if current_line2:

            candidate = (
                current_line2
                + " "
                + word
            )

        else:

            candidate = word


        if len(candidate) <= 16:

            current_line2 = candidate

            current_glyphs = new_glyphs

            continue


        # ----------------------------------------------------
        # Страница заполнена
        # ----------------------------------------------------

        flush_page()

        current_line1 = word

        current_glyphs = word_glyphs(word)


    # --------------------------------------------------------
    # Последняя страница
    # --------------------------------------------------------

    flush_page()

    return pages


# ============================================================
# ARDUINO
# ============================================================

def connect_arduino():

    global arduino

    try:

        arduino = serial.Serial(
            SERIAL_PORT,
            SERIAL_BAUDRATE,
            timeout=1,
            write_timeout=2
        )

        time.sleep(2)

        arduino.reset_input_buffer()
        arduino.reset_output_buffer()

        print(
            f"[ARDUINO] Подключена: {SERIAL_PORT}"
        )

        logging.info(
            f"Arduino connected: {SERIAL_PORT}"
        )

    except Exception:

        arduino = None

        # В консоль ничего не выводим.
        logging.error(
            "Arduino connection error",
            exc_info=True
        )


# ============================================================
# ОТПРАВКА ДВУХ СТРОК
# ============================================================

def send_lcd_packet(line1="", line2=""):

    global arduino

    # Arduino нет — полностью молчим
    if arduino is None:
        return


    line1 = (
        ""
        if line1 is None
        else str(line1)
    )

    line2 = (
        ""
        if line2 is None
        else str(line2)
    )


    line1 = line1.replace(
        "\r",
        " "
    )

    line1 = line1.replace(
        "\n",
        " "
    )


    line2 = line2.replace(
        "\r",
        " "
    )

    line2 = line2.replace(
        "\n",
        " "
    )


    try:

        message = (
            line1
            + "\n"
            + line2
            + "\n"
        )


        data = message.encode(
            "utf-8"
        )


        arduino.write(
            data
        )

        arduino.flush()


    except Exception:

        arduino = None

        logging.error(
            "Serial send error",
            exc_info=True
        )


# ============================================================
# LCD WORKER
#
# Один поток отвечает за LCD.
# Поэтому COM4 никогда не используется
# одновременно несколькими потоками.
# ============================================================

def lcd_worker():

    while True:

        item = lcd_queue.get()


        if item is None:

            lcd_queue.task_done()

            break


        text, text2 = item


        try:

            # ------------------------------------------------
            # Две готовые строки
            # ------------------------------------------------

            if text2 is not None:

                if arduino is not None:

                    send_lcd_packet(
                        text,
                        text2
                    )


            else:

                # --------------------------------------------
                # Обычный текст
                # --------------------------------------------

                if arduino is not None:

                    pages = make_lcd_pages(
                        text
                    )


                    for index, page in enumerate(pages):

                        if arduino is None:
                            break


                        line1, line2 = page


                        print(
                            f"[LCD PAGE "
                            f"{index + 1}/"
                            f"{len(pages)}]"
                        )


                        send_lcd_packet(
                            line1,
                            line2
                        )


                        if (
                            index + 1
                            < len(pages)
                        ):

                            time.sleep(
                                1.5
                            )


        except Exception:

            logging.error(
                "LCD worker error",
                exc_info=True
            )


        finally:

            lcd_queue.task_done()


# ============================================================
# ОТПРАВКА НА LCD
# ============================================================

def send_lcd(text="", text2=None):

    # Arduino нет — ничего не добавляем в очередь
    if arduino is None:
        return


    lcd_queue.put(
        (
            text,
            text2
        )
    )


# ============================================================
# LCD СТАТУСЫ
# ============================================================

def lcd_start():

    send_lcd(
        "",
        ""
    )


def lcd_listening():

    send_lcd(
        "JARVIS",
        "LISTENING"
    )


def lcd_sleep():

    send_lcd(
        "JARVIS",
        "SLEEP"
    )


def lcd_status(status):

    send_lcd(
        "JARVIS",
        status
    )


# ============================================================
# КОМАНДА "ВЫВЕДИ НА ЭКРАН"
# ============================================================

def extract_screen_text(text):

    if not text:
        return None


    triggers = [

        "поставь на экран",
        "поставь на дисплей",

        "выведи на экран",
        "выведи на дисплей",

        "выведи на экране",
        "выведи на дисплее",

        "покажи на экран",
        "покажи на дисплей",

        "покажи на экране",
        "покажи на дисплее",

        "напиши на экран",
        "напиши на дисплей",

        "напиши на экране",
        "напиши на дисплее",

        "отобрази на экран",
        "отобрази на дисплей",

        "отобрази на экране",
        "отобрази на дисплее"
    ]


    triggers.sort(
        key=len,
        reverse=True
    )


    for trigger in triggers:

        if trigger in text:

            result = text.split(
                trigger,
                1
            )[1].strip()


            if result:

                return result


    return None


# ============================================================
# ОЧИСТКА ЭКРАНА
# ============================================================

def is_clear_screen_command(text):

    commands = [

        "очисти экран",
        "очисти дисплей",

        "сотри экран",
        "сотри дисплей",

        "убери с экрана",

        "очисти экран полностью",
        "очисти дисплей полностью"
    ]


    for command in commands:

        if command in text:
            return True


    return False


# ============================================================
# ВРЕМЯ
# ============================================================

def lcd_time():

    now = datetime.now()

    send_lcd(
        now.strftime("%H-%M"),
        ""
    )


# ============================================================
# ДАТА
# ============================================================

def lcd_date():

    now = datetime.now()

    send_lcd(
        now.strftime("%d.%m.%Y"),
        ""
    )


# ============================================================
# ВРЕМЯ + ДАТА
# ============================================================

def lcd_datetime():

    now = datetime.now()

    send_lcd(
        now.strftime("%H-%M"),
        now.strftime("%d.%m.%Y")
    )


# ============================================================
# ОБРАБОТКА КОМАНД
# ============================================================

def process_command(text):

    if not text:
        return None


    text = text.strip().lower()


    # ========================================================
    # LCD
    # ========================================================

    screen_text = extract_screen_text(
        text
    )


    if screen_text:

        print(
            f"[LCD COMMAND] -> {screen_text}"
        )


        send_lcd(
            screen_text
        )


        return "Вывожу на экран"


    # ========================================================
    # ОЧИСТКА
    # ========================================================

    if is_clear_screen_command(text):

        send_lcd(
            "",
            ""
        )

        return "Экран очищен"


    # ========================================================
    # ПАМЯТЬ
    # ========================================================

    mem = remember(
        text
    )

    if mem:

        return mem


    # ========================================================
    # СОН
    # ========================================================

    if (
        "сон" in text
        or "усни" in text
    ):

        state.microphone_enabled = False

        lcd_sleep()

        return "Перехожу в режим сна"


    # ========================================================
    # ПРОБУЖДЕНИЕ
    # ========================================================

    if "проснись" in text:

        state.microphone_enabled = True

        lcd_status(
            "AWAKE"
        )

        return "Микрофон включен"


    # ========================================================
    # HUD
    # ========================================================

    if (
        "спрячься" in text
        or "скройся" in text
        or "убери интерфейс" in text
    ):

        hide_hud()

        lcd_status(
            "HUD OFF"
        )

        return "Интерфейс скрыт"


    # ========================================================
    # ВРЕМЯ + ДАТА
    # ========================================================

    if (
        "время и дата" in text
        or "дату и время" in text
        or "время с датой" in text
    ):

        now = datetime.now()

        lcd_datetime()

        return (
            f"Сейчас "
            f"{now.strftime('%H')} часов "
            f"{now.strftime('%M')} минут, "
            f"дата "
            f"{now.strftime('%d.%m.%Y')}"
        )


    # ========================================================
    # ВРЕМЯ
    # ========================================================

    if (
        text == "время"
        or "который час" in text
        or "сколько времени" in text
        or "текущее время" in text
        or "сколько сейчас времени" in text
    ):

        now = datetime.now()

        lcd_time()

        return (
            f"Сейчас "
            f"{now.strftime('%H')} часов "
            f"{now.strftime('%M')} минут"
        )


    # ========================================================
    # ДАТА
    # ========================================================

    if (
        text == "дата"
        or "какая дата" in text
        or "сегодня какая дата" in text
        or "какое сегодня число" in text
        or "какое число" in text
    ):

        now = datetime.now()

        lcd_date()

        return (
            f"Сегодня "
            f"{now.strftime('%d.%m.%Y')}"
        )


    # ========================================================
    # WINDOWS
    # ========================================================

    win_res = windows_command(
        text
    )


    if win_res:

        if win_res == "__SHUTDOWN_REQUEST__":

            lcd_status(
                "SHUTDOWN"
            )

            os.system(
                "shutdown /s /t 5"
            )

            return "Выключаюсь"


        if win_res == "__REBOOT_REQUEST__":

            lcd_status(
                "REBOOT"
            )

            os.system(
                "shutdown /r /t 5"
            )

            return "Перезагружаю компьютер"


        return win_res


    # ========================================================
    # AI
    # ========================================================

    return ai.ask(
        text
    )


# ============================================================
# ОЖИДАНИЕ "ДЖАРВИС"
# ============================================================

def wait_activation():

    while assistant_running:

        text = listen()

        if not text:
            continue


        print(
            f"HEARD: {text}"
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

                return text.replace(
                    trigger,
                    "",
                    1
                ).strip()


    return None


# ============================================================
# LCD ОТВЕТ
# ============================================================

def lcd_answer(answer):

    if answer:

        send_lcd(
            answer
        )


# ============================================================
# ГОЛОСОВОЙ ЦИКЛ
# ============================================================

def voice_loop():

    global assistant_running


    print(
        "\n======================\n"
        " JARVIS READY \n"
        " Скажите Джарвис \n"
        "======================"
    )


    while assistant_running:

        try:

            command = wait_activation()


            if command is None:
                continue


            # ------------------------------------------------
            # Просто "Джарвис"
            # ------------------------------------------------

            if command == "":

                lcd_listening()

                speak(
                    "Слушаю"
                )


                command = listen()


                if not command:
                    continue


            print(
                f"COMMAND: {command}"
            )


            # ------------------------------------------------
            # ОСТАНОВКА
            # ------------------------------------------------

            if command in [
                "стоп",
                "выход",
                "закройся"
            ]:

                speak(
                    "Завершаю работу"
                )

                assistant_running = False

                break


            # ------------------------------------------------
            # ОБРАБОТКА
            # ------------------------------------------------

            answer = process_command(
                command
            )


            if answer:

                set_command(
                    command
                )

                set_answer(
                    answer
                )


                # ------------------------------------------------
                # LCD добавляется в очередь мгновенно.
                # Голос НЕ ждёт LCD.
                # ------------------------------------------------

                if extract_screen_text(
                    command
                ) is None:

                    lcd_answer(
                        answer
                    )


                # ------------------------------------------------
                # Голос сразу начинает говорить.
                # ------------------------------------------------

                speak(
                    answer
                )


        except Exception as e:

            logging.error(
                f"Voice Loop Error: {e}",
                exc_info=True
            )

            traceback.print_exc()


# ============================================================
# TELEGRAM
# ============================================================

def run_telegram_bot():

    try:

        print(
            "Запуск Telegram бота..."
        )


        if ask_start():

            Tg_bot()

        else:

            print(
                "Бот не запущен."
            )


    except Exception as e:

        logging.critical(
            f"Ошибка Telegram бота: {e}",
            exc_info=True
        )

        traceback.print_exc()


# ============================================================
# MAIN
# ============================================================

def main():

    global assistant_running


    # --------------------------------------------------------
    # Первоначальная настройка
    # --------------------------------------------------------

    first_start_setup()


    print("""
============================
 AI VOICE ASSISTANT PRO
============================
    """)


    # --------------------------------------------------------
    # Arduino
    # --------------------------------------------------------

    connect_arduino()


    # --------------------------------------------------------
    # LCD worker
    # --------------------------------------------------------

    lcd_thread = threading.Thread(
        target=lcd_worker,
        daemon=True
    )

    lcd_thread.start()


    # --------------------------------------------------------
    # HUD
    # --------------------------------------------------------

    open_hud()


    # --------------------------------------------------------
    # Очистка LCD
    # --------------------------------------------------------

    send_lcd(
        "",
        ""
    )


    # --------------------------------------------------------
    # Голос
    # --------------------------------------------------------

    speak(
        "Ассистент запущен"
    )


    # --------------------------------------------------------
    # Telegram
    # --------------------------------------------------------

    tg_thread = threading.Thread(
        target=run_telegram_bot,
        daemon=True
    )

    tg_thread.start()


    print(
        "Telegram бот запущен "
        "в отдельном потоке."
    )


    time.sleep(2)


    # --------------------------------------------------------
    # Голосовой цикл
    # --------------------------------------------------------

    voice_loop()


    # --------------------------------------------------------
    # Остановка LCD worker
    # --------------------------------------------------------

    lcd_queue.put(
        None
    )


    # --------------------------------------------------------
    # Закрытие Arduino
    # --------------------------------------------------------

    if arduino:

        try:

            arduino.close()

            print(
                "[ARDUINO] Serial закрыт."
            )

        except Exception:

            pass


    print(
        "Ассистент остановлен."
    )


# ============================================================
# START
# ============================================================

if __name__ == "__main__":

    main()

