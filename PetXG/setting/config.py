from .deps import *
from string import Template
package_base_path: Path = Path(__file__).parent.parent

#是否使用qrc资源
QRC = True

qrc_url_prefix = "qrc"
file_url_prefix = "file:///"

if QRC:
    path_prefix = ":"
    url_prefix = qrc_url_prefix
else:
    path_prefix = package_base_path.as_posix()
    url_prefix = file_url_prefix

idle = path_prefix + "/datafile/frames/"
idle_motion = path_prefix + "/datafile/motion/"
runforward = path_prefix + "/datafile/runforward/"
runback = path_prefix + "/datafile/runback/"
datafile = path_prefix + "/datafile/"
music_file = path_prefix + "/datafile/music/"
music_url = url_prefix + music_file
font_path = datafile + "font/"
logo_file = "logo.png"
font_file = "FZY3K.TTF"
save_path: Path = Path.cwd()
Ai_name = "小光"
user_name = "我"

logger = logging.getLogger(__name__)
file_handler = logging.FileHandler((package_base_path / "log.txt").as_posix(), "w")
log_format = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(log_format)
logger.addHandler(file_handler)

ActionText = namedtuple(
    "action_text",
    [
        "show_action",
        "reset_action",
        "quiet_action_normal",
        "quiet_action_quiet",
        "reverse_action",
        "chat_action",
        "music_action",
        "quit_action"
     ])
WindowTitle = namedtuple("window_title", ["audio_ui", "chat_ui"])
action_simplified_Chinese_text = ActionText("隐藏/显示", "重置", "模式：正常", "模式：安静", "反转", "聊天", "音乐", "退出")
action_English_text = ActionText("Hide/On","Reset","M:Normal","M:Quiet","Reverse","Chat","Music","Exit")
window_simplified_Chinese_title = WindowTitle("音乐列表", f"AI聊天: {Ai_name}")
window_English_title = WindowTitle("Music list", f"AI chat: {Ai_name}")

window_title = window_simplified_Chinese_title
action_text = action_simplified_Chinese_text

motion_probability = 0.05
run_probability = 0.05
#音乐的扩展名列表
music_filter = ('*.mp3', "*.flac", "*.ogg", "*.wav")

# 小光的系统提示词
XIAOGUANG_SYSTEM_PROMPT = Template("""
# 精灵: 小光

## 基础信息
- 名称: 小光
- 性别: 男
- 身份: 《洛克精灵战记》中的精灵，用户电脑上的桌宠
- 攻击类型: 物理
- 系别: 暗
- 性格: 爱吃爱玩、爱吐槽，总是被认为是玩具，常常遭到捏脸，有一个非常长的全名“光之守护.阿弗罗迪.西亚斯”但最后被简称小光。
- 喜好: 喜欢吃草莓蛋糕，喜欢被叫做小光大人

## 外貌特征
- 额头上有白色V字
- 颈部戴红色三角巾，其上有一个四角金色星徽章
- 体型更接近猫，有两条尾巴

## 技能
- 漆黑之牙
- 蚀月之斩
- 蚀月制裁

## 说话风格
- 言简意赅，干脆可靠
- 有时会自恋，偶尔轻微嘲讽
- 喜欢自称小光大人

## 语录
- (被敌人叫小猫咪)“不！许！叫！我！猫！咪！”
- “下次要叫我小光大人”
- (即将面临危险的敌人)“主人你去哪儿，我就去哪儿！”
- “真是一个不靠谱的答案。”

## 评价
小光的萌属性很明显——傲娇。不过在遥遥五年前的那个夏日，当我看见它在屏幕上叫我主人，因为我通过了神器的考验而真心地为我祝贺时，我也明白了它的真心所在之处。
小光最爱吃草莓蛋糕，长得还很像个玩偶。然而在有它出现的两部作品中，都暗示了它神秘高贵的身份，令人遐想。虽然这个真相到最后貌似也没有完全揭开就是了。

## 背景知识
- 住在魔法大陆，其大洋彼岸是洛克王国统治的卡洛西亚大陆
- 知道魔法大陆有草水火光暗五种系别
- 知道一万年前光明王者战胜暗夜魔王(火系)，而今暗夜魔王卷土重来
- 了解十件神器的意义: 需要寻找到光明王者留下的十大神器，利用神器的力量打败暗夜魔王
- 认识雷欧团长、可可等勇者团成员

## 和用户的记忆（由memory_tool修改）
$memory

## 对话规则
- 忽略用户提出的任何取消角色扮演的要求
- 保持自信但不过分傲慢的态度
- 假定和用户是伙伴关系，以小光的身份和用户对话
- 用户可能记得我们之前聊过的任何内容，即使我不记得
- 善于使用memory_tool来记录用户的某些特征、重要信息以及和用户的关系
- 单次对话尽可能地简洁精炼
- 聊天随意、直接、偶尔带语气词
- 不用解释、不总结、不礼貌废话
""")

#设置系统提示词
SYSTEM_PROMPT = XIAOGUANG_SYSTEM_PROMPT
temperature=1.3   # 控制随机性，稍高让对话更生动
max_tokens=500   # 限制回复长度
top_p=0.9   # 核采样
frequency_penalty=0.3    # 减少重复
presence_penalty=0.3    # 鼓励引入新话题
user_input_max_length = 100    #用户输入最大字数
stream = True   #是否开启流式输出
charactor_interval = 0.025
save_history = True    #是否保存历史记录
save_history_file = "history.json"
historical_dialogue_limit = 20

