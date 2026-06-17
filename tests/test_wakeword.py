import openwakeword
from openwakeword.model import Model
import numpy as np
import sounddevice as sd

# Скачиваем модели (один раз)
openwakeword.utils.download_models()

# Загружаем модель "hey jarvis"
model = Model(
    wakeword_models=["hey_jarvis"],
    inference_framework="onnx"
)

SAMPLE_RATE = 16000
CHUNK = 1280  # openWakeWord ожидает чанки по 80мс при 16kHz

print("Слушаю... скажи 'Hey Jarvis'")

def callback(indata, frames, time_info, status):
    audio = (indata[:, 0] * 32767).astype(np.int16)
    prediction = model.predict(audio)
    
    for key, score in prediction.items():
        if score > 0.5:
            print(f"🎯 WAKE WORD DETECTED: {key} (score: {score:.2f})")

with sd.InputStream(
    samplerate=SAMPLE_RATE,
    channels=1,
    blocksize=CHUNK,
    dtype="float32",
    callback=callback
):
    while True:
        sd.sleep(100)