import os
os.environ["PYTHONIOENCODING"] = "utf-8"

import traceback
from core.listener import listen
from core.brain import process, clear_memory
from jarvis_voice import speak
import sys

sys.stdout.reconfigure(encoding='utf-8')


WAKE_WORDS = [
    "джарвис",
    "жарвис",
    "арвис",
    "карвис",
    "джорес"
]


print("[JARVIS] Инициализация завершена.")
speak("Все системы в норме. Жду распоряжений.")


try:
    while True:

        text = listen()
        if not text:
            continue

        text = text.lower().strip()
        print(f"[ВЫ]: {text}")

        # ───── выключение ─────
        if "отключись" in text:
            speak("Сеанс окончен, сэр.")
            break

        # ───── очистка памяти ─────
        if "забудь всё" in text or "очисти память" in text:
            clear_memory()
            speak("Память очищена, сэр.")
            continue

        # ───── активация ассистента ─────
        if any(w in text for w in WAKE_WORDS):

            query = text

            for w in WAKE_WORDS:
                query = query.replace(w, "")

            query = query.strip()

            if not query:
                speak("Да, сэр?")
                continue

            print("[ДУМАЮ...]")

            answer = process(query)

            print(f"[ДЖАРВИС]: {answer}")
            speak(answer)


except KeyboardInterrupt:
    print("\n[ВЫХОД] Ctrl+C")
    speak("Конец сессии, сэр.")

except Exception as e:
    print("\n===== ERROR =====")
    traceback.print_exc()
    print("=================\n")
    speak("Произошла критическая ошибка системы.")