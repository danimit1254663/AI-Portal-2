import os
import sys
import tempfile

import telebot
from dotenv import load_dotenv
from ai.giga import GigaAI
from commands.windows import windows_command
from ai.memory import remember
from telebot import types


# ============================================================
# НАСТРОЙКИ
# ============================================================

load_dotenv()

TOKEN = os.getenv("Telegram_CREDENTIALS")

if not TOKEN:
    raise ValueError(
        "Токен не найден! Проверь .env (Telegram_CREDENTIALS)"
    )

# Лучше хранить пароль в .env:
#
# BOT_PASSWORD=12546633
#
# Если его нет, используется пароль ниже.
PASSWORD = os.getenv(
    "BOT_PASSWORD",
    "12546633"
)

bot = telebot.TeleBot(TOKEN)
ai = GigaAI()


# ============================================================
# СОСТОЯНИЕ
# ============================================================

# Авторизованные пользователи
# chat_id -> True
authorized_users = {}

# Пользователь вызвал /key и теперь должен ввести пароль
# chat_id -> True
waiting_for_password = {}

# Пользователь нажал "Спросить у Джарвиса"
# chat_id -> True
waiting_for_question = {}

# ID сообщений, отправленных ботом
# Используются для попытки очистки истории при /logout
bot_messages = {}


# ============================================================
# ОТПРАВКА СООБЩЕНИЙ
# ============================================================

def save_bot_message(chat_id, message):
    """
    Запоминает ID сообщения бота.
    """

    try:
        if chat_id not in bot_messages:
            bot_messages[chat_id] = []

        bot_messages[chat_id].append(
            message.message_id
        )

        # Не храним бесконечную историю
        if len(bot_messages[chat_id]) > 100:
            bot_messages[chat_id] = (
                bot_messages[chat_id][-100:]
            )

    except Exception:
        pass


def send_message(chat_id, text, **kwargs):
    """
    Отправляет сообщение и сохраняет его ID.
    """

    message = bot.send_message(
        chat_id,
        text,
        **kwargs
    )

    save_bot_message(
        chat_id,
        message
    )

    return message


# ============================================================
# ПРОВЕРКА АВТОРИЗАЦИИ
# ============================================================

def is_authorized(chat_id):
    return authorized_users.get(
        chat_id,
        False
    ) is True


# ============================================================
# ОЧИСТКА СОСТОЯНИЯ
# ============================================================

def clear_user_state(chat_id):
    """
    Полностью очищает локальное состояние пользователя.
    """

    authorized_users.pop(
        chat_id,
        None
    )

    waiting_for_password.pop(
        chat_id,
        None
    )

    waiting_for_question.pop(
        chat_id,
        None
    )


# ============================================================
# ОЧИСТКА ИСТОРИИ БОТА
# ============================================================

def clear_bot_history(chat_id):
    """
    Пытается удалить сообщения, которые бот отправлял
    и ID которых он сохранил.

    Telegram не во всех типах чатов позволяет боту
    удалять любые сообщения.
    """

    message_ids = bot_messages.get(
        chat_id,
        []
    )

    for message_id in message_ids:

        try:
            bot.delete_message(
                chat_id,
                message_id
            )

        except Exception:
            # Например, сообщение уже удалено
            # или Telegram не разрешил его удалить.
            pass

    bot_messages.pop(
        chat_id,
        None
    )


def logout_user(chat_id):
    """
    Закрывает доступ и очищает локальное состояние.
    """

    clear_user_state(
        chat_id
    )

    clear_bot_history(
        chat_id
    )


# ============================================================
# СКРИНШОТ
# ============================================================

