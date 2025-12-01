from PySide6.QtWidgets import (QLabel,QSystemTrayIcon,QApplication,QMenu,QMessageBox,
                               QSlider,QVBoxLayout, QHBoxLayout, QWidget,QListWidget)
from PySide6.QtGui import QAction,Qt,QIcon,QPixmap,QTransform
from PySide6.QtCore import QTimer,Signal,QFile,QProcess,QUrl,QDir
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
import resource
import random
import math

idle = ":/datafile/frames/"
idle_motion = ":/datafile/motion/"
runforward = ":/datafile/runforward/"
runback = ":/datafile/runback/"
datafile = ":/datafile/"
music_file = ":/datafile/music/"

class MyPet(QLabel):
    resource_dir = ":/datafile/frames/"
    count = 1
    timer = QTimer()
    timer_seq = 40
    end_circle = Signal()
    move_direction = 0
    new_x = 0
    new_y = 0
    run_arrive = False
    reverse_pic = False

    def __init__(self):
        super().__init__()
        self.oldpos = self.pos()
        self.audio_output = QAudioOutput()
        self.media_player = QMediaPlayer()
        self.media_player.setAudioOutput(self.audio_output)
        self.media_player.setLoops(self.media_player.Loops.Infinite)
        self.audio_ui = AudioUi()
        self.audio_ui.volume_slider.valueChanged.connect(self.set_volume)
        self.audio_ui.list_view.currentRowChanged.connect(self.play_audio)
        self.audio_output.setVolume(0.5)
        self.icon = self.audio_ui.icon
        self.setWindowIcon(self.icon)
        self.show_action = QAction(self,text="隐藏/显示",icon=self.icon)
        self.reset_action = QAction(self,text="重置",icon=self.icon)
        self.quiet_action = QAction(self,text="状态：正常",icon=self.icon)
        self.reverse_action = QAction(self,text="反转",icon=self.icon)
        self.music_action = QAction(self, text="音乐",icon=self.icon)
        self.quit_action = QAction(self,text="退出",icon=self.icon)
        self.menu = self.get_menu()
        self.music_process = QProcess(self)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground,True)
        self.setWindowFlags(Qt.WindowType.Tool | Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.pixmap = QPixmap(self.resource_dir + "1.png")
        self.petheight = self.pixmap.height()//2+1
        self.width_divide_height = self.pixmap.width()/self.pixmap.height()
        self.reset_pet()
        self.setScaledContents(True)
        self.set_tray_icon()
        self.end_circle.connect(self.end_animate)
        self.timer.timeout.connect(self.change_pixmap)
        self.timer.start(self.timer_seq)
        self.set_right_click()
        self.audio_ui.hide()
        self.show()

    def set_right_click(self):
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)

    def show_context_menu(self,point):
        if self.resource_dir == runback or self.resource_dir == runforward:
            self.timer.timeout.disconnect(self.move_run)
            self.run_arrive = True
        self.menu.move(self.mapToGlobal(point))
        self.menu.exec()

    def reset_pet(self):
        if self.pixmap.height() > 50 and self.pixmap.width() > 50:
            self.resize(round(self.petheight*self.width_divide_height/2),round(self.petheight/2))
        elif self.width_divide_height > 1:
            self.resize(round(50 * self.width_divide_height), 50)
        else:
            self.resize(50,round(50 / self.width_divide_height))
        self.move(round(self.screen().geometry().width()/2-self.petheight*self.width_divide_height/4),
                  round(self.screen().geometry().height()/2-self.petheight/4))

    def change_pixmap(self):
        pixmap_to_change = QPixmap(self.resource_dir + f"{self.count}.png")
        if self.reverse_pic:
            pixmap_to_change = pixmap_to_change.transformed(QTransform().scale(-1,1))
        self.setPixmap(pixmap_to_change)
        self.count += 1
        if not QFile(self.resource_dir + f"{self.count}.png").exists():
            self.end_circle.emit()
            self.count = 1

    def end_animate(self):
        random_int = random.randint(0, 10)
        if self.resource_dir == idle:
            if random_int == 9:
                self.resource_dir = idle_motion
            elif random_int == 10:
                if self.quiet_action.text() == "状态：正常":
                    self.change_to_run()
        elif self.run_arrive or self.resource_dir == idle_motion:
            self.run_arrive = False
            self.resource_dir = idle

    def change_to_run(self):
        while True:
            self.new_x = random.randint(0,self.screen().geometry().width() - self.width())
            self.new_y = random.randint(0,self.screen().geometry().height() - self.height())
            if abs(self.new_x - self.x()) <= 100 or abs(self.new_y - self.y()) <= 100:
                break
        if self.new_x - self.x() > 0:
            if self.new_y - self.y() >= 0:
                self.move_direction = 1
                self.resource_dir = runforward
                self.reverse_pic = False
            else:
                self.move_direction = 4
                self.resource_dir = runback
                self.reverse_pic = False
        else:
            if self.new_y - self.y() >= 0:
                self.move_direction = 2
                self.resource_dir = runforward
                self.reverse_pic = True
            else:
                self.move_direction = 3
                self.resource_dir = runback
                self.reverse_pic = True
        self.timer.timeout.connect(self.move_run)

    def move_run(self):
        delta_x_divide_delta_y = abs((self.new_x - self.x())/(self.new_y - self.y()))
        speed = self.width()/40
        angle = math.atan(delta_x_divide_delta_y)
        speed_x = round(speed*math.sin(angle))
        speed_y = round(speed*math.cos(angle))
        if self.move_direction == 1:
            self.move(self.x() + speed_x, self.y() + speed_y)
        elif self.move_direction == 2:
            self.move(self.x() - speed_x, self.y() + speed_y)
        elif self.move_direction == 3:
            self.move(self.x() - speed_x, self.y() - speed_y)
        else:
            self.move(self.x() + speed_x, self.y() - speed_y)
        if abs(self.x() - self.new_x) <= 10:
            self.run_arrive = True
            self.timer.timeout.disconnect(self.move_run)

    def set_tray_icon(self):
        tray_icon = QSystemTrayIcon(self)
        tray_icon.setIcon(self.icon)
        tray_icon.activated.connect(lambda reason:(self.show() if reason == QSystemTrayIcon.ActivationReason.Trigger else 0))
        tray_icon.show()
        tray_icon.setContextMenu(self.menu)

    def get_menu(self):
        menu = QMenu(self)
        self.show_action.triggered.connect(self.show_hide_act)
        self.reset_action.triggered.connect(self.reset_pet)
        self.quiet_action.triggered.connect(self.quiet_mode)
        self.reverse_action.triggered.connect(self.reverse_pixmap)
        self.music_action.triggered.connect(self.audio_ui.show)
        self.quit_action.triggered.connect(QApplication.quit)
        menu.addAction(self.show_action)
        menu.addAction(self.reset_action)
        menu.addAction(self.quiet_action)
        menu.addAction(self.reverse_action)
        menu.addAction(self.music_action)
        menu.addAction(self.quit_action)
        return menu

    def show_hide_act(self):
        if self.isHidden():
            self.show()
        else:
            self.hide()

    def quiet_mode(self):
        if self.quiet_action.text() == "状态：安静":
            self.quiet_action.setText("状态：正常")
        else:
            self.quiet_action.setText("状态：安静")

    def reverse_pixmap(self):
        self.reverse_pic = not self.reverse_pic

    def play_audio(self, audio_file):
        if audio_file:
            self.media_player.setSource(QUrl(f"qrc{music_file}{self.audio_ui.music_list[audio_file]}.mp3"))
            self.media_player.play()
        else:
            self.media_player.stop()

    def set_volume(self, value):
        volume = value / 100.0
        self.audio_output.setVolume(volume)

    def mousePressEvent(self,event):
        if event.buttons() == Qt.MouseButton.LeftButton or event.buttons() == Qt.MouseButton.MiddleButton:
            self.oldpos = event.globalPosition().toPoint()
        if self.resource_dir == runback or self.resource_dir == runforward:
            self.timer.timeout.disconnect(self.move_run)
            self.run_arrive = True

    def mouseMoveEvent(self, event):
        delta = event.globalPosition().toPoint() - self.oldpos
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.move(self.x()+delta.x(),self.y()+delta.y())
        elif event.buttons() == Qt.MouseButton.MiddleButton:
            if (delta.y() <0 and self.width() > 50 and self.height() > 50) or delta.y() > 0:
                new_height = self.height()+delta.y()
                self.resize(round(new_height*self.width_divide_height),round(new_height))
        self.oldpos = event.globalPosition().toPoint()

class AudioUi(QWidget):
    def __init__(self,):
        super().__init__()
        self.h_layout = QHBoxLayout(self)
        self.icon = QIcon(datafile + "logo.png")
        self.setWindowIcon(self.icon)
        self.list_view = QListWidget(self)
        self.v_layout = QVBoxLayout()
        self.volume_slider = QSlider(Qt.Orientation.Vertical)
        self.label = QLabel("音量:")
        self.music_dir = QDir(music_file)
        self.music_dir.setNameFilters(['*.mp3'])
        self.music_list = ['无'] + [i.split('.')[0] for i in self.music_dir.entryList()]
        self.list_view.addItems(self.music_list)
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("音乐列表")
        self.setFixedSize(300, 200)
        self.h_layout.addWidget(self.list_view)
        self.v_layout.addWidget(self.label)
        self.v_layout.addWidget(self.volume_slider)
        self.h_layout.addLayout(self.v_layout)
        self.setLayout(self.h_layout)
        self.list_view.setFixedWidth(100)
        self.volume_slider.setMinimum(0)
        self.volume_slider.setMaximum(100)
        self.volume_slider.setValue(50)

    def closeEvent(self, event, /):
        self.hide()
        event.ignore()

