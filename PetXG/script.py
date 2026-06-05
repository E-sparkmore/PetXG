from .setting.deps import *
from . import pet_label, audio_ui, resource
from .agent import ai_chat, tools
from .setting import config
from .setting.config import logger

class PetMain(object):
    def __init__(self, save_path):
        if save_path:
            config.save_path = Path(save_path)
            file_handler = logging.FileHandler((config.save_path / "log.txt").as_posix(), "w")
            file_handler.setFormatter(config.log_format)
            logger.addHandler(file_handler)
        else:
            config.save_path = config.package_base_path
        self.app = QApplication([])
        self.font_id = QFontDatabase.addApplicationFont(config.font_path + config.font_file)
        self.font_families = QFontDatabase.applicationFontFamilies(self.font_id)
        if self.font_families:
            self.font_family = self.font_families[0]
        else:
            self.font_family = None
        self.app.setQuitOnLastWindowClosed(False)
        self.mypet = pet_label.MyPet(font_name=self.font_family)
        self.audio_player = audio_ui.AudioWidget(font_name=self.font_family)
        self.chat = ai_chat.MyAi(font_name=self.font_family, dotenv_path=config.save_path / ".env")
        self.mypet.music_action.triggered.connect(self.audio_player.show)
        self.mypet.chat_action.triggered.connect(self.chat.show)
        self.add_tools()

    def exec(self):
        self.mypet.show()
        self.app.exec()

    def add_tools(self):
        tools.add_ai_tool(self.audio_player.get_music_list)
        tools.add_ai_tool(self.audio_player.play_audio)
        tools.add_ai_tool(self.audio_player.set_volume)
        tools.add_ai_tool(self.chat.memory_tool)



def main(save_path):
    pet = PetMain(save_path)
    pet.exec()