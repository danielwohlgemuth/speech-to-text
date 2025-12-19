import pyperclip
import pystray

from PIL import Image, ImageDraw


class UiText():
    TITLE = "Speech to Text"
    RECORD = "Record"
    STOP = "Stop"
    SELECT_MODEL = "Select Model"
    QUIT = "Quit Speech to Text"


class SystemTrayIcon:
    def __init__(self, recorder, transcriber):
        self.is_recording = False
        self.recorder = recorder
        self.transcriber = transcriber
        self.icon = None
        self.last_transcription = ""

    def create_image(self,color):
        width = 64
        height = 64
        image = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        dc = ImageDraw.Draw(image)
        dc.ellipse((0, 0, width, height), fill='white')
        dc.ellipse((width//6, height//6, 5*width//6, 5*height//6), fill=color)
        return image

    def get_record_text(self, item):
        return UiText.STOP if self.is_recording else UiText.RECORD

    def get_model_menu_items(self):
        models = self.transcriber.available_models()
        current_model = self.transcriber.get_current_model_name()
        menu_items = []

        for model in models:
            def create_model_handler(model_name):
                def load_model(icon, item):
                    self.icon.icon = self.create_image('yellow')
                    self.transcriber.load_model(model_name)
                    print(f"Loaded model: {model_name}")
                    self.icon.icon = self.create_image('blue')
                    self.icon.update_menu()
                return load_model

            display_text = f"✓ {model}" if model == current_model else model
            menu_items.append(pystray.MenuItem(display_text, create_model_handler(model)))

        return menu_items

    def get_copy_menu_item(self):
        if not self.last_transcription:
            return None

        def copy_to_clipboard(icon, item):
            pyperclip.copy(self.last_transcription)

        if len(self.last_transcription) <= 15:
            display_text = f'Copy "{self.last_transcription}"'
        else:
            display_text = f'Copy "{self.last_transcription[:15]}..."'

        return pystray.MenuItem(display_text, copy_to_clipboard)

    def get_menu_items(self):
        items = [pystray.MenuItem(self.get_record_text, self.record_or_transcribe)]

        copy_item = self.get_copy_menu_item()
        if copy_item:
            items.append(copy_item)

        if not self.is_recording:
            items.append(pystray.MenuItem(UiText.SELECT_MODEL, pystray.Menu(lambda: self.get_model_menu_items())))

        items.append(pystray.MenuItem(UiText.QUIT, lambda icon, item: self.icon.stop()))
        return items

    def record_or_transcribe(self, icon, item):
        try:
            self.is_recording = not self.is_recording
            color = 'yellow'
            self.icon.icon = self.create_image(color)

            if self.is_recording:
                self.recorder.start()
            else:
                self.recorder.stop()
                audio_data = self.recorder.get_audio_data()
                self.last_transcription = self.transcriber.transcribe(audio_data)
                print(self.last_transcription)
                pyperclip.copy(self.last_transcription)

            color = 'red' if self.is_recording else 'blue'
            self.icon.icon = self.create_image(color)

            self.icon.update_menu()
        except Exception as e:
            print('record_or_transcribe error', e)

    def show(self):
        self.icon = pystray.Icon(
            UiText.TITLE,
            title=UiText.TITLE,
            icon=self.create_image('blue'),
            menu=pystray.Menu(lambda: self.get_menu_items())
        )
        self.icon.run()
