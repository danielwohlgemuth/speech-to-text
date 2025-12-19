import numpy as np
import whisper


class Transcriber:
    def __init__(self, model_name="tiny.en"):
        self.load_model(model_name)

    def transcribe(self, audio_data):
        normalized_audio = audio_data.flatten().astype(np.float32)
        transcription = self.model.transcribe(normalized_audio)
        return transcription["text"].strip()

    def available_models(self):
        return whisper.available_models()

    def load_model(self, model_name):
        self.model_name = model_name
        self.model = whisper.load_model(model_name)

    def get_current_model_name(self):
        return self.model_name

    def get_sample_rate(self):
        return whisper.audio.SAMPLE_RATE
