import sounddevice as sd
import numpy as np
import whisper
import threading
import queue
import time
from collections import deque


model = whisper.load_model("tiny.en")
whisper_sample_rate = whisper.audio.SAMPLE_RATE
default_device = sd.query_devices(kind='input')
device_sample_rate = default_device['default_samplerate']
chunk_duration_seconds = 2
chunk_samples = int(whisper_sample_rate * chunk_duration_seconds)
audio_queue = queue.Queue()
is_recording = True

def audio_callback(indata, frames, time_info, status):
    if whisper_sample_rate != device_sample_rate:
        resampling_factor = whisper_sample_rate / device_sample_rate
        resampled_length = int(len(indata) * resampling_factor)
        indices = np.linspace(0, len(indata) - 1, resampled_length)
        indata = np.interp(indices, np.arange(len(indata)), indata.flatten()).reshape(-1, 1)
    audio_queue.put(indata.copy())

def transcribe_audio(audio_buffer):
    audio_data = np.concatenate(audio_buffer)
    normalized_audio = audio_data.flatten().astype(np.float32)
    transcription = model.transcribe(normalized_audio)
    if transcription["text"].strip():
        print(transcription["text"].strip())

def transcribe_worker():
    audio_buffer = deque()
    total_samples = 0
    while is_recording or not audio_queue.empty():
        try:
            audio_chunk = audio_queue.get(timeout=0.1)
            audio_buffer.append(audio_chunk)
            total_samples += len(audio_chunk)
            if total_samples >= chunk_samples:
                transcribe_audio(audio_buffer)
                audio_buffer.clear()
                total_samples = 0
        except queue.Empty:
            continue

transcription_thread = threading.Thread(target=transcribe_worker)
transcription_thread.start()

try:
    with sd.InputStream(callback=audio_callback, channels=1, samplerate=device_sample_rate, blocksize=1024):
        print("Live transcription. Press Ctrl+C to stop.")
        while True:
            time.sleep(0.1)
except KeyboardInterrupt:
    pass
finally:
    is_recording = False
    if transcription_thread:
        transcription_thread.join(timeout=5)
