import torch
import sounddevice as sd
import numpy as np

model, utils = torch.hub.load(
    repo_or_dir="snakers4/silero-vad",
    model="silero_vad",
    trust_repo=True
)

(get_speech_timestamps,
 _, _, _, _) = utils

SAMPLE_RATE = 16000

print("Говорите...")

audio = sd.rec(
    int(5 * SAMPLE_RATE),
    samplerate=SAMPLE_RATE,
    channels=1,
    dtype="float32"
)

sd.wait()

audio = torch.from_numpy(audio.flatten())
 
print("Максимум:", np.max(np.abs(audio.numpy())))

speech = get_speech_timestamps(
    audio,
    model,
    sampling_rate=SAMPLE_RATE
)

print("Найдены участки речи:")
print(speech)