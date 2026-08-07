# telegram_bot.py
import os
import telebot
from dotenv import load_dotenv
from ai.giga_ai import GigaAI
from commands.windows import windows_command
from ai.memory import remember

load_dotenv()

token = os.getenv("Telegram_CREDENTIALS")
if not token:
    raise ValueError("Токен не найден! Проверь .env (Telegram_CREDENTIALS)")

password = os.getenv("SHUTDOWN_PASSWORD")
if not password:
    # Если пароля нет, ставим заглушку, чтобы бот не падал
    password = "NO_PASSWORD_SET"
    print("⚠️ ВНИМАНИЕ: SHUTDOWN_PASSWORD не задан в .env!")

bot = telebot.TeleBot(token)
ai = GigaAI()

@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(
        message.chat.id,
        "Я здесь, Сэр!\n\n"
        "Теперь для ЛЮБОЙ команды нужен пароль.\n"
        "Напиши пароль — и дальше сможешь отправлять любые команды."
    )

# Состояние: ждём пароль или уже авторизован
user_state = {}  # chat_id -> "waiting_password" / "authorized"

@bot.message_handler(func=lambda m: True)
def handle_message(message):
    chat_id = message.chat.id
    text = message.text.strip().lower()

    # Инициализация состояния
    if chat_id not in user_state:
        user_state[chat_id] = "waiting_password"
        bot.send_message(chat_id, "Введите пароль для доступа к ассистенту:")
        return

    # Если ждём пароль
    if user_state[chat_id] == "waiting_password":
        if text == password:
            user_state[chat_id] = "authorized"
            bot.send_message(chat_id, "✅ Доступ разрешён. Теперь можно отправлять любые команды.")
            return
        else:
            bot.send_message(chat_id, "❌ Неверный пароль. Попробуйте ещё раз.")
            return

    # Если уже авторизован — обрабатываем команды
    triggers = ["джарвис", "ассистент"]
    clean_text = text
    for t in triggers:
        clean_text = clean_text.replace(t, "").strip()

    if not clean_text:
        bot.send_message(chat_id, "Слушаю, Сэр.")
        return

    # Сначала проверяем, не является ли команда опасной (для единообразия логики)
    danger_res = windows_command(clean_text)

    # В текущей версии windows_command опасные команды возвращают маркеры
    # Но даже если они их выполнят, у нас уже есть авторизация — так что всё ок.
    if danger_res == "__SHUTDOWN_REQUEST__":
        bot.send_message(chat_id, "Выключение через 5 секунд… Отмена невозможна.")
        os.system("shutdown /s /t 5")
        return
    elif danger_res == "__REBOOT_REQUEST__":
        bot.send_message(chat_id, "Перезагрузка через 5 секунд.")
        os.system("shutdown /r /t 5")
        return

    # Обычные команды
    if clean_text.startswith("узнай "):
        question = clean_text.replace("узнай ", "", 1).strip()
        if not question:
            bot.send_message(chat_id, "Что нужно узнать? Напиши после «узнай».")
            return
        try:
            answer = ai.ask(question)
            bot.send_message(chat_id, answer)
        except Exception as e:
            bot.send_message(chat_id, f"Ошибка ИИ: {e}")
        return

    mem = remember(clean_text)
    if mem:
        bot.send_message(chat_id, mem)
        return

    res = windows_command(clean_text)
    if res:
        # Если windows_command вернул текст (не маркер выключения) — отправляем
        # Маркеры выключения мы уже обработали выше
        if res not in ("__SHUTDOWN_REQUEST__", "__REBOOT_REQUEST__"):
            bot.send_message(chat_id, res)
        return

    # Если ничего не подошло — в ИИ
    try:
        answer = ai.ask(clean_text)
        bot.send_message(chat_id, answer)
    except Exception as e:
        bot.send_message(chat_id, str(e))


if __name__ == "__main__":
    print("Telegram бот запущен (все команды требуют пароль)...")
    bot.infinity_polling(skip_pending=True, timeout=30, long_polling_timeout=40)
