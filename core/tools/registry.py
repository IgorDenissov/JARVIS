from core.tools.time_tool import run as time_tool


def run_tool(user_text: str):

    text = user_text.lower()

    # TIME TOOL
    if any(word in text for word in [
        "время",
        "времени",
        "час",
        "часов"
    ]):
        return time_tool(user_text)

    return None