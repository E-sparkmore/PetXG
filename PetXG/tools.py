from datetime import datetime
from .deps import *

all_tools = {}

match_type = {int: "integer", str: "string", float: "number"}

def add_ai_tool(function):
    """
    不支持lambda函数，要求函数有类型注解, Literal只支持字符串枚举,
    参数支持[int, str, float],
    返回值为字符串或者无返回值
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

def ai_tool(function):
    add_ai_tool(function)
    return function

#函数注册例子
@ai_tool
def get_data_time_week() -> str :
    """Get date, time, day of the week"""
    now = datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S %A")


"""
all_tools:
函数名: {函数, "properties", "required"}
properties: {参数名: {"type": 类型名}}   可有多个参数
例：
properties: {"location": {"type": "string","description": "The city and state, e.g. San Francisco, CA"}}
required: [必需的参数名]
"""