from faster_whisper import WhisperModel
import sounddevice as sd
import numpy as np


class WhisperSTT:

    def __init__(self):

        print("Загрузка Whisper...")

        self.model = WhisperModel(
            "small",
            device="cpu",
            compute_type="int8"
        )

        print("Whisper готов")


    def listen(self):

        print("🎤 Слушаю...")


        audio = sd.rec(
            int(5 * 16000),
            samplerate=16000,
            channels=1,
            dtype="float32"
        )

        sd.wait()


        audio = np.squeeze(audio)


        segments, info = self.model.transcribe(
            audio,
            language="ru"
        )


        text = ""


        for segment in segments:
            text += segment.text


        text = text.lower().strip()


        print(
            "HEARD:",
            text
        )


        return text