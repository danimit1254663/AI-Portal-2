
from gigachat import GigaChat
import os

from ai.grok import GrokAI

from ai.memory import (
    add_history,
    get_history,
    context
)


class GigaAI:

    def __init__(self):

        # =====================
        # GIGACHAT
        # =====================

        try:

            key = os.getenv(
                "GIGACHAT_CREDENTIALS"
            )

            if key:

                self.giga = GigaChat(
                    credentials=key,
                    model="GigaChat-2",
                    verify_ssl_certs=False
                )

                print("GigaChat готов")

            else:

                self.giga = None

                print("GigaChat ключ отсутствует")

        except Exception as e:

            print("GigaChat ошибка:", e)

            self.giga = None


        # =====================
        # GROK
        # =====================

        try:

            self.grok = GrokAI()

            print("Grok готов")

        except Exception as e:

            print("Grok отключён:", e)

            self.grok = None


    # =========================================================
    # ОГРАНИЧЕНИЕ ОТВЕТА
    # =========================================================

    def limit_answer(self, answer):

        if not answer:
            return ""

        answer = str(answer).strip()

        # Максимум примерно 500 символов.
        # Этого достаточно для нормального ответа JARVIS.
        if len(answer) > 500:

            answer = answer[:500]

            # Не обрываем слово
            last_space = answer.rfind(" ")

            if last_space > 200:
                answer = answer[:last_space]

            answer += "..."

        return answer


    # =========================================================
    # AI
    # =========================================================

    def ask(self, text):

        add_history(
            "user",
            text
        )


        # =====================================================
        # SYSTEM PROMPT
        # =====================================================

        system_prompt = """
Ты JARVIS — голосовой помощник.

Отвечай максимально кратко и естественно.

Правила:
1. Обычно отвечай 1-2 короткими предложениями.
2. Максимум 300 символов.
3. Не пиши длинные объяснения без просьбы пользователя.
4. Не используй списки, если они не нужны.
5. Не повторяй вопрос пользователя.
6. Отвечай по существу.
7. Ответ должен быть удобен для озвучивания голосом.
8. Если пользователь говорит "кратко" — ответь одним коротким предложением.
9. Не добавляй лишние приветствия и заключения.
10. Не объясняй очевидные вещи.

Ты работаешь как голосовой ассистент, поэтому лучше короткий ответ,
чем длинный текст.
"""


        messages = [

            {
                "role": "system",
                "content":
                    system_prompt
                    + "\n\n"
                    + context()
            }

        ]


        # =====================================================
        # ИСТОРИЯ
        # =====================================================

        for item in get_history():

            messages.append({

                "role": item["role"],
                "content": item["content"]

            })


        # =====================================================
        # GIGACHAT
        # =====================================================

        if self.giga:

            try:

                response = self.giga.chat({

                    "messages": messages

                })


                answer = response.choices[0].message.content

                answer = self.limit_answer(
                    answer
                )


                add_history(
                    "assistant",
                    answer
                )


                print(
                    "Ответ: GigaChat"
                )


                return answer


            except Exception as e:

                print(
                    "GigaChat недоступен:",
                    e
                )


        # =====================================================
        # GROK
        # =====================================================

        if self.grok:

            try:

                answer = self.grok.ask(
                    text
                )


                answer = self.limit_answer(
                    answer
                )


                add_history(
                    "assistant",
                    answer
                )


                print(
                    "Ответ: Grok"
                )


                return answer


            except Exception as e:

                print(
                    "Grok ошибка:",
                    e
                )


        # =====================================================
        # НЕТ AI
        # =====================================================


