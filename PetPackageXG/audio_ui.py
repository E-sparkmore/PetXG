from .deps import *
from . import config, styles

class AudioWidget(QWidget):
    def __init__(self,font_name=None):
        super().__init__()
        self.v_layout = QVBoxLayout(self)
        self.icon = QIcon(config.datafile + "logo.png")
        self.setWindowIcon(self.icon)
        self.ui_font = QFont()
        if font_name:
            self.ui_font.setFamily(font_name)
        self.ui_font.setPointSize(13)
        self.list_view = QListWidget(self)
        self.h_layout = QHBoxLayout()
        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.label = QLabel("音量:")
        self.label.setFont(self.ui_font)
        self.music_dir = QDir(config.music_file)
        self.music_dir.setNameFilters([j for i in config.music_filter for j in (i, i.upper())])
        self.music_list = self.music_dir.entryList()
        self.list_view.addItem("无")
        for i in self.music_list:
            self.list_view.addItem(i.split(".")[0])
        self.init_ui()
        self.audio_output = QAudioOutput()
        self.media_player = QMediaPlayer()
        self.media_player.setAudioOutput(self.audio_output)
        self.media_player.setLoops(self.media_player.Loops.Infinite)
        self.audio_output.setVolume(0.5)
        self.volume_slider.valueChanged.connect(self.set_volume)
        self.list_view.currentRowChanged.connect(self.play_audio)
        self.list_view.setFont(self.ui_font)
        self.setStyleSheet(styles.audio_ui_style)

    def init_ui(self):
        self.setWindowTitle(config.window_title.audio_ui)
        self.setFixedWidth(250)
        self.setMinimumHeight(300)
        self.resize(250, 400)
        self.v_layout.addWidget(self.list_view)
        self.h_layout.addWidget(self.label)
        self.h_layout.addWidget(self.volume_slider)
        self.v_layout.addLayout(self.h_layout)
        self.setLayout(self.v_layout)
        self.volume_slider.setMinimum(0)
        self.volume_slider.setMaximum(100)
        self.volume_slider.setValue(50)
        self.volume_slider.setMinimumHeight(30)

    def play_audio(self, audio_index):
        if audio_index:
            self.media_player.setSource(QUrl(config.music_url + self.music_list[audio_index-1]))
            self.media_player.play()
        else:
            self.media_player.stop()

    def set_volume(self, value):
        volume = value / 100.0
        self.audio_output.setVolume(volume)

def main():
    app = QApplication([])
    w = AudioWidget()
    w.show()
    app.exec()

if __name__ == '__main__':
    main()