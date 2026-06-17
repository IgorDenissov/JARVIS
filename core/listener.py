import os
import time
import numpy as np
import torch
from faster_whisper import WhisperModel

from config.settings import (
    WHISPER_MODEL,
    WHISPER_DEVICE,
    WHISPER_COMPUTE_TYPE,
    SAMPLE_RATE,
    CHANNELS,
    BLOCK_SIZE,
    SILENCE_AFTER_SPEECH
)

os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
os.environ["HF_HUB_DISABLE_SYMLINKS"] = "1"


print("[STT] Загружаю faster-whisper large-v3...")
model = WhisperModel(str(WHISPER_MODEL), device=WHISPER_DEVICE, compute_type=WHISPER_COMPUTE_TYPE)
print("[STT] Whisper готов ✓")

print("[VAD] Загружаю Silero VAD...")
vad_model, utils = torch.hub.load(
    repo_or_dir="snakers4/silero-vad",
    model="silero_vad",
    trust_repo=True
)
(get_speech_timestamps, _, _, _, _) = utils
print("[VAD] Silero готов ✓")


def has_speech(audio_chunk):
    audio = torch.from_numpy(audio_chunk.flatten().astype(np.float32))
    speech_prob = vad_model(audio, SAMPLE_RATE).item()
    return speech_prob > 0.7


def listen(audio_queue, timeout=None):
    """
    Слушает команду через VAD + Whisper.

    timeout: максимальное время ожидания НАЧАЛА речи в секундах.
             Если речь не началась за это время — возвращает "".
             Если None — ждёт бесконечно (как раньше).
    """

    speech_started = False
    speech_buffer = []

    silence_chunks = 0
    silence_limit = int(SILENCE_AFTER_SPEECH * SAMPLE_RATE / BLOCK_SIZE)

    print("[STT] Слушаю команду...")

    start_time = time.time()

    while True:

        try:
            chunk = audio_queue.get(timeout=0.5)
        except Exception:
            chunk = None

        if chunk is None:
            if timeout and not speech_started and (time.time() - start_time) > timeout:
                print("[STT] Таймаут ожидания")
                return ""
            continue

        if has_speech(chunk):
            if not speech_started:
                print("[VAD] Речь обнаружена")
            speech_started = True
            silence_chunks = 0
            speech_buffer.append(chunk)
        else:
            if speech_started:
                speech_buffer.append(chunk)
                silence_chunks += 1
                if silence_chunks >= silence_limit:
                    print("[VAD] Конец речи")
                    break
            elif timeout and (time.time() - start_time) > timeout:
                print("[STT] Таймаут ожидания")
                return ""

    if not speech_buffer:
        return ""

    audio_data = np.concatenate(speech_buffer, axis=0).flatten()
    segments, _ = model.transcribe(audio_data, language="ru", beam_size=5)
    text = " ".join(seg.text for seg in segments).strip()

    if text:
        print(f"[STT] Распознано: {text}")

    return text