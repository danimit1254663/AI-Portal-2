import tkinter as tk
from tkinter import ttk, messagebox
import requests
import json


# =====================================
# ВСТАВЬТЕ СЮДА ТОКЕН
# =====================================

TOKEN = ""


# =====================================

API = "https://quasar.yandex.net"


class YandexQuasar:

    def __init__(self, root):

        self.root = root
        self.root.title("Яндекс ТВ и Станции")
        self.root.geometry("500x500")

        self.devices = []


        self.headers = {
            "Authorization": f"OAuth {TOKEN}",
            "Content-Type": "application/json"
        }


        tk.Button(
            root,
            text="Получить устройства",
            command=self.get_devices,
            width=30
        ).pack(pady=10)


        self.listbox = ttk.Combobox(
            root,
            width=45,
            state="readonly"
        )

        self.listbox.pack(pady=10)


        frame = tk.Frame(root)
        frame.pack(pady=20)


        tk.Button(
            frame,
            text="Громкость +",
            width=15,
            command=lambda:self.command("volume_up")
        ).grid(row=0,column=0,padx=5)


        tk.Button(
            frame,
            text="Громкость -",
            width=15,
            command=lambda:self.command("volume_down")
        ).grid(row=0,column=1,padx=5)



        tk.Button(
            frame,
            text="Выключить",
            width=15,
            command=lambda:self.command("power_off")
        ).grid(row=1,column=0,padx=5,pady=10)


        tk.Button(
            frame,
            text="Стоп",
            width=15,
            command=lambda:self.command("stop")
        ).grid(row=1,column=1,padx=5,pady=10)



        self.status = tk.Label(
            root,
            text="Готов"
        )

        self.status.pack()



    # =====================================
    # Получение устройств
    # =====================================

    def get_devices(self):

        try:

            r = requests.post(
                API + "/glagol/device_list",
                headers=self.headers,
                json={}
            )


            print(r.text)

            data = r.json()


            self.devices = data.get(
                "devices",
                []
            )


            names = []

            for d in self.devices:

                names.append(
                    d.get(
                        "name",
                        "Без имени"
                    )
                )


            self.listbox["values"] = names


            if names:

                self.listbox.current(0)


            self.status.config(
                text=f"Найдено: {len(names)}"
            )


        except Exception as e:

            messagebox.showerror(
                "Ошибка",
                str(e)
            )



    # =====================================
    # Команды
    # =====================================

    def command(self, action):

        index = self.listbox.current()


        if index < 0:

            return


        device = self.devices[index]


        payload = {

            "device_id":
                device["id"],

            "command":
                action
        }


        try:

            r = requests.post(

                API + "/glagol/device_action",

                headers=self.headers,

                json=payload

            )


            print(
                r.text
            )


            self.status.config(
                text="Команда отправлена"
            )


        except Exception as e:

            messagebox.showerror(
                "Ошибка",
                str(e)
            )




root = tk.Tk()

app = YandexQuasar(root)

root.mainloop()