# ============================================================
# JARVIS - main.py
# ============================================================

import time
import logging
import traceback
import os
import threading
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
# LOGGING
# ============================================================

logging.basicConfig(
    filename="assistant.log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)


# ============================================================
# РУССКИЕ БУКВЫ, КОТОРЫЕ ТРЕБУЮТ CGRAM
#
# Эти буквы должны быть согласованы
# с LCD_1602_RUS_ALL.h
# ============================================================

CUSTOM_RUSSIAN = set(
    "БГДЖЗИЙЛПУФЦЧШЩЪЫЬЭЮЯ"
    "бвгджзийклмноптфцчшщъыьэюя"
    "Ёё"
)


# ============================================================
# ПРОВЕРКА:
# сколько разных CGRAM-букв будет на странице
# ============================================================

def count_custom_letters(text):

    result = set()

    for char in text:

        if char in CUSTOM_RUSSIAN:

            result.add(char)

    return len(result)


# ============================================================
# РАЗБИВКА ТЕКСТА
#
# Максимум:
#
# 16 символов строка
# 2 строки страница
#
# И НЕ БОЛЕЕ 8 разных CGRAM-букв
# на одной странице.
# ============================================================

def make_lcd_pages(text):

    if not text:

        return []


    text = str(text)

    text = text.replace(
        "\r",
        " "
    )

    text = text.replace(
        "\n",
        " "
    )

    words = text.split()

    if not words:

        return []


    pages = []

    current_line1 = ""
    current_line2 = ""

    current_glyphs = set()


    def page_text():

        return (
            current_line1
            + " "
            + current_line2
        ).strip()


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


    def try_add_word(line, word):

        if not line:

            return word

        return line + " " + word


    for word in words:

        # ----------------------------------------------------
        # Очень длинное слово
        # ----------------------------------------------------

        if len(word) > 16:

            # Сначала закрываем текущую страницу,
            # чтобы не смешивать длинное слово
            # с уже набранным текстом.

            if current_line2:

                flush_page()

            elif current_line1:

                flush_page()


            # Режем длинное слово по 16 Unicode-символов.
            # Здесь Python работает именно с символами,
            # а не с UTF-8 байтами.

            while len(word) > 16:

                part = word[:16]

                pages.append(
                    (
                        part,
                        ""
                    )
                )

                word = word[16:]


            if not word:

                continue


        # ----------------------------------------------------
        # Проверяем новые CGRAM-буквы
        # ----------------------------------------------------

        word_glyphs = {
            c for c in word
            if c in CUSTOM_RUSSIAN
        }


        new_glyphs = (
            current_glyphs
            | word_glyphs
        )


        # ----------------------------------------------------
        # Если больше 8 CGRAM-букв —
        # новая страница.
        # ----------------------------------------------------

        if len(new_glyphs) > 8:

            flush_page()

            new_glyphs = word_glyphs


        # ----------------------------------------------------
        # Пытаемся поставить слово в первую строку
        # ----------------------------------------------------

        candidate = try_add_word(
            current_line1,
            word
        )


        if len(candidate) <= 16:

            current_line1 = candidate

            current_glyphs = new_glyphs

            continue


        # ----------------------------------------------------
        # Не помещается в первую строку.
        # Пробуем вторую.
        # ----------------------------------------------------

        candidate = try_add_word(
            current_line2,
            word
        )


        if len(candidate) <= 16:

            current_line2 = candidate

            current_glyphs = new_glyphs

            continue


        # ----------------------------------------------------
        # Обе строки заняты.
        # Закрываем страницу.
        # ----------------------------------------------------

        flush_page()


        # ----------------------------------------------------
        # Начинаем новую страницу.
        # ----------------------------------------------------

        word_glyphs = {
            c for c in word
            if c in CUSTOM_RUSSIAN
        }

        current_line1 = word

        current_glyphs = word_glyphs


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
            f"[ARDUINO] Подключена: "
            f"{SERIAL_PORT}"
        )

    except Exception:

        arduino = None

        # Не выводим ошибку в консоль.
        logging.error(
            "Arduino connection error",
            exc_info=True
        )


# ============================================================
# ОТПРАВКА ДВУХ СТРОК
# ============================================================
def send_lcd_packet(line1="", line2=""):

    global arduino

    # Arduino не подключена —
    # полностью выходим без Serial-вывода
    if arduino is None:
        return

    line1 = "" if line1 is None else str(line1)
    line2 = "" if line2 is None else str(line2)

    line1 = line1.replace("\r", " ")
    line1 = line1.replace("\n", " ")

    line2 = line2.replace("\r", " ")
    line2 = line2.replace("\n", " ")

    try:

        message = (
            line1
            + "\n"
            + line2
            + "\n"
        )

        data = message.encode("utf-8")

        arduino.write(data)
        arduino.flush()

    except Exception as e:

        # Если Arduino отключилась во время работы,
        # перестаём пытаться отправлять данные.
        arduino = None

        logging.error(
            "Serial send error",
            exc_info=True
        )
# ============================================================
# ОТПРАВКА ТЕКСТА НА LCD
# ============================================================

def send_lcd(text="", text2=None):

    # --------------------------------------------------------
    # Прямая отправка двух строк
    # --------------------------------------------------------

    if text2 is not None:

        send_lcd_packet(
            text,
            text2
        )

        return


    if text is None:

        return


    pages = make_lcd_pages(
        text
    )


    if not pages:

        send_lcd_packet(
            "",
            ""
        )

        return


    # --------------------------------------------------------
    # Отправляем страницы
    # --------------------------------------------------------

    for index, page in enumerate(pages):

        line1, line2 = page


        print(
            f"[LCD PAGE {index + 1}/{len(pages)}]"
        )


        send_lcd_packet(
            line1,
            line2
        )


        if index + 1 < len(pages):

            time.sleep(
                1.5
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
# ОЖИДАНИЕ ДЖАРВИС
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


                # Для команды "выведи на экран"
                # текст уже отправлен на LCD.

                if extract_screen_text(
                    command
                ) is None:

                    lcd_answer(
                        answer
                    )


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


    first_start_setup()


    print("""
============================
 AI VOICE ASSISTANT PRO
============================
    """)


    connect_arduino()


    open_hud()


    send_lcd(
        "",
        ""
    )


    speak(
        "Ассистент запущен"
    )


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


    voice_loop()


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