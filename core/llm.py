import requests
from config.settings import OLLAMA_URL


def ask_llm(model: str, prompt: str, temperature: float = 0.7) -> str:
    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": temperature
                }
            },
            timeout=120
        )

        response.raise_for_status()
        data = response.json()

        return data.get("response", "Сэр, я не получил ответ от модели.")

    except requests.exceptions.Timeout:
        return "Сэр, модель слишком долго думает."

    except requests.exceptions.ConnectionError:
        return "Сэр, нет соединения с Ollama."

    except Exception as e:
        return f"Сэр, ошибка LLM слоя: {str(e)}"