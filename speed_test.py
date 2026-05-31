import time
import requests

MODEL = #"gemma3:27b"
"qwen2.5-coder:14b" 
#"qwen2.5:32b"

prompt = "Объясни квантовую механику простыми словами и приведи примеры"

start = time.time()

r = requests.post(
    "http://localhost:11434/api/generate",
    json={
        "model": MODEL,
        "prompt": prompt,
        "stream": False
    }
)

end = time.time()

response = r.json()["response"]

duration = end - start

print("\n--- РЕЗУЛЬТАТ ---")
print("Модель:", MODEL)
print("Время ответа:", round(duration, 2), "сек")
print("Длина ответа:", len(response), "символов")
print("Скорость:", round(len(response) / duration, 2), "символов/сек")