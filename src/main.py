from src.recorder import Recorder
from src.system_tray_icon import SystemTrayIcon


def main():
    recorder = Recorder()
    icon = SystemTrayIcon(recorder)
    icon.show()


if __name__ == "__main__":
    main()
