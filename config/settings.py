from pathlib import Path


# Корень проекта JARVIS
BASE_DIR = Path(__file__).parent.parent


# ==========================
# VOICE SETTINGS
# ==========================

VOICE_SAMPLE = BASE_DIR / "voices" / "Morgan_Freeman CC3.wav"

VOICE_LANGUAGE = "ru"


# ==========================
# LLM SETTINGS
# ==========================

OLLAMA_URL = "http://localhost:11434/api/generate"

FAST_MODEL = "qwen2.5:1.5b"
SMART_MODEL = "qwen2.5:32b"

# ==========================
# STT / LISTENER SETTINGS
# ==========================

WHISPER_MODEL = Path("C:/models/whisper-large-v3")

WHISPER_DEVICE = "cuda"
WHISPER_COMPUTE_TYPE = "float16"

SAMPLE_RATE = 16000
CHANNELS = 1
BLOCK_SIZE = 512

SILENCE_AFTER_SPEECH = 1.0