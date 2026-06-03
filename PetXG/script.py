from .deps import *
from . import pet_label, audio_ui, ai_chat, config, resource, tools

class PetMain(object):
    def __init__(self, save_path):
        if save_path:
            config.save_path = Path(save_path)
        else:
            config.save_path = config.package_base_path
        if os.path.exists(config.save_path / ".env"):
            load_dotenv(dotenv_path=config.save_path / ".env")
        elif "AI_BASE_URL" in os.environ and "AI_API_KEY" in os.environ:
            with open(config.save_path / ".env", "w") as f:
                base_url = os.environ.get("AI_BASE_URL")
                api_key = os.environ.get("AI_API_KEY")
                f.write(f"AI_BASE_URL = {base_url}\nAI_API_KEY = {api_key}")
        logging.basicConfig(filename=(config.save_path / "log.txt").as_posix(), filemode="a")
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
        self.chat = ai_chat.MyAi(font_name=self.font_family)
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