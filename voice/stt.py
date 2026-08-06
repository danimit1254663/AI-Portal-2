from faster_whisper import WhisperModel


model = WhisperModel(
    "small",
    device="cuda",
    compute_type="float16"
)


def recognize(audio):

    segments, info = model.transcribe(
        audio,
        language=None
    )

    text = ""

    for s in segments:
        text += s.text

    return text.strip()