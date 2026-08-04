import re



# ==========================
# ENGLISH FIX
# ==========================


ENGLISH_WORDS = {


    "хром":
        "chrome",

    "гугл":
        "google",

    "ютуб":
        "youtube",

    "ю туб":
        "youtube",

    "дискорд":
        "discord",

    "телеграм":
        "telegram",

    "ватсап":
        "whatsapp",

    "виндовс":
        "windows",

    "фотошоп":
        "photoshop",

    "стим":
        "steam",

    "браузер":
        "browser",

    "спотифай":
        "spotify"

}




def fix_english(text):


    for ru,en in ENGLISH_WORDS.items():


        text=text.replace(

            ru,

            en

        )


    return text






# ==========================
# NUMBERS
# ==========================


NUMBERS = {


    "ноль":0,


    "один":1,

    "одна":1,


    "два":2,

    "две":2,


    "три":3,

    "четыре":4,


    "пять":5,

    "шесть":6,

    "семь":7,

    "восемь":8,

    "девять":9,


    "десять":10,


    "двадцать":20,

    "тридцать":30,

    "сорок":40,

    "пятьдесят":50,

    "шестьдесят":60,

    "семьдесят":70,

    "восемьдесят":80,

    "девяносто":90,


    "сто":100

}

NUMBER_FIX = {


    "7десят": "семьдесят",

    "6десят": "шестьдесят",

    "5десят": "пятьдесят",

    "8десят": "восемьдесят",

    "9десят": "девяносто",


    "2дцать": "двадцать",

    "3дцать": "тридцать",

    "4дцать": "сорок",

}
def fix_bad_numbers(text):


    for bad,good in NUMBER_FIX.items():

        text=text.replace(

            bad,

            good

        )


    return text


def words_to_number(text):


    words=text.split()


    total=0


    found=False



    for word in words:


        if word in NUMBERS:


            total += NUMBERS[word]

            found=True




    if found:

        return total



    return None






# ==========================
# CLEAN VOICE
# ==========================


def normalize_text(text):


    text=text.lower().strip()
    text = fix_bad_numbers(text)


    text=fix_english(

        text

    )



    number=words_to_number(

        text

    )



    if number is not None:


        for word,value in NUMBERS.items():


            text=text.replace(

                word,

                str(value)

            )



    text=re.sub(

        r"\s+",

        " ",

        text

    )

    text = text.replace(
        "7десят",
        "70"
    )

    text = text.replace(
        "6десят",
        "60"
    )

    text = text.replace(
        "5десят",
        "50"
    )

    text = text.replace(
        "8десят",
        "80"
    )

    text = text.replace(
        "9десят",
        "90"
    )

    return text