# main.py
import time
import logging
import traceback
import os
import sys
import threading
from dotenv import load_dotenv

# Импорты компонентов
from core.config import first_start_setup, config
from ui.hud import open_hud, hide_hud, set_status, set_command, set_answer
from voice.vosk_engine import listen
from voice.tts import speak
import core.state as state

from ai.giga import GigaAI
from ai.memory import remember
from commands.windows import windows_command
from commands.time_control import get_time

# ИМПОРТ БОТА (функция Tg_bot из telegram_bot.py)
from Telegram_bot import Tg_bot

# Настройка логирования
logging.basicConfig(
    filename="assistant.log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)

load_dotenv()
assistant_running = True
ai = GigaAI()
SESSION_TIME = 15


def process_command(text):
    """Единая логика обработки команд для голоса"""
    if not text:
        return None

    # Память
    mem = remember(text)
    if mem:
        return mem

    # Управление сном
    if "сон" in text or "усни" in text:
        state.microphone_enabled = False
        return "Перехожу в режим сна"

    if "проснись" in text:
        state.microphone_enabled = True
        return "Микрофон включен"

    # HUD
    if "спрячься" in text or "скройся" in text or "убери интерфейс" in text:
        hide_hud()
        return "Интерфейс скрыт"

    # Время
    time_res = get_time(text)
    if time_res:
        return time_res

    # Windows команды
    win_res = windows_command(text)
    if win_res!="__SHUTDOWN_REQUEST__"or "__REBOOT_REQUEST__":
        return win_res
    elif win_res!="__SHUTDOWN_REQUEST__":
        os.system("shutdown /s /t 5")
        speak('Выключаюсь')
    elif win_res!="__REBOOT_REQUEST__":
        os.system("shutdown /r /t 5")
        speak('Перезапуск')
    # AI
    return ai.ask(text)


def wait_activation():
    """Ждёт фразы активации ('Джарвис')"""
    while assistant_running:
        text = listen()
        if not text:
            continue

        print(f"HEARD: {text}")
        triggers = config.get("activation", ["джарвис", "ассистент"])

        for trigger in triggers:
            if trigger in text:
                # Удаляем триггер и возвращаем чистую команду
                command = text.replace(trigger, "", 1).strip()
                return command
    return None


def voice_loop():
    global assistant_running
    print("\n======================\n JARVIS READY \n Скажите Джарвис \n======================")

    while assistant_running:
        try:
            command = wait_activation()
            if command is None:
                continue

            # Если сказали просто "Джарвис"
            if command == "":
                speak("Слушаю")
                command = listen()
                if not command:
                    continue

            print(f"COMMAND: {command}")

            if command in ["стоп", "выход", "закройся"]:
                speak("Завершаю работу")
                assistant_running = False
                break

            answer = process_command(command)

            if answer:
                set_command(command)
                set_answer(answer)
                speak(answer)

        except Exception as e:
            logging.error(f"Voice Loop Error: {e}")
            traceback.print_exc()


def run_telegram_bot():
    """Функция-обёртка для запуска бота в отдельном потоке"""
    try:
        print("Запуск Telegram бота...")
        Tg_bot()  # Эта функция содержит infinity_polling(), она будет работать вечно
    except Exception as e:
        logging.critical(f"Ошибка Telegram бота: {e}")
        traceback.print_exc()


def main():
    first_start_setup()
    print("""
============================
 AI VOICE ASSISTANT PRO
============================
    """)

    open_hud()
    speak("Ассистент запущен")

    # --- ЗАПУСК В РАЗНЫХ ПОТОКАХ ---

    # 1. Создаём поток для Telegram бота
  #  tg_thread = threading.Thread(target=run_telegram_bot, daemon=True)
   # tg_thread.start()

    # Небольшая пауза, чтобы бот успел инициализироваться
    time.sleep(2)

    # 2. Запускаем голосовой цикл в главном потоке
    voice_loop()

    print("Ассистент остановлен.")


if __name__ == "__main__":
    main()