def send_screenshot(chat_id):
    """
    Делает временный скриншот экрана,
    отправляет его в Telegram,
    затем удаляет файл с компьютера.
    """

    screenshot_path = None

    try:

        import pyautogui

        # Создаём временный файл
        fd, screenshot_path = tempfile.mkstemp(
            suffix=".png",
            prefix="jarvis_screen_"
        )

        os.close(fd)

        # Делаем скриншот
        screenshot = pyautogui.screenshot()

        screenshot.save(
            screenshot_path
        )

        # Отправляем в Telegram
        with open(
            screenshot_path,
            "rb"
        ) as photo:

            message = bot.send_photo(
                chat_id,
                photo,
                caption="🖥 Скриншот после выполнения команды."
            )

            save_bot_message(
                chat_id,
                message
            )

    except ImportError:

        send_message(
            chat_id,
            "⚠️ Для скриншотов установи pyautogui:\n\n"
            "pip install pyautogui"
        )

    except Exception as e:

        send_message(
            chat_id,
            f"⚠️ Ошибка создания скриншота:\n{e}"
        )

    finally:

        # ВАЖНО:
        # после отправки удаляем файл с компьютера
        if screenshot_path:

            try:

                if os.path.exists(
                    screenshot_path
                ):
                    os.remove(
                        screenshot_path
                    )

            except Exception:
                pass


# ============================================================
# /START
# ============================================================

@bot.message_handler(commands=["start"])
def start(message):

    chat_id = message.chat.id

    markup = types.ReplyKeyboardMarkup(
        resize_keyboard=True
    )

    button_ask = types.KeyboardButton(
        "Спросить у Джарвиса информацию"
    )

    button_date = types.KeyboardButton(
        "Дата"
    )

    button_time = types.KeyboardButton(
        "Время"
    )

    button_commands = types.KeyboardButton(
        "Список команд"
    )

    markup.add(
        button_ask,
        button_date,
        button_time,
        button_commands
    )

    send_message(
        chat_id,
        "🤖 Я здесь, Сэр!\n\n",
        reply_markup=markup
    )


# ============================================================
# /KEY
# ============================================================

@bot.message_handler(commands=["key"])
def key_command(message):

    chat_id = message.chat.id

    if is_authorized(chat_id):

        send_message(
            chat_id,
            "🔓 Доступ уже открыт."
        )

        return

    waiting_for_password[chat_id] = True

    send_message(
        chat_id,
        "🔐 Запрос доступа.\n\n"
        "Введите пароль.\n\n"
        "⚠️ После выполнения /logout доступ будет закрыт, "
        "а сохранённое состояние текущего сеанса будет очищено."
    )


# ============================================================
# /LOGOUT
# ============================================================

@bot.message_handler(commands=["logout"])
def logout_command(message):

    chat_id = message.chat.id

    if not is_authorized(chat_id):

        clear_user_state(
            chat_id
        )

        send_message(
            chat_id,
            "🔒 Доступ уже закрыт."
        )

        return

    # Сначала сообщаем пользователю
    send_message(
        chat_id,
        "🔒 Закрываю доступ...\n"
        "Состояние текущего сеанса будет очищено."
    )

    # Затем очищаем всё
    logout_user(
        chat_id
    )


# ============================================================
# СПИСОК КОМАНД
# ============================================================

def show_commands(chat_id):

    send_message(
        chat_id,

        "📋 СПИСОК КОМАНД\n\n"

       
        "• Спросить у Джарвиса информацию\n"
        "• Дата\n"
        "• Время\n"
        "• Список команд\n\n"
    )


# ============================================================
# ОСНОВНОЙ ОБРАБОТЧИК
# ============================================================

