# Speech to Text

```bash
uv run src/main.py
```

```bash
uv run pyinstaller --onefile --hidden-import=whisper --hidden-import=recorder --hidden-import=system_tray_icon --collect-data whisper --name speech-to-text --paths src src/main.py
```

```bash
./dist/speech-to-text
```