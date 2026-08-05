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
                    credentials=os.getenv("GIGACHAT_CREDENTIALS"),
                    model="GigaChat-2",
                    verify_ssl_certs=False
                )

                print(
                    "GigaChat готов"
                )

            else:

                self.giga = None

                print(
                    "GigaChat ключ отсутствует"
                )


        except Exception as e:

            print(
                "GigaChat ошибка:",
                e
            )

            self.giga = None



        # =====================
        # GROK
        # =====================

        try:

            self.grok = GrokAI()

            print(
                "Grok готов"
            )


        except Exception as e:

            print(
                "Grok отключён:",
                e
            )

            self.grok = None






    def ask(self,text):


        add_history(
            "user",
            text
        )


        messages=[

            {
                "role":"system",

                "content":

                "Ты голосовой помощник Jarvis. "
                "Отвечай кратко и понятно.\n\n"

                +

                context()

            }

        ]


        for item in get_history():

            messages.append(

                {

                    "role":item["role"],

                    "content":item["content"]

                }

            )



        # =====================
        # 1 GIGACHAT
        # =====================

        if self.giga:


            try:

                response=self.giga.chat(

                    {
                        "messages":messages
                    }

                )


                answer=response.choices[0].message.content


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



        # =====================
        # 2 GROK
        # =====================

        if self.grok:


            try:

                answer=self.grok.ask(
                    text
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





        return "Все системы ИИ недоступны"