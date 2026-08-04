import customtkinter as ctk
import threading
import time
import math

import core.state as state


hud_window = None
canvas = None

status_label = None
command_label = None
answer_label = None
mic_button = None


running = False

reactor_angle = 0
reactor_speed = 5


answer_history = []


# =========================
# РЕАКТОР
# =========================

def set_reactor_speed(speed):

    global reactor_speed

    reactor_speed = speed



def reactor_animation():

    global reactor_angle

    while running:

        try:

            reactor_angle += reactor_speed

            canvas.delete("reactor")


            x = 250
            y = 120
            r = 45


            for i in range(12):

                angle = math.radians(
                    reactor_angle + i * 30
                )

                x1 = x + math.cos(angle)*r
                y1 = y + math.sin(angle)*r

                x2 = x + math.cos(angle)*(r+15)
                y2 = y + math.sin(angle)*(r+15)


                canvas.create_line(
                    x1,
                    y1,
                    x2,
                    y2,
                    width=3,
                    fill="#00ffff",
                    tags="reactor"
                )


            canvas.create_oval(
                x-35,
                y-35,
                x+35,
                y+35,
                outline="#00ffff",
                width=3,
                tags="reactor"
            )


            time.sleep(0.05)


        except:

            break



# =========================
# HUD
# =========================

def show_hud():

    global hud_window
    global canvas
    global status_label
    global command_label
    global answer_label
    global mic_button
    global running


    if hud_window:

        hud_window.deiconify()

        return


    running = True


    hud_window = ctk.CTk()


    hud_window.geometry(
        "500x650"
    )


    hud_window.title(
        "JARVIS HUD"
    )


    hud_window.attributes(
        "-topmost",
        True
    )


    hud_window.resizable(
        False,
        False
    )


    canvas = ctk.CTkCanvas(
        hud_window,
        width=450,
        height=250,
        bg="black",
        highlightthickness=0
    )


    canvas.pack()


    ctk.CTkLabel(
        hud_window,
        text="◉ J A R V I S",
        font=("Arial",28,"bold")
    ).pack()



    status_label = ctk.CTkLabel(
        hud_window,
        text="Статус: Готов",
        font=("Arial",18)
    )

    status_label.pack()



    mic_button = ctk.CTkButton(
        hud_window,
        text="🎤 Микрофон включен",
        command=toggle_mic
    )

    mic_button.pack(
        pady=10
    )



    command_label = ctk.CTkLabel(
        hud_window,
        text="Команда: -",
        font=("Arial",16)
    )

    command_label.pack(
        pady=10
    )



    answer_label = ctk.CTkLabel(
        hud_window,
        text="Jarvis: -",
        font=("Arial",16),
        wraplength=450,
        justify="left"
    )

    answer_label.pack(
        pady=10
    )


    threading.Thread(
        target=reactor_animation,
        daemon=True
    ).start()


    hud_window.mainloop()



def open_hud():

    threading.Thread(
        target=show_hud,
        daemon=True
    ).start()

    state.hud_visible = True

    return "Открываю интерфейс Jarvis"



# =========================
# ТЕКСТ
# =========================

def set_status(text):

    if status_label:

        status_label.configure(
            text="Статус: "+text
        )



def set_command(text):

    if command_label:

        command_label.configure(
            text="Команда: "+text
        )



def set_answer(text):

    global answer_history


    answer_history.append(
        "Jarvis: "+text
    )


    if len(answer_history)>5:

        answer_history.pop(0)



    if answer_label:

        answer_label.configure(
            text="\n\n".join(answer_history)
        )



# =========================
# МИКРОФОН
# =========================
def is_hud_open():

    return state.hud_visible
def toggle_mic():


    state.microphone_enabled = not state.microphone_enabled


    if state.microphone_enabled:


        mic_button.configure(
            text="🎤 Микрофон включен"
        )


    else:


        mic_button.configure(
            text="🔴 Микрофон выключен"
        )



def hide_hud():

    global hud_window


    state.hud_visible = False


    if hud_window:

        hud_window.withdraw()


    return "Скрываю интерфейс"
def show_time(text):

    global answer_label


    if answer_label:

        answer_label.configure(
            text="⏰ " + text
        )

        answer_label.after(
            5000,
            lambda:
            answer_label.configure(
                text=""
            )
        )

        return True


    return False