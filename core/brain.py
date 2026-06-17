from core.llm import ask_llm
from core.tools.registry import run_tool
from config.settings import FAST_MODEL, SMART_MODEL

# ─────────────────────────────
# ПАМЯТЬ
# ─────────────────────────────
conversation_history = []
MAX_HISTORY = 10


def clear_memory():
    conversation_history.clear()


def build_context():
    return "\n".join([
        f"{'Игорь' if m['role'] == 'user' else 'Джарвис'}: {m['content']}"
        for m in conversation_history[-MAX_HISTORY:]
    ])


# ─────────────────────────────
# ВЫБОР МОДЕЛИ
# ─────────────────────────────
def choose_model(text: str) -> str:

    text = text.lower()

    if any(k in text for k in [
        "объясни",
        "почему",
        "как работает",
        "код",
        "напиши",
        "создай",
        "разработай",
        "спроектируй",
        "квантовая",
        "программирование",
        "архитектура",
        "алгоритм"
    ]):
        return SMART_MODEL

    return FAST_MODEL


# ─────────────────────────────
# ОСНОВНАЯ ЛОГИКА
# ─────────────────────────────
def process(user_text: str) -> str:

    user_text = user_text.strip()

    # ───── TOOLS ─────
    tool_result = run_tool(user_text)

    if tool_result:

        conversation_history.append({
            "role": "user",
            "content": user_text
        })

        conversation_history.append({
            "role": "assistant",
            "content": tool_result
        })

        return tool_result

    # ───── ПАМЯТЬ ─────
    conversation_history.append({
        "role": "user",
        "content": user_text
    })

    context = build_context()

    # ───── ВЫБОР МОДЕЛИ ─────
    model = choose_model(user_text)

    print(f"[MODEL] {model}")

    # ───── ПРОМПТ ─────
    prompt = f"""
Ты Джарвис — персональный ИИ-ассистент Игоря.

Правила:

- Отвечай только на русском языке.
- Не смешивай русский и английский.
- Не говори "давайте разберем это".
- Не упоминай, что ты языковая модель.
- Отвечай естественно как голосовой ассистент.
- Для простых вопросов отвечай кратко.
- Для сложных вопросов объясняй подробно.
- Не используй markdown.
- Не используй списки и нумерацию без необходимости.
- Для голосового режима отвечай максимум 5 предложениями.

Контекст:
{context}

Вопрос:
{user_text}
"""

    # ───── LLM ─────
    answer = ask_llm(model, prompt)

    conversation_history.append({
        "role": "assistant",
        "content": answer
    })

    # ───── ОГРАНИЧЕНИЕ ПАМЯТИ ─────
    if len(conversation_history) > MAX_HISTORY * 2:
        conversation_history[:] = conversation_history[-MAX_HISTORY * 2:]

    return answer