@bot.message_handler(func=lambda message: True)
def handle_message(message):

    chat_id = message.chat.id

    # Нормализация текста
    text = (
        message.text or ""
    ).replace(
        "\xa0",
        " "
    ).strip()

    text_lower = " ".join(
        text.lower().split()
    )


    # ========================================================
    # ПОЛЬЗОВАТЕЛЬ ВВОДИТ ПАРОЛЬ
    # ========================================================

    if waiting_for_password.get(chat_id):

        if text == PASSWORD:

            waiting_for_password.pop(
                chat_id,
                None
            )

            authorized_users[chat_id] = True

            send_message(
                chat_id,
                "✅ Пароль верный!\n\n"
                "🔓 Доступ разрешён.\n"
                "Теперь доступны команды управления компьютером."
            )

        else:

            waiting_for_password.pop(
                chat_id,
                None
            )

            send_message(
                chat_id,
                "❌ Неверный пароль.\n\n"
            )

        return


    # ========================================================
    # СПРОСИТЬ У ДЖАРВИСА
    # БЕЗ ПАРОЛЯ
    # ========================================================

    ask_buttons = {
        "спросить у джарвиса информацию",
        "спросить у джарвиса инфорамцию",
    }

    if text_lower in ask_buttons:

        waiting_for_question[chat_id] = True

        send_message(
            chat_id,
            "🤖 Что вас интересует, Сэр?\n\n"
            "Отправьте вопрос следующим сообщением.\n"
            "🔓 Пароль для этого не требуется."
        )

        return


    # ========================================================
    # ВОПРОС ДЖАРВИСУ
    # БЕЗ ПАРОЛЯ
    # ========================================================

    if waiting_for_question.get(chat_id):

        waiting_for_question[chat_id] = False

        try:

            send_message(
                chat_id,
                "🤖 Запрос обрабатывается Джарвисом..."
            )

            answer = ai.ask(
                text
            )

            send_message(
                chat_id,
                answer
            )

        except Exception as e:

            send_message(
                chat_id,
                f"❌ Ошибка ИИ:\n{e}"
            )

        return


    # ========================================================
    # ДАТА
    # БЕЗ ПАРОЛЯ
    # ========================================================

    if text_lower == "дата":

        result = windows_command(
            "какая дата"
        )

        send_message(
            chat_id,
            result if result else
            "Не удалось получить дату."
        )

        return


    # ========================================================
    # ВРЕМЯ
    # БЕЗ ПАРОЛЯ
    # ========================================================

    if text_lower == "время":

        result = windows_command(
            "который час"
        )

        send_message(
            chat_id,
            result if result else
            "Не удалось получить время."
        )

        return


    # ========================================================
    # СПИСОК КОМАНД
    # БЕЗ ПАРОЛЯ
    # ========================================================

    if text_lower == "список команд":

        show_commands(
            chat_id
        )

        return


    # ========================================================
    # ВСЁ ОСТАЛЬНОЕ ТРЕБУЕТ /KEY
    # ========================================================

    if not is_authorized(chat_id):

        send_message(
            chat_id,
            "❌ Команды нет.\n\n"
            "Эта команда требует доступа.\n"
        )

        return


    # ========================================================
    # ОЧИЩАЕМ "ДЖАРВИС" / "АССИСТЕНТ"
    # ========================================================

    clean_text = text_lower

    for trigger in (
        "джарвис",
        "ассистент"
    ):

        clean_text = clean_text.replace(
            trigger,
            ""
        ).strip()


    # ========================================================
    # ВЫКЛЮЧЕНИЕ ПК
    # ========================================================

    shutdown_commands = {
        "выключить пк",
        "выключи пк",
        "выключить компьютер",
        "выключи компьютер",
        "shutdown"
    }

    if clean_text in shutdown_commands:

        send_message(
            chat_id,
            "⚠️ Выключение компьютера через 5 секунд..."
        )

        # Скриншот ДО выключения
        send_screenshot(
            chat_id
        )

        os.system(
            "shutdown /s /t 5"
        )

        return


    # ========================================================
    # ПЕРЕЗАГРУЗКА ПК
    # ========================================================

    reboot_commands = {
        "перезагрузить пк",
        "перезагрузи пк",
        "перезагрузка пк",
        "перезагрузить компьютер",
        "перезагрузи компьютер",
        "reboot"
    }

    if clean_text in reboot_commands:

        send_message(
            chat_id,
            "🔄 Перезагрузка компьютера через 5 секунд..."
        )

        # Скриншот ДО перезагрузки
        send_screenshot(
            chat_id
        )

        os.system(
            "shutdown /r /t 5"
        )

        return


    # ========================================================
    # БЛОКИРОВКА ЭКРАНА
    # ========================================================

    lock_commands = {
        "заблокировать экран",
        "заблокируй экран",
        "блокировка экрана",
        "заблокировать компьютер",
        "заблокируй компьютер",
        "lock"
    }

    if clean_text in lock_commands:

        send_message(
            chat_id,
            "🔒 Блокирую экран..."
        )

        # До блокировки
        send_screenshot(
            chat_id
        )

        os.system(
            "rundll32.exe "
            "user32.dll,LockWorkStation"
        )

        return


    # ========================================================
    # "УЗНАЙ"
    # ========================================================

    if clean_text.startswith(
        "узнай "
    ):

        question = text[
            text_lower.find(
                "узнай "
            ) + 6:
        ].strip()

        if not question:

            send_message(
                chat_id,
                "❓ Что нужно узнать?"
            )

            return

        try:

            send_message(
                chat_id,
                "🤖 Запрос обрабатывается..."
            )

            answer = ai.ask(
                question
            )

            send_message(
                chat_id,
                answer
            )

            # После защищённой команды
            send_screenshot(
                chat_id
            )

        except Exception as e:

            send_message(
                chat_id,
                f"❌ Ошибка ИИ:\n{e}"
            )

        return


    # ========================================================
    # MEMORY
    # ========================================================

    memory_result = remember(
        clean_text
    )

    if memory_result:

        send_message(
            chat_id,
            memory_result
        )

        send_screenshot(
            chat_id
        )

        return


    # ========================================================
    # WINDOWS COMMAND
    # ========================================================

    result = windows_command(
        clean_text
    )

    if result:

        # Выключение
        if result == "__SHUTDOWN_REQUEST__":

            send_message(
                chat_id,
                "⚠️ Выключение компьютера через 5 секунд..."
            )

            send_screenshot(
                chat_id
            )

            os.system(
                "shutdown /s /t 5"
            )

            return


        # Перезагрузка
        if result == "__REBOOT_REQUEST__":

            send_message(
                chat_id,
                "🔄 Перезагрузка компьютера через 5 секунд..."
            )

            send_screenshot(
                chat_id
            )

            os.system(
                "shutdown /r /t 5"
            )

            return


        send_message(
            chat_id,
            result
        )

        send_screenshot(
            chat_id
        )

        return


    # ========================================================
    # НЕИЗВЕСТНАЯ КОМАНДА -> ИИ
    # ========================================================

    try:

        answer = ai.ask(
            text
        )

        send_message(
            chat_id,
            answer
        )

        send_screenshot(
            chat_id
        )

    except Exception as e:

        send_message(
            chat_id,
            f"❌ Ошибка ИИ:\n{e}"
        )


