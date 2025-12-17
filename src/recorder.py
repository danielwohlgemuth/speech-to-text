import numpy as np
import sounddevice as sd
import threading
import time
import whisper


class Recorder:
    def __init__(self):
        self.is_recording = False
        self.model = whisper.load_model("tiny.en")
        self.whisper_sample_rate = whisper.audio.SAMPLE_RATE
        default_device = sd.query_devices(kind='input')
        self.device_sample_rate = default_device['default_samplerate']
        self.audio_buffer = []
        self.recording_thread = None

    def audio_callback_factory(self):
        def audio_callback(indata, frames, time_info, status):
            if self.whisper_sample_rate != self.device_sample_rate:
                resampling_factor = self.whisper_sample_rate / self.device_sample_rate
                resampled_length = int(len(indata) * resampling_factor)
                indices = np.linspace(0, len(indata) - 1, resampled_length)
                indata = np.interp(indices, np.arange(len(indata)), indata.flatten()).reshape(-1, 1)
            self.audio_buffer.append(indata.copy())
        return audio_callback

    def record(self):
        try:
            print("Recording. Press Ctrl+C to stop and transcribe.")
            with sd.InputStream(callback=self.audio_callback_factory(), channels=1, samplerate=self.device_sample_rate, blocksize=1024):
                while self.is_recording:
                    time.sleep(0.1)
        except KeyboardInterrupt:
            pass

    def start(self):
        if not self.is_recording:
            self.audio_buffer = []
            self.is_recording = True
            self.recording_thread = threading.Thread(target=self.record, daemon=True)
            self.recording_thread.start()

    def stop(self):
        if self.is_recording:
            self.is_recording = False
            if self.recording_thread and self.recording_thread.is_alive():
                self.recording_thread.join(timeout=1.0)

    def transcribe(self):
        audio_data = np.empty((0, 1)) if not self.audio_buffer else np.concatenate(self.audio_buffer)
        normalized_audio = audio_data.flatten().astype(np.float32)
        transcription = self.model.transcribe(normalized_audio)
        return transcription["text"].strip()
