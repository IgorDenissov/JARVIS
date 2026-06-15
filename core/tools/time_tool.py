from datetime import datetime

def get_time():
    return datetime.now().strftime("%H:%M")


def run(user_text: str) -> str:
    return f"Сейчас {get_time()}"