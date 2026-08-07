import os
import telebot
from dotenv import load_dotenv
from ai.giga import GigaAI
from commands.windows import windows_command

load_dotenv()

token = os.getenv("Telegram_CREDENTIALS")
if not token:
    raise ValueError("Токен не найден! Проверь файл .env и переменную Telegram_CREDENTIALS.")

bot = telebot.TeleBot(token)

PASSWORD = "12546633"  # Лучше вынести в .env, но пока оставим так для наглядности


@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(
        message.chat.id,
        "Здравствуйте, Сэр!\n\n"
        "Доступные команды:\n"
        "- «Джарвис» — приветствие и подсказки\n"
        "- «Джарвис узнай <вопрос>» — спросить ИИ\n"
        "- «Джарвис выключи комп» — запрос на выключение (нужен пароль)\n"
    )


@bot.message_handler(func=lambda m: True)
def handle(message):
    text = message.text.strip().lower()

    # 1. Просто «джарвис»
    if text == "джарвис":
        bot.send_message(
            message.chat.id,
            "Да, Сэр!\nНапишите:\n- «Джарвис узнай <вопрос>», чтобы спросить ИИ\n- «Джарвис выключи комп», чтобы выключить компьютер (нужен пароль)"
        )
        return

    # 2. Запрос к ИИ
    if text.startswith("джарвис узнай"):
        question = text.replace("джарвис узнай", "", 1).strip()
        if not question:
            bot.send_message(message.chat.id, "После «Джарвис узнай» нет вопроса. Напишите вопрос.")
            return

        try:
            ai = GigaAI()
            answer = ai.ask(question)
            bot.send_message(message.chat.id, answer)
        except Exception as e:
            bot.send_message(message.chat.id, f"Ошибка при запросе к ИИ: {e}")
        return

    # 3. Выключение компьютера
    if text == "джарвис выключи комп":
        bot.send_message(message.chat.id, "Введите ключ доступа для выключения компьютера:")
        bot.register_next_step_handler(message, check_shutdown_password)
        return

    # 4. Любая другая команда с «джарвис» (например, «джарвис открой блокнот»)
    if text.startswith("джарвис "):
        command_text = text.replace("джарвис", "", 1).strip()
        bot.send_message(message.chat.id, "Введите ключ доступа для выполнения команды:")
        # Сохраняем команду в сообщение, чтобы передать дальше
        message.custom_command = command_text
        bot.register_next_step_handler(message, check_windows_password)
        return


def check_shutdown_password(message):
    if message.text == PASSWORD:
        bot.send_message(message.chat.id, "Компьютер будет выключен через 5 секунд. Отмена невозможна.")
        os.system("shutdown /s /t 5")
    else:
        bot.send_message(message.chat.id, "Неверный ключ доступа.")


def check_windows_password(message):
    # Получаем сохранённую команду
    command_text = getattr(message, "custom_command", None)
    if not command_text:
        bot.send_message(message.chat.id, "Ошибка: команда не сохранена.")
        return

    if message.text == PASSWORD:
        try:
            # windows_command должен принимать строку, а не message
            result = windows_command(command_text)
            bot.send_message(message.chat.id, result)
        except Exception as e:
            bot.send_message(message.chat.id, f"Ошибка выполнения команды: {e}")
    else:
        bot.send_message(message.chat.id, "Неверный ключ доступа.")


def Tg_bot():
    print("Telegram бот запущен")
    bot.infinity_polling(skip_pending=True)


if __name__ == "__main__":
    Tg_bot()
