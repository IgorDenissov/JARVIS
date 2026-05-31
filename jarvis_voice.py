import os
#os.add_dll_directory(r"C:\Users\Igor\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.1-full_build\bin")
os.environ["TORCHAUDIO_USE_BACKEND_DISPATCHER"] = "0"
os.environ["TORCHAUDIO_BACKEND"] = "soundfile"

import torch
from TTS.tts.configs.xtts_config import XttsConfig
from TTS.tts.models.xtts import XttsAudioConfig, XttsArgs
from TTS.config.shared_configs import BaseDatasetConfig
torch.serialization.add_safe_globals([XttsConfig, XttsAudioConfig, XttsArgs, BaseDatasetConfig])

# Патч: меняем torchaudio.load на soundfile до импорта TTS
import torchaudio
import soundfile as sf
import torch as _torch

def patched_load(filepath, *args, **kwargs):
    audio, sr = sf.read(filepath, dtype='float32')
    if audio.ndim == 1:
        audio = audio.reshape(1, -1)
    else:
        audio = audio.T
    return _torch.from_numpy(audio), sr

torchaudio.load = patched_load

import pygame
import tempfile
import time

# ───────────────────────────────────────────────
# Настройки
# ───────────────────────────────────────────────
VOICE_SAMPLE = os.path.join(
    os.path.dirname(__file__),
    "voices", "Morgan_Freeman CC3.wav"  # ← твой русский актёр
)
LANGUAGE = "ru"

# ───────────────────────────────────────────────
# Инициализация TTS (один раз при импорте)
# ───────────────────────────────────────────────
print("[VOICE] Загружаю XTTS v2...")
from TTS.api import TTS

tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2")
tts.to("cuda" if torch.cuda.is_available() else "cpu")
print(f"[VOICE] XTTS v2 готов ✓ (устройство: {'cuda' if torch.cuda.is_available() else 'cpu'})")

pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)


def speak(text: str):
    """Озвучить текст голосом из VOICE_SAMPLE."""
    if not text or not text.strip():
        return

    temp_file = tempfile.mktemp(suffix=".wav")
    try:
        tts.tts_to_file(
            text=text,
            speaker_wav=VOICE_SAMPLE,
            language=LANGUAGE,
            file_path=temp_file,
        )

        sound = pygame.mixer.Sound(temp_file)
        sound.set_volume(0.9)
        sound.play()

        while pygame.mixer.get_busy():
            time.sleep(0.05)

    finally:
        pygame.mixer.quit()
        pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
        if os.path.exists(temp_file):
            try:
                os.remove(temp_file)
            except Exception:
                pass


# ───────────────────────────────────────────────
# Быстрый тест
# ───────────────────────────────────────────────
if __name__ == "__main__":
    speak("все системы работают жду распоряжений")