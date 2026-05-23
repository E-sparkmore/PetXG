from pathlib import Path
from collections import namedtuple

#是否使用qrc资源
QRC = False

if QRC:
    path_prefix = ":"
    url_prefix = f"qrc"
else:
    path_prefix = Path(__file__).parent.parent.as_posix()
    url_prefix = f"file:///"

idle = path_prefix + "/datafile/frames/"
idle_motion = path_prefix + "/datafile/motion/"
runforward = path_prefix + "/datafile/runforward/"
runback = path_prefix + "/datafile/runback/"
datafile = path_prefix + "/datafile/"
music_file = path_prefix + "/datafile/music/"
music_url = url_prefix + music_file
font_path = datafile + "font/"
logo_file = "logo.png"
font_file = ""
Ai_name = "小光"
user_name = "我"

ActionText = namedtuple(
    "action_text",
    [
        "show_action",
        "reset_action",
        "quiet_action_normal",
        "quiet_action_quiet",
        "reverse_action",
        "music_action",
        "quit_action"
     ])
WindowTitle = namedtuple("window_title", ["audio_ui"])
action_simplified_Chinese_text = ActionText("隐藏/显示", "重置", "模式：正常", "模式：安静", "反转", "音乐", "退出")
action_English_text = ActionText("Hide/On","Reset","M:Normal","M:Quiet","Reverse","Music","Exit")
window_simplified_Chinese_title = WindowTitle("音乐列表")
window_English_title = WindowTitle("Music list")

window_title = window_simplified_Chinese_title
action_text = action_simplified_Chinese_text

motion_probability = 0.1
run_probability = 0.1
#音乐的扩展名列表
music_filter = ('*.mp3', "*.flac", "*.ogg", "*.wav")
