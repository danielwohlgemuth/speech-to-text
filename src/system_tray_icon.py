import pyperclip
import pystray

from PIL import Image, ImageDraw


class UiText():
    TITLE = "Speech to Text"
    RECORD = "Record"
    STOP = "Stop"
    QUIT = "Quit Speech to Text"


class SystemTrayIcon:
    def __init__(self, recorder):
        self.is_recording = False
        self.recorder = recorder
        self.icon = None

    def create_image(self,color):
        width = 64
        height = 64
        image = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        dc = ImageDraw.Draw(image)
        dc.ellipse((0, 0, width, height), fill='white')
        dc.ellipse((width//6, height//6, 5*width//6, 5*height//6), fill=color)
        return image

    def on_clicked(self, icon, item):
        try:
            self.is_recording = not self.is_recording
            color = 'yellow'
            self.icon.icon = self.create_image(color)

            if self.is_recording:
                self.recorder.start()
            else:
                self.recorder.stop()
                text = self.recorder.transcribe()
                print(text)
                pyperclip.copy(text)

            color = 'red' if self.is_recording else 'blue'
            self.icon.icon = self.create_image(color)
            text = UiText.STOP if self.is_recording else UiText.RECORD
            self.icon.menu = pystray.Menu(
                pystray.MenuItem(text, self.on_clicked),
                pystray.MenuItem(UiText.QUIT, lambda icon, item: self.icon.stop())
            )
        except Exception as e:
            print('on_clicked error', e)

    def show(self):
        self.icon = pystray.Icon(
            UiText.TITLE,
            title=UiText.TITLE,
            icon=self.create_image('blue'),
            menu=pystray.Menu(
                pystray.MenuItem(UiText.RECORD, self.on_clicked),
                pystray.MenuItem(UiText.QUIT, lambda icon, item: self.icon.stop())
            ))
        self.icon.run()
