import os
import sys
import signal
import atexit
from recorder import Recorder
from transcriber import Transcriber
from system_tray_icon import SystemTrayIcon


PID_FILE = os.path.expanduser("~/.speech-to-text.pid")


def is_pid_running(pid):
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def prevent_multiple_instances_workaround():
    if os.path.exists(PID_FILE):
        try:
            with open(PID_FILE, 'r') as f:
                stored_pid = int(f.read().strip())

            if is_pid_running(stored_pid):
                sys.exit(1)
            else:
                os.remove(PID_FILE)
        except (ValueError, IOError):
            try:
                os.remove(PID_FILE)
            except OSError:
                pass

    with open(PID_FILE, 'w') as f:
        f.write(str(os.getpid()))

    atexit.register(cleanup)
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)


def cleanup():
    try:
        if os.path.exists(PID_FILE):
            with open(PID_FILE, 'r') as f:
                stored_pid = int(f.read().strip())
            if stored_pid == os.getpid():
                os.remove(PID_FILE)
    except (ValueError, IOError, OSError):
        pass


def signal_handler(signum, frame):
    cleanup()
    sys.exit(0)


def main():
    prevent_multiple_instances_workaround()

    transcriber = Transcriber()
    recorder = Recorder(transcriber.get_sample_rate())
    icon = SystemTrayIcon(recorder, transcriber)
    icon.show()


if __name__ == "__main__":
    main()
