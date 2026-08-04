
from gigachat import GigaChat

from core.config import get_gigachat_config

from ai.memory import (
    add_history,
    get_history,
    context
)



class GigaAI:

    def __init__(self):

        giga = get_gigachat_config()

        self.client = GigaChat(

            credentials=giga["credentials"],

            scope=giga["scope"],

            model=giga["model"],

            verify_ssl_certs=False

        )


    def ask(self, text):

        try:


            # сохраняем вопрос пользователя

            add_history(

                "user",

                text

            )



            messages = []



            system_text = (

                "Ты голосовой помощник Jarvis. "

                "Отвечай кратко и понятно. "

                "Используй информацию о пользователе.\n\n"

                +

                context()

            )



            messages.append(

                {

                    "role": "system",

                    "content": system_text

                }

            )



            for item in get_history():


                messages.append(

                    {

                        "role": item["role"],

                        "content": item["content"]

                    }

                )



            response = self.client.chat(

                {

                    "messages": messages

                }

            )



            answer = response.choices[0].message.content



            add_history(

                "assistant",

                answer

            )



            return answer



        except Exception as e:


            print(

                "GigaChat error:",

                e

            )


            return "Ошибка связи с искусственным интеллектом."

