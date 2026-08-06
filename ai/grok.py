from openai import OpenAI
import os


class GrokAI:

    def __init__(self):

        self.client = OpenAI(
            api_key=os.getenv(
                "XAI_API_KEY"
            ),
            base_url="https://api.x.ai/v1"
        )


    def ask(self, text):

        response = self.client.chat.completions.create(

            model="grok-3-mini",

            messages=[
                {
                    "role":"user",
                    "content":text
                }
            ]

        )

        return response.choices[0].message.content