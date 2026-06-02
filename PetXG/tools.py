from datetime import datetime
from .deps import *
from . import config

all_tools = {}

match_type = {int: "integer", str: "string", float: "number"}

def ai_tools(function):
    """
    不支持lambda函数，要求函数有类型注解, Literal只支持字符串枚举,
    参数支持[int, str, float],
    返回值为字符串或者无返回值
    暂不支持成员函数
    """
    args = {}
    for key, value in function.__annotations__.items():
        if key != "return":
            if value in match_type:
                args[key] = {"type": match_type[value]}
            elif get_origin(value) == Literal:
                args[key] = {"type": "string", "enum": list(value.__args__)}
            else:
                logging.error(f"{function.__name__} 的参数 {key} 类型错误")
    if function.__defaults__:
        default_arg_len = len(function.__defaults__)
    else:
        default_arg_len = 0
    all_tools[function.__name__] = [function, args, list(args.keys())[:(len(args) - default_arg_len)]]

@ai_tools
def get_data_time_week() -> str :
    """Get date, time, day of the week"""
    now = datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S %A")



memory = {}
if os.path.exists(config.save_path / "memory.json"):
    f = open(config.save_path / "memory.json", "r")
    try:
        memory = json.load(f)
    except Exception as e:
        logging.error(str(e))
    f.close()

@ai_tools
def memory_tool(action: Literal["add", "edit", "delete"], key: str, value: str="") -> str:
    """
    操作memory的工具函数。memory采用键值对存储，以key值为索引，value为内容：
    - "add"：增加一条记忆
    - "edit"：更新一条记忆
    - "delete": 根据key删除一条记忆"
    你可以存储这类信息，以便后续对话中自动引用：
    - 和用户的关系
    - 用户偏好
    - 称呼
    - 计划/待办事项
    - 任何你认为对后续对话有帮助的长期信息
    你可以合并重复记忆并删掉不重要或者对后续对话没有帮助的信息
    记忆没有备份，谨慎删除
    """
    try:
        global memory
        match action:
            case "add":
                memory[key] = value
            case "edit":
                memory[key] = value
            case "delete":
                del memory[key]
        return "操作成功"
    except Exception as exc:
        return str(exc)


"""
all_tools:
函数名: {函数, "properties", "required"}
properties: {参数名: {"type": 类型名}}   可有多个参数
例：
properties: {"location": {"type": "string","description": "The city and state, e.g. San Francisco, CA"}}
required: [必需的参数名]
"""