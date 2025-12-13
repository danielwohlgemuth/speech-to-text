import sounddevice as sd
import numpy as np
import whisper
import time


model = whisper.load_model("tiny.en")
whisper_sample_rate = whisper.audio.SAMPLE_RATE
default_device = sd.query_devices(kind='input')
device_sample_rate = default_device['default_samplerate']
audio_buffer = []

def audio_callback(indata, frames, time_info, status):
    if whisper_sample_rate != device_sample_rate:
        resampling_factor = whisper_sample_rate / device_sample_rate
        resampled_length = int(len(indata) * resampling_factor)
        indices = np.linspace(0, len(indata) - 1, resampled_length)
        indata = np.interp(indices, np.arange(len(indata)), indata.flatten()).reshape(-1, 1)
    audio_buffer.append(indata.copy())

try:
    print("Recording. Press Ctrl+C to stop and transcribe.")
    with sd.InputStream(callback=audio_callback, channels=1, samplerate=device_sample_rate, blocksize=1024):
        while True:
            time.sleep(0.1)
except KeyboardInterrupt:
    pass
finally:
    audio_data = np.concatenate(audio_buffer)
    normalized_audio = audio_data.flatten().astype(np.float32)
    transcription = model.transcribe(normalized_audio)
    print(transcription["text"].strip())
