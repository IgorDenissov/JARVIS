import os
import queue
import numpy as np
import sounddevice as sd
import torch
from faster_whisper import WhisperModel

os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
os.environ["HF_HUB_DISABLE_SYMLINKS"] = "1"

# --------------------------------------------------
# Настройки
# --------------------------------------------------

SAMPLE_RATE = 16000
CHANNELS = 1
BLOCK_SIZE = 512

SILENCE_AFTER_SPEECH = 1.0  # секунд

# --------------------------------------------------
# Whisper
# --------------------------------------------------

print("[STT] Загружаю faster-whisper large-v3...")

model = WhisperModel(
    "C:/models/whisper-large-v3",
    device="cuda",
    compute_type="float16"
)

print("[STT] Whisper готов ✓")

# --------------------------------------------------
# Silero VAD
# --------------------------------------------------

print("[VAD] Загружаю Silero VAD...")

vad_model, utils = torch.hub.load(
    repo_or_dir="snakers4/silero-vad",
    model="silero_vad",
    trust_repo=True
)

(get_speech_timestamps,
 _, _, _, _) = utils

print("[VAD] Silero готов ✓")

# --------------------------------------------------
# Аудио очередь
# --------------------------------------------------

audio_queue = queue.Queue()

def audio_callback(indata, frames, time_info, status):
    audio_queue.put(indata.copy())

# --------------------------------------------------
# Проверка речи
# --------------------------------------------------

def has_speech(audio_chunk):

    audio = torch.from_numpy(
        audio_chunk.flatten().astype(np.float32)
    )


    # Вызываем модель напрямую — возвращает вероятность речи
    speech_prob = vad_model(audio, SAMPLE_RATE).item()
    
    if speech_prob > 0.5:
        #print(f"VOICE DETECTED (prob: {speech_prob:.2f})")
        return True
    
    return False

# --------------------------------------------------
# Основная функция
# --------------------------------------------------

def listen():

    print("[STT] Слушаю...")

    speech_started = False
    speech_buffer = []

    silence_chunks = 0
    silence_limit = int(
        SILENCE_AFTER_SPEECH
        * SAMPLE_RATE
        / BLOCK_SIZE
    )

    with sd.InputStream(
        samplerate=SAMPLE_RATE,
        channels=CHANNELS,
        blocksize=BLOCK_SIZE,
        dtype="float32",
        callback=audio_callback
    ):

        while True:

            chunk = audio_queue.get()


            #print(np.max(np.abs(chunk)))

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

    if not speech_buffer:
        return ""

    audio_data = np.concatenate(
        speech_buffer,
        axis=0
    ).flatten()

    segments, _ = model.transcribe(
        audio_data,
        language="ru",
        beam_size=5
    )

    text = " ".join(
        seg.text for seg in segments
    ).strip()

    if text:
        print(f"[STT] Распознано: {text}")

    return text


if __name__ == "__main__":

    while True:
        text = listen()
        print(text)