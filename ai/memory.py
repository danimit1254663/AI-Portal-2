
import json

from pathlib import Path



BASE_DIR = Path.cwd()

DATA_DIR = BASE_DIR / "data"

DATA_DIR.mkdir(
    exist_ok=True
)


MEMORY_FILE = DATA_DIR / "memory.json"



memory = {


    "user": {

        "name": ""

    },


    "history": []

}




def load_memory():

    global memory


    if not MEMORY_FILE.exists():

        save_memory()

        return



    try:

        with open(

            MEMORY_FILE,

            "r",

            encoding="utf-8"

        ) as f:


            memory = json.load(f)



    except:


        memory = {

            "user": {

                "name": ""

            },

            "history": []

        }





def save_memory():


    with open(

        MEMORY_FILE,

        "w",

        encoding="utf-8"

    ) as f:


        json.dump(

            memory,

            f,

            indent=4,

            ensure_ascii=False

        )





def remember(text):

    text=text.lower()



    if "меня зовут" in text:


        name=text.split(

            "меня зовут",

            1

        )[1].strip()



        if name:


            memory["name"]=name

            save_memory()


            return (

                "Запомнил ваше имя "

                + name

            )




    if "запомни" in text:


        fact=text.split(

            "запомни",

            1

        )[1].strip()



        if fact:


            memory.setdefault(

                "facts",

                []

            )


            memory["facts"].append(

                fact

            )


            save_memory()



            return "Запомнил"



    if "забудь" in text:


        fact=text.split(

            "забудь",

            1

        )[1].strip()



        if fact in memory.get(

            "facts",

            []

        ):


            memory["facts"].remove(

                fact

            )


            save_memory()


            return "Забыл"



    return None


def add_history(role, text):


    memory["history"].append(

        {

            "role": role,

            "content": text

        }

    )


    if len(memory["history"]) > 20:


        memory["history"] = memory["history"][-20:]



    save_memory()





def get_history():


    return memory["history"]





def context():


    result = []



    name = memory["user"].get(

        "name",

        ""

    )



    if name:


        result.append(

            "Имя пользователя: "

            +

            name

        )



    return "\n".join(result)





load_memory()

