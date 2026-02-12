import numpy as np
import os
from transformers import pipeline, AutoModelForSpeechSeq2Seq, AutoTokenizer, AutoFeatureExtractor, AutoConfig


MODELS = [
    'openai/whisper-tiny.en',
    'openai/whisper-base.en',
    'openai/whisper-small.en',
    'openai/whisper-medium.en',
    'openai/whisper-tiny',
    'openai/whisper-base',
    'openai/whisper-small',
    'openai/whisper-medium',
    'openai/whisper-large',
    'openai/whisper-large-v2',
]


class Transcriber:
    def __init__(self, model_name="openai/whisper-tiny.en"):
        self.load_model(model_name)

    def transcribe(self, audio_data):
        normalized_audio = audio_data.flatten().astype(np.float32)
        transcription = self.transcriber(normalized_audio)
        return transcription["text"].strip()

    def available_models(self):
        return MODELS

    def load_model(self, model_name):
        model_directory = f'{os.environ["HOME"]}/.cache/speech-to-text/model/{model_name}/'
        if not os.path.exists(model_directory):
            model = AutoModelForSpeechSeq2Seq.from_pretrained(model_name)
            model.save_pretrained(model_directory)
        model = AutoModelForSpeechSeq2Seq.from_pretrained(model_directory, local_files_only=True)

        tokenizer_directory = f'{os.environ["HOME"]}/.cache/speech-to-text/tokenizer/{model_name}/'
        if not os.path.exists(tokenizer_directory):
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            tokenizer.save_pretrained(tokenizer_directory)
        tokenizer = AutoTokenizer.from_pretrained(tokenizer_directory, local_files_only=True)

        feature_extractor_directory = f'{os.environ["HOME"]}/.cache/speech-to-text/feature_extractor/{model_name}/'
        if not os.path.exists(feature_extractor_directory):
            feature_extractor = AutoFeatureExtractor.from_pretrained(model_name)
            feature_extractor.save_pretrained(feature_extractor_directory)
        feature_extractor = AutoFeatureExtractor.from_pretrained(feature_extractor_directory, local_files_only=True)

        config_directory = f'{os.environ["HOME"]}/.cache/speech-to-text/config/{model_name}/'
        if not os.path.exists(config_directory):
            config = AutoConfig.from_pretrained(model_name)
            config.save_pretrained(config_directory)
        config = AutoConfig.from_pretrained(config_directory, local_files_only=True)

        self.transcriber = pipeline('automatic-speech-recognition', model=model, tokenizer=tokenizer, feature_extractor=feature_extractor, config=config)
        self.model_name = model_name

    def get_current_model_name(self):
        return self.model_name

    def get_sample_rate(self):
        return 16000
