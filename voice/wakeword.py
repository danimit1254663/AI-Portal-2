from core.config import config
from core.state import activate



def check(text):

    triggers=config.get(
        "activation",
        [
            "джарвис"
        ]
    )


    for word in triggers:

        if word in text.lower():

            activate(10)

            command=text.replace(
                word,
                ""
            ).strip()


            return command


    return None