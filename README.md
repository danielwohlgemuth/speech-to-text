# Speech to Text

A simple GUI application for local speech-to-text transcription using OpenAI Whisper.

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
uv run pyinstaller --onefile --collect-data whisper --name speech-to-text --paths src src/main.py
```

## Run build

```bash
./dist/speech-to-text
```
