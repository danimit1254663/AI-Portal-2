import requests
import subprocess
import shutil
import os


class LocalAI:


    def __init__(self):

        self.model = "qwen2.5:7b"

        self.check_ollama()



    def check_ollama(self):

        ollama = shutil.which(
            "ollama"
        )


        if not ollama:

            print(
                "Ollama не найден"
            )

            return False


        print(
            "Ollama найден"
        )

        return True




    def ask(self, text):


        try:


            response = requests.post(

                "http://localhost:11434/api/generate",

                json={

                    "model": self.model,

                    "prompt": text,

                    "stream": False

                },

                timeout=120

            )


            data = response.json()


            return data.get(

                "response",

                "Нет ответа"

            )


        except Exception as e:


            print(
                "Ollama ошибка:",
                e
            )


            raise e