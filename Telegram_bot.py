import os
from dotenv import load_dotenv
import telebot
from ai.giga import GigaAI

load_dotenv()


def Tg_bot():
    token = os.getenv("Telegram_CREDENTIALS")
    if not token:
        raise ValueError("Не найден Telegram_CREDENTIALS")

    bot = telebot.TeleBot(token)

    @bot.message_handler(commands=["start"])
    def start(message):
        bot.send_message(message.chat.id, "Здравствуйте, Сэр!")

    @bot.message_handler(content_types=["text"])
    def handle_text(message):
        text = message.text.strip().lower()

        # Просто Джарвис
        if text == "джарвис":
            bot.send_message(
                message.chat.id,
                "Да, Сэр!\nНапишите:\nДжарвис узнай <вопрос>"
            )
            return

        # Вопрос ИИ
        if text.startswith("джарвис узнай"):
            question = text.replace("джарвис узнай", "", 1).strip()

            if not question:
                bot.send_message(message.chat.id, "После команды нет вопроса.")
                return

            bot.send_message(message.chat.id, "Да, Сэр! Сейчас узнаю...")

            try:
                ai = GigaAI()
                answer = ai.ask(question)
                bot.send_message(message.chat.id, answer)
            except Exception as e:
                bot.send_message(message.chat.id, str(e))

            return

        # Выключение ПК
        if text == "джарвис выключи комп":
            msg = bot.send_message(
                message.chat.id,
                "Введите ключ доступа:"
            )

            bot.register_next_step_handler(msg, check_password)
            return

    def check_password(message):
        password = message.text.strip()

        if password == "12546633":
            bot.send_message(message.chat.id, "Ключ принят. Выключаю компьютер.")
            os.system("shutdown /s /t 5")
        else:
            bot.send_message(message.chat.id, "Неверный ключ доступа.")

    bot.infinity_polling(skip_pending=True)