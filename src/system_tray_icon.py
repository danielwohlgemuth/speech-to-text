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

    def create_copy_menu_item(self, transcription):
        def copy_to_clipboard(icon, item):
            pyperclip.copy(transcription)

        if len(transcription) <= 10:
            display_text = f'Copy "{transcription}"'
        else:
            display_text = f'Copy "{transcription[:15]}..."'

        return pystray.MenuItem(display_text, copy_to_clipboard)

    def record_or_transcribe(self, icon, item):
        try:
            self.is_recording = not self.is_recording
            color = 'yellow'
            self.icon.icon = self.create_image(color)
            transcription = ''

            if self.is_recording:
                self.recorder.start()
            else:
                self.recorder.stop()
                transcription = self.recorder.transcribe().strip()
                print(transcription)
                pyperclip.copy(transcription)

            color = 'red' if self.is_recording else 'blue'
            self.icon.icon = self.create_image(color)
            text = UiText.STOP if self.is_recording else UiText.RECORD

            menu_items = [pystray.MenuItem(text, self.record_or_transcribe)]

            if transcription:
                menu_items.append(self.create_copy_menu_item(transcription))

            menu_items.append(pystray.MenuItem(UiText.QUIT, lambda icon, item: self.icon.stop()))

            self.icon.menu = pystray.Menu(*menu_items)
        except Exception as e:
            print('record_or_transcribe error', e)

    def show(self):
        self.icon = pystray.Icon(
            UiText.TITLE,
            title=UiText.TITLE,
            icon=self.create_image('blue'),
            menu=pystray.Menu(
                pystray.MenuItem(UiText.RECORD, self.record_or_transcribe),
                pystray.MenuItem(UiText.QUIT, lambda icon, item: self.icon.stop())
            ))
        self.icon.run()
