import numpy as np
from openwakeword.model import Model as WakeWordModel
from core import state
import time

WAKE_CHUNK = 1280

print("[WAKE] Загружаю Hey Jarvis...")
wake_model = WakeWordModel(
    wakeword_models=["hey_jarvis"],
    inference_framework="onnx"
)
print("[WAKE] Готов ✓")


def wait_for_wake_word(audio_queue):
    print("[WAKE] Жду 'Hey Jarvis'...")

    wake_buffer = []

    while True:

        if state.is_speaking:
            while not audio_queue.empty():
                audio_queue.get()  # сбрасываем накопленное
            wake_buffer.clear()
            time.sleep(0.1)
            continue

        chunk = audio_queue.get()
        wake_buffer.append(chunk.flatten())

        total_samples = sum(len(c) for c in wake_buffer)
        if total_samples >= WAKE_CHUNK:
            audio_data = np.concatenate(wake_buffer)[:WAKE_CHUNK]
            wake_buffer = []

            audio_int16 = (audio_data * 32767).astype(np.int16)
            prediction = wake_model.predict(audio_int16)

            for key, score in prediction.items():
                if score > 0.98:
                    print(f"[WAKE] Активация! ({key}: {score:.2f})")
                    while not audio_queue.empty():
                        audio_queue.get()
                    return

if __name__ == "__main__":
    import queue
    import sounddevice as sd

    SAMPLE_RATE = 16000

    q = queue.Queue()

    def cb(indata, frames, time_info, status):
        q.put(indata.copy())

    with sd.InputStream(samplerate=SAMPLE_RATE, channels=1, blocksize=512, dtype="float32", callback=cb):
        while True:
            wait_for_wake_word(q)
            print("--- сработало, жду снова ---")