import numpy as np
import pyperclip
import pystray
import sounddevice as sd
import threading
import time
import whisper

from PIL import Image, ImageDraw

class UiText():
    TITLE = "Speech to Text"
    RECORD = "Record"
    STOP = "Stop"
    QUIT = "Quit Speech to Text"


class Recorder:
    def __init__(self):
        self.is_recording = False
        self.model = whisper.load_model("tiny.en")
        self.whisper_sample_rate = whisper.audio.SAMPLE_RATE
        default_device = sd.query_devices(kind='input')
        self.device_sample_rate = default_device['default_samplerate']
        self.audio_buffer = []
        self.recording_thread = None

    def create_image(self,color):
        width = 64
        height = 64
        image = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        dc = ImageDraw.Draw(image)
        dc.ellipse((0, 0, width, height), fill='white')
        dc.ellipse((width//6, height//6, 5*width//6, 5*height//6), fill=color)
        return image

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

    def start_recording(self):
        if not self.is_recording:
            self.audio_buffer = []
            self.is_recording = True
            self.recording_thread = threading.Thread(target=self.record, daemon=True)
            self.recording_thread.start()

    def stop_recording(self):
        if self.is_recording:
            self.is_recording = False
            if self.recording_thread and self.recording_thread.is_alive():
                self.recording_thread.join(timeout=1.0)

    def transcribe(self):
        audio_data = np.empty((0, 1)) if not self.audio_buffer else np.concatenate(self.audio_buffer)
        normalized_audio = audio_data.flatten().astype(np.float32)
        transcription = self.model.transcribe(normalized_audio)
        return transcription["text"].strip()

    def on_clicked(self, icon, item):
        try:
            color = 'yellow'
            icon.icon = self.create_image(color)

            if not self.is_recording:
                self.start_recording()
                print('⏺️')
            else:
                self.stop_recording()
                text = self.transcribe()
                print(text)
                pyperclip.copy(text)

            color = 'red' if self.is_recording else 'blue'
            icon.icon = self.create_image(color)
            text = UiText.STOP if self.is_recording else UiText.RECORD
            icon.menu = pystray.Menu(
                pystray.MenuItem(text, self.on_clicked),
                pystray.MenuItem(UiText.QUIT, lambda icon, item: icon.stop())
            )
        except Exception as e:
            print('on_clicked error', e)


def main():
    recorder = Recorder()
    icon = pystray.Icon(
        UiText.TITLE,
        title=UiText.TITLE,
        icon=recorder.create_image('blue'),
        menu=pystray.Menu(
            pystray.MenuItem(UiText.RECORD, recorder.on_clicked),
            pystray.MenuItem(UiText.QUIT, lambda icon, item: icon.stop())
        ))
    icon.run()


if __name__ == "__main__":
    main()
