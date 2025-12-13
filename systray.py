import pystray

from PIL import Image, ImageDraw

class UiText():
    TITLE = "Speech to Text"
    RECORD = "Record"
    STOP = "Stop"
    QUIT = "Quit Speech to Text"


is_recording = False

def create_image(color):
    width = 64
    height = 64
    image = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    dc = ImageDraw.Draw(image)
    dc.ellipse((0, 0, width, height), fill='white')
    dc.ellipse((width//6, height//6, 5*width//6, 5*height//6), fill=color)
    return image

def on_clicked(icon, item):
    global is_recording

    is_recording = not is_recording
    color = 'red' if is_recording else 'blue'
    icon.icon = create_image(color)
    text = UiText.STOP if is_recording else UiText.RECORD
    icon.menu = pystray.Menu(
        pystray.MenuItem(text, on_clicked),
        pystray.MenuItem(UiText.QUIT, lambda icon, item: icon.stop())
    )


def main():
    icon = pystray.Icon(
        UiText.TITLE,
        title=UiText.TITLE,
        icon=create_image('blue'),
        menu=pystray.Menu(
            pystray.MenuItem(UiText.RECORD, on_clicked),
            pystray.MenuItem(UiText.QUIT, lambda icon, item: icon.stop())
        ))
    icon.run()


if __name__ == "__main__":
    main()
