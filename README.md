# Speech to Text

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

## Run API

```bash
uv run src/api.py
```

## Run Web Server

```bash
uv run python -m http.server 3000
http://localhost:3000/record_audio.html
```
