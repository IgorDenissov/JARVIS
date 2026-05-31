import os
import requests

# Whisper слушатель
from core.listener import listen

# Голос
from jarvis_voice import speak


AI_MODEL = "gemma3:27b"
OLLAMA_URL = "http://localhost:11434/api/generate"

# История разговора
conversation_history = []
MAX_HISTORY = 10


def ask_ai(question):

    conversation_history.append(
        {
            "role": "user",
            "content": question
        }
    )

    context = "\n".join([
        f"{'Игорь' if msg['role']=='user' else 'Джарвис'}: {msg['content']}"
        for msg in conversation_history[-MAX_HISTORY:]
    ])

    prompt = f"""
Ты Джарвис, ИИ-ассистент Игоря.

Говори как Джарвис из Железного человека.
Отвечай кратко: 1–2 предложения.
Будь полезным, спокойным и умным.

История разговора:

{context}

Ответь на последнее сообщение Игоря.
"""

    payload = {
        "model": AI_MODEL,
        "prompt": prompt,
        "stream": False
    }

    try:

        response = requests.post(
            OLLAMA_URL,
            json=payload,
            timeout=120
        )

        answer = response.json().get(
            "response",
            "Сэр, система задумалась."
        )

        conversation_history.append(
            {
                "role": "assistant",
                "content": answer
            }
        )

        if len(conversation_history) > MAX_HISTORY * 2:
            conversation_history.pop(0)
            conversation_history.pop(0)

        return answer

    except Exception as e:

        print(f"[ОШИБКА AI] {e}")

        return "Сэр, ядро искусственного интеллекта недоступно."


print("[JARVIS] Инициализация завершена.")
speak("Все системы в норме. Жду распоряжений.")


try:

    while True:

        text = listen()

        if not text:
            continue

        text = text.lower()

        print(f"[ВЫ]: {text}")

        if "отключись" in text:

            speak("Сеанс окончен, сэр.")
            os._exit(0)

        if (
            "забудь всё" in text
            or
            "очисти память" in text
        ):

            conversation_history.clear()

            speak("Память очищена, сэр.")
            continue


        if "джарвис" in text:

            query = text.replace(
                "джарвис",
                ""
            ).strip()

            if not query:

                speak("Да, сэр?")
                continue

            print("[ДУМАЮ...]")

            answer = ask_ai(query)

            print(f"[ДЖАРВИС]: {answer}")

            speak(answer)


except KeyboardInterrupt:

    print("\n[ВЫХОД] Остановлено пользователем")

    speak("Конец сессии, сэр.")

except Exception as e:

    print(f"[ОШИБКА] {e}")

    speak("Произошла ошибка системы.")