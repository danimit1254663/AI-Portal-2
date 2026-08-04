import os
import json
import subprocess
import psutil
from core.language import normalize_text
from pathlib import Path



APP_FILE = Path("apps.json")



SEARCH_PATHS = [

    Path("C:/Program Files"),

    Path("C:/Program Files (x86)"),

    Path.home() / "AppData/Roaming",

    Path.home() / "AppData/Local"

]



apps = {}





# ==========================
# SAVE
# ==========================


def save_apps():

    with open(

        APP_FILE,

        "w",

        encoding="utf-8"

    ) as f:

        json.dump(

            apps,

            f,

            indent=4,

            ensure_ascii=False

        )





# ==========================
# SCAN
# ==========================


def scan_apps():


    global apps


    apps={}


    print(
        "Сканирование программ..."
    )


    for folder in SEARCH_PATHS:


        if not folder.exists():

            continue



        for root,dirs,files in os.walk(folder):


            for file in files:


                if file.lower().endswith(".exe"):


                    name=file[:-4].lower()


                    path=os.path.join(

                        root,

                        file

                    )



                    apps[name]=path




    save_apps()



    return (

        "Список программ обновлён. Найдено "

        + str(len(apps))

        + " программ"

    )






# ==========================
# LOAD
# ==========================


def load_apps():


    global apps


    if APP_FILE.exists():


        try:


            with open(

                APP_FILE,

                "r",

                encoding="utf-8"

            ) as f:


                apps=json.load(f)


        except:


            scan_apps()


    else:


        scan_apps()







# ==========================
# OPEN APP
# ==========================


def open_app(text):


    text=normalize_text(text)



    for name,path in apps.items():


        if name in text:


            try:


                subprocess.Popen(

                    path,

                    shell=True

                )


                return (

                    "Открываю "

                    + name

                )


            except:

                pass



    return None







# ==========================
# LIST APPS
# ==========================


def list_apps(text):


    if (

        "какие программы" in text

        or

        "список программ" in text

    ):


        count=len(apps)


        return (

            "У меня в базе "

            + str(count)

            +

            " программ"

        )



    return None








# ==========================
# CLOSE APP
# ==========================


def close_app(text):


    for name in apps:


        if name in text:


            for proc in psutil.process_iter(

                [

                    "name"

                ]

            ):


                try:


                    process=proc.info["name"]



                    if process and name in process.lower():


                        proc.kill()


                        return (

                            "Закрываю "

                            + name

                        )


                except:


                    pass



    return None






load_apps()