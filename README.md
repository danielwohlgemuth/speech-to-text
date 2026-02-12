# Speech to Text

A simple GUI application for offline (after initial download) speech-to-text transcription, originally using the [OpenAI Whisper](https://github.com/openai/whisper) Python library, but now using the [Hugging Face Transformers](https://github.com/huggingface/transformers) Python library.

![Screenshot](/assets/speech-to-text.png)

## Prerequisites

- [Python](https://www.python.org/downloads/)
- [uv](https://docs.astral.sh/uv/): A Python package and project manager

## Run

```bash
uv run src/main.py
```

## Build

```bash
uv run pyinstaller --onefile --name speech-to-text --paths src src/main.py
```

## Run build

```bash
./dist/speech-to-text
```
