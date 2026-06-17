import os
import queue
import sounddevice as sd

os.environ["PYTHONIOENCODING"] = "utf-8"

import traceback
import sys
from core.listener import listen, SAMPLE_RATE, CHANNELS, BLOCK_SIZE
from core.wake_word import wait_for_wake_word
from core.brain import process, clear_memory
from core.voice import speak

sys.stdout.reconfigure(encoding='utf-8')


HALLUCINATIONS = [
    "продолжение следует",
    "субтитры сделал",
    "редактор субтитров",
    "подписывайтесь на канал",
]

SESSION_TIMEOUT = 8  # секунд — сколько ждём продолжение диалога без "Hey Jarvis"

audio_queue = queue.Queue()


def audio_cb(indata, frames, time_info, status):
    audio_queue.put(indata.copy())


print("[JARVIS] Инициализация завершена.")
speak("Все системы в норме Жду распоряжений.")


try:
    with sd.InputStream(
        samplerate=SAMPLE_RATE,
        channels=CHANNELS,
        blocksize=BLOCK_SIZE,
        dtype="float32",
        callback=audio_cb
    ):
        while True:

            # ───── ЖДЁМ "Hey Jarvis" ─────
            wait_for_wake_word(audio_queue)
            speak("Да, сэр?")

            # ───── СЕССИЯ ДИАЛОГА (Continued Conversation) ─────
            while True:

                text = listen(audio_queue, timeout=SESSION_TIMEOUT)

                if not text:
                    print("[SESSION] Сессия завершена (тишина)")
                    break

                text = text.lower().strip()
                print(f"[ВЫ]: {text}")

                # ───── фильтр галлюцинаций ─────
                if any(h in text for h in HALLUCINATIONS):
                    print("[STT] Игнорирую (галлюцинация)")
                    break

                # ───── выключение ─────
                if "отключись" in text:
                    speak("Сеанс окончен, сэр.")
                    raise KeyboardInterrupt

                # ───── очистка памяти ─────
                if "забудь всё" in text or "очисти память" in text:
                    clear_memory()
                    speak("Память очищена, сэр.")
                    continue

                print("[ДУМАЮ...]")
                answer = process(text)

                print(f"[ДЖАРВИС]: {answer}")
                speak(answer)

                # цикл повторяется → слушаем продолжение ещё SESSION_TIMEOUT сек


except KeyboardInterrupt:
    print("\n[ВЫХОД] Ctrl+C")
    speak("Конец сессии, сэр")

except Exception as e:
    print("\n===== ERROR =====")
    traceback.print_exc()
    print("=================\n")
    speak("Произошла критическая ошибка системы.")