NUMBERS = {

"ноль":0,
"один":1,
"два":2,
"три":3,
"четыре":4,
"пять":5,

"zero":0,
"one":1,
"two":2,
"three":3,
"four":4,
"five":5

}


def normalize(text):

    words=text.lower().split()

    out=[]

    for w in words:

        if w in NUMBERS:
            out.append(str(NUMBERS[w]))

        else:
            out.append(w)

    return " ".join(out)