import os
from dotenv import load_dotenv
import telebot
from ai.giga import GigaAI

load_dotenv()
def Tg_bot:
    token = os.getenv("Telegram_CREDENTIALS")
    if not token:
        raise ValueError("Токен не найден! Проверь файл .env и переменную Telegram_CREDENTIALS.")

    bot = telebot.TeleBot(token)

    @bot.message_handler(commands=["start"])
    def start(message):
        bot.send_message(message.chat.id, "Здравствуйте, Сэр!")

    @bot.message_handler(content_types=["text"])
    def handle_text(message):
        text = message.text.strip().lower()

    # Вариант 1: просто «джарвис»
        if text == "джарвис":
            bot.send_message(message.chat.id, "Да, Сэр!")
            bot.send_message(
            message.chat.id,
            "Если хотите что-то спросить, просто скажите: «Джарвис узнай <вопрос>»"
        )
            return  # чтобы не идти дальше

    # Вариант 2: «джарвис узнай …»
        if text.startswith("джарвис узнай"):
            bot.send_message(message.chat.id, "Да, Сэр! Сейчас узнаю…")

        # Извлекаем сам вопрос (убираем «джарвис узнай»)
            question = text.replace("джарвис узнай", "", 1).strip()
            if not question:
                bot.send_message(message.chat.id, "Сэр, вы не задали вопрос после «Джарвис узнай».")
                return

             try:
                ai = GigaAI()
                answer = ai.ask(question)  # убедись, что ask принимает именно строку
                response = f"Надеюсь, я помог, Сэр. Jarvis:\n{answer}"
                bot.send_message(message.chat.id, response)
            except Exception as e:

        if text.startswith("джарвис выключи комп"):
            bot.send_message(message.chat.id, "Да, Сэр! Сейчас")

            os.system(
                "shutdown /s /t 5"
            )

    bot.infinity_polling()
