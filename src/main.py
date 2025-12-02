from PetLabel import *
from PySide6.QtWidgets import (QLabel,QSystemTrayIcon,QApplication,QMenu,QMessageBox,
                               QSlider,QVBoxLayout, QHBoxLayout, QWidget,QListWidget)
from PySide6.QtGui import QAction,Qt,QIcon,QPixmap,QTransform
from PySide6.QtCore import QTimer,Signal,QFile,QProcess,QUrl,QDir
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput

if __name__ == "__main__":
    app = QApplication([])
    mypet = MyPet()
    app.setStyleSheet('''
            QMenu {
                background-color:transparent;
                border-radius: 20px;
                padding-top:20px;
                padding-left:15px;
                padding-right:10px;
                padding-bottom:40px;
                height: 200px;
                background-image: url("''' + datafile + '''menu_skin.png");
                background-repeat: no-repeat;
            }
            QMenu::item {
                font-weight: 600;
                font-size:12px;
                padding:2px;
                margin: 2px;
                margin-right:60px;
                padding-left:20px;
                padding-right: 0px;
                color: black;
            }
            QMenu::item:selected{
                background-color: rgba(20,20,20,0.1);
            }
            QMenu::item::QToolButton {
                padding-left:6px;
            }
            QMenu::item:!enabled {
                color: gray;
            }
            QListWidget {
                font-family: "MSYH";
                font-weight: bold;
            }
            QSlider {
                width: 25px;
            }
            AudioUi {
                background-color: #AFE3FF;
            }
        ''')
    app.exec()