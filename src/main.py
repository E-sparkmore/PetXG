from PySide6.QtGui import QFontDatabase
import pet_label
import audio_ui
import config
import logging
import resource

logging.basicConfig(filename="log.txt", filemode="a")

def main():
    app = pet_label.QApplication([])
    if config.font_file:
        font_id = QFontDatabase.addApplicationFont(config.font_path + config.font_file)
        font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
    else:
        font_family = None
    app.setQuitOnLastWindowClosed(False)
    mypet = pet_label.MyPet(font_name=font_family)
    audio_player = audio_ui.AudioWidget(font_name=font_family)
    mypet.music_action.triggered.connect(audio_player.show)
    mypet.show()
    app.exec()

if __name__ == '__main__':
    main()