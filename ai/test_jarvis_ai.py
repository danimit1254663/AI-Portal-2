
from ai.giga import GigaAI


ai = GigaAI()



while True:


    text = input(

        "Ты: "

    )


    if text == "выход":

        break



    answer = ai.ask(

        text

    )


    print(

        "Jarvis:",

        answer

    )