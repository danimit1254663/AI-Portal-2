import os
import shutil
import subprocess
from pathlib import Path


HOME = Path.home()


pending_delete = None



SEARCH_DIRS = [

    HOME / "Desktop",
    HOME / "Documents",
    HOME / "Downloads",
    HOME / "Music",
    HOME / "Pictures"

]



# =====================================
# ПОИСК
# =====================================

def find_files(text):


    query=text.lower()


    if "найди" not in query:

        return None



    query=query.replace(
        "найди",
        ""
    )


    query=query.replace(
        "файл",
        ""
    )


    query=query.strip()



    if not query:

        return None



    results=[]


    for folder in SEARCH_DIRS:


        if folder.exists():


            for file in folder.rglob("*"):


                if file.is_file():


                    if query in file.name.lower():

                        results.append(file)



                        if len(results)>=5:

                            break



    if results:


        return (

            "Нашёл: "

            +

            ", ".join(

                x.name

                for x in results

            )

        )



    return "Файл не найден"





# =====================================
# ОТКРЫТЬ ФАЙЛ
# =====================================


def open_file(text):


    if "открой файл" not in text:

        return None



    name=text.split(

        "открой файл",

        1

    )[1].strip()



    for folder in SEARCH_DIRS:


        if folder.exists():


            for file in folder.rglob("*"):


                if file.is_file() and name in file.name.lower():


                    subprocess.Popen(

                        [
                            "start",
                            "",
                            str(file)

                        ],

                        shell=True

                    )


                    return (

                        "Открываю "

                        +

                        file.name

                    )


    return "Файл не найден"





# =====================================
# УДАЛЕНИЕ С ПОДТВЕРЖДЕНИЕМ
# =====================================


def delete_file(text):

    global pending_delete



    if (

        "да" in text

        and

        pending_delete

    ):


        try:

            pending_delete.unlink()


            name=pending_delete.name


            pending_delete=None


            return (

                "Удалил файл "

                +

                name

            )


        except:


            pending_delete=None


            return "Не удалось удалить"



    if "удали файл" not in text:

        return None



    name=text.split(

        "удали файл",

        1

    )[1].strip()



    for folder in SEARCH_DIRS:


        if folder.exists():


            for file in folder.rglob("*"):


                if file.is_file() and name in file.name.lower():


                    pending_delete=file


                    return (

                        "Нашёл "

                        +

                        file.name

                        +

                        ". Подтвердите удаление"

                    )



    return "Файл не найден"





# =====================================
# КОРЗИНА
# =====================================


def empty_bin(text):


    if "очисти корзину" in text:


        os.system(

            "PowerShell.exe -command Clear-RecycleBin -Force"

        )


        return "Корзина очищена"



    return None





# =====================================
# КОПИРОВАНИЕ
# =====================================


def copy_file(text):


    if "скопируй файл" not in text:

        return None



    return (

        "Функция копирования готова. "

        "Добавим выбор места назначения"

    )





# =====================================
# ГЛАВНЫЙ РОУТЕР
# =====================================


def file_command(text):


    commands=[

        find_files,

        open_file,

        delete_file,

        empty_bin,

        copy_file

    ]


    for cmd in commands:


        result=cmd(text)


        if result:

            return result



    return None