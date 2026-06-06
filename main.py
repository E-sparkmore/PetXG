import json
import logging
import subprocess
import PetXG
from pathlib import Path

lnk_dict: dict[str, str] = {}

@PetXG.agent.ai_tool
def start_url(url: str) -> str:
    """打开网址为url（不含"https://"）的网页"""
    result = subprocess.run(["powershell", "-Command", "start", f"https://{url}"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return json.dumps({"returnCode": result.returncode, "stdout": str(result.stdout), "stderr": str(result.stderr)})

@PetXG.agent.ai_tool
def get_desktop_link() -> str:
    """获取用户桌面上的快捷方式"""
    user_desktop = Path.home() / "Desktop"
    public_desktop = Path('C:/Users/Public/Desktop')
    path_list: list[Path] = []
    for i in ("*.lnk", "*.exe"):
        path_list.extend(list(user_desktop.glob(i)))
        path_list.extend(list(public_desktop.glob(i)))
    lnk_dict.clear()
    for i in path_list:
        lnk_dict[i.stem] = str(i)
    return json.dumps(list(lnk_dict.keys()))

@PetXG.agent.ai_tool
def start_desktop_app(name: str) -> str:
    """根据快捷方式列表的名称运行应用软件"""
    try:
        result = subprocess.run(["powershell", "-Command", "Start-Process", f"'{lnk_dict[name]}'"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return json.dumps({"returnCode": result.returncode, "stdout": str(result.stdout), "stderr": str(result.stderr)})
    except Exception as e:
        logging.error(str(e))
        return str(e)

cwd = Path(__file__).parent
main = PetXG.PetMain(cwd)
# main.chat.use_tool_add_ui_info = True
main.exec()
