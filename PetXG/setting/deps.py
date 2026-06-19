from PySide6.QtWidgets import (QLabel,QSystemTrayIcon,QApplication,QMenu, QWidget, QLineEdit,QPushButton,
                               QHBoxLayout, QListWidget, QVBoxLayout, QSlider, QMessageBox, QGridLayout)
from PySide6.QtGui import QAction,Qt,QIcon,QPixmap,QTransform, QFont, QFontDatabase, QPalette
from PySide6.QtCore import QTimer,Signal,QFile, QThread, Qt, QDir, QUrl
from PySide6.QtMultimedia import QAudioOutput, QMediaPlayer
from dotenv import load_dotenv
from openai import OpenAI
import os
import random
import math
from enum import Enum
import logging
import json
import time
from pathlib import Path
from collections import namedtuple
from typing import Literal, get_origin, Any
