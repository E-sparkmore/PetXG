from .deps import *
from . import pet_label, audio_ui, ai_chat, config, resource

def main(save_path: str|None, *args, **kwargs):
    if save_path:
        config.save_history_path = (Path(save_path) / config.save_history_path).as_posix()
    app = QApplication([])
    font_id = QFontDatabase.addApplicationFont(config.font_path + config.font_file)
    font_families = QFontDatabase.applicationFontFamilies(font_id)
    if font_families:
        font_family = font_families[0]
    else:
        font_family = None
    app.setQuitOnLastWindowClosed(False)
    app.styleHints().setColorScheme(Qt.ColorScheme.Light)
    mypet = pet_label.MyPet(font_name=font_family)
    audio_player = audio_ui.AudioWidget(font_name=font_family)
    chat = ai_chat.MyAi(font_name=font_families[0])
    mypet.music_action.triggered.connect(audio_player.show)
    mypet.chat_action.triggered.connect(chat.show)
    mypet.show()
    app.exec()