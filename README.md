# Speech to Text

```bash
uv run src/main.py
```

```bash
uv run pyinstaller --onefile --hidden-import=whisper --hidden-import=recorder --hidden-import=system_tray_icon --collect-data whisper src/main.py --name speech-to-text
```

```bash
./dist/speech-to-text
```