# ============================================================
# ПОДТВЕРЖДЕНИЕ ЗАПУСКА В КОНСОЛИ
# ============================================================

def ask_start():

    print()
    print("=" * 55)
    print("              JARVIS TELEGRAM BOT")
    print("=" * 55)
    print()
    print("Запустить Telegram-бота?")
    print()
    print("  [Y] / [Д]  — запустить")
    print("  [N] / [Н]  — выйти")
    print()

    while True:

        answer = input(
            "Ваш выбор: "
        ).strip().lower()

        if answer in (
            "y",
            "yes",
            "д",
            "да"
        ):

            return True

        if answer in (
            "n",
            "no",
            "н",
            "нет"
        ):

            return False

        print(
            "Введите Y/Д для запуска "
            "или N/Н для выхода."
        )


# ============================================================
# ЗАПУСК БОТА
# ============================================================

def Tg_bot():

    print()
    print("Telegram-бот запускается...")
    print("Кнопки меню работают без пароля.")
    print("Для управления ПК используется /key.")
    print()

    try:

        bot.infinity_polling(
            skip_pending=True,
            timeout=30,
            long_polling_timeout=40
        )

    except KeyboardInterrupt:

        print()
        print("Бот остановлен.")

    except Exception as e:

        print()
        print(
            f"Критическая ошибка бота: {e}"
        )


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    if ask_start():

        Tg_bot()

    else:

        print()
        print("Бот не запущен.")
        print("Программа завершена.")
        print()

        sys.exit(0)