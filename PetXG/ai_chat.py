from .deps import *
from . import ai_ui, config, tools

if os.path.exists(".env"):
    load_dotenv()
elif "AI_BASE_URL" in os.environ and "AI_API_KEY" in os.environ:
    with open(config.save_path / ".env", "w") as f:
        base_url = os.environ.get("AI_BASE_URL")
        api_key = os.environ.get("AI_API_KEY")
        f.write(f"AI_BASE_URL = {base_url}\nAI_API_KEY = {api_key}")
function_tools = [{
        "type": "function",
        "function":{
            "name": i,
            "description": j[0].__doc__,
            "parameters": {
                "type": "object",
                "properties": j[1],
                "required": j[2]
            },
        }
    } for i, j in tools.all_tools.items()]
class AiStreamWork(QThread):
    text_received = Signal(str)
    finished = Signal(str)
    function_calling = Signal(str)
    def __init__(self, client: OpenAI):
        super().__init__()
        self.client  = client
        self.history = []
        self.prompt = ""
    def prepare(self, history, prompt):
        self.history = history
        self.prompt = prompt
    def run(self):
        messages = [
            {"role": "system", "content": config.SYSTEM_PROMPT.substitute(memory=json.dumps(tools.memory))}
        ]
        if self.history:
            messages.extend(self.history)
        # 添加当前用户消息
        if self.prompt:
            messages.append({"role": "user", "content": self.prompt})
        try:
            response = self.client.chat.completions.create(
                model=config.model,  # 使用DeepSeek对话模型
                messages=messages,
                temperature=config.temperature,
                max_tokens=config.max_tokens,
                top_p=config.top_p,
                frequency_penalty=config.frequency_penalty,
                presence_penalty=config.presence_penalty,
                stream = config.stream,
                tools= function_tools,
                tool_choice="auto"
            )
            if config.stream:
                tool_calls_set = {}
                charactor_start_time = time.time()
                for chunk in response:
                    stream_delta = chunk.choices[0].delta
                    if stream_delta.tool_calls:
                        for tool_call_delta in stream_delta.tool_calls:
                            idx = tool_call_delta.index
                            if idx not in tool_calls_set:
                                tool_calls_set[idx] = {
                                    "id": None,
                                    "name": None,
                                    "arguments": ""
                                }
                            if tool_call_delta.id:
                                tool_calls_set[idx]["id"] = tool_call_delta.id
                            if tool_call_delta.function.name:
                                tool_calls_set[idx]["name"] = tool_call_delta.function.name
                            if tool_call_delta.function.arguments:
                                tool_calls_set[idx]["arguments"] += tool_call_delta.function.arguments

                    content = chunk.choices[0].delta.content
                    if content:
                        for i in content:
                            interval = time.time() - charactor_start_time
                            if interval < config.charactor_interval:
                                time.sleep(config.charactor_interval - interval)
                            self.text_received.emit(i)
                            charactor_start_time = time.time()
                self.finished.emit("")
                if tool_calls_set:
                    assistant_message = {
                        "role": "assistant",
                        "content": None,
                        "tool_calls": []
                    }
                    for idx, tc in tool_calls_set.items():
                        tool_call_obj = {
                            "id": tc["id"],
                            "type": "function",
                            "function": {
                                "name": tc["name"],
                                "arguments": tc["arguments"]
                            }
                        }
                        assistant_message["tool_calls"].append(tool_call_obj)
                    self.function_calling.emit(json.dumps(assistant_message))
            else:
                self.text_received.emit(response.choices[0].message.content)
                self.finished.emit("")
                if response.choices[0].message.tool_calls:
                    assistant_message = {
                        "role": "assistant",
                        "content": None,
                        "tool_calls": []
                    }
                    for tool_call in response.choices[0].message.tool_calls:
                        tool_call_obj = {
                            "id": tool_call.id,
                            "type": "function",
                            "function": {
                                "name": tool_call.function.name,
                                "arguments": tool_call.function.arguments
                            }
                        }
                        assistant_message["tool_calls"].append(tool_call_obj)
                    self.function_calling.emit(json.dumps(assistant_message))

        except Exception as e:
            self.finished.emit(f"{config.Ai_name}遇到了一点问题: {str(e)}")
            logging.error(f"调用API出现问题: {str(e)}")

class MyAi(QWidget):
    information_color = 0x777777
    user_color = 0x19A31B
    assistant_color = 0x307CC7
    system_color = 0xF00004
    def __init__(self, font_name=None):
        super().__init__()
        self.setWindowOpacity(0.9)
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint)
        palette = self.palette()
        palette.setColor(self.backgroundRole(), "aliceblue")
        self.setPalette(palette)
        self.font = QFont()
        if font_name:
            self.font.setFamily(font_name)
        self.font.setPointSize(12)
        self.setFont(self.font)
        self.ui = ai_ui.Ui_Form()
        self.ui.setupUi(self)
        self.font.setBold(True)
        self.setFont(self.font)
        self.ui.pushButton.clicked.connect(self.send)
        self.ui.lineEdit.returnPressed.connect(self.send)
        self.history = []
        if os.path.exists(Path(config.save_path) / config.save_history_file) and config.save_history:
            try:
                with open(Path(config.save_path) / config.save_history_file, "r", encoding="utf-8") as f:
                    self.history = json.load(f)
            except Exception as e:
                logging.error(f"history.json 读取失败: {str(e)}")
        self.initialize_view()
        try:
            self.client = OpenAI(
                api_key=os.environ.get("AI_API_KEY"),
                base_url=os.environ.get("AI_BASE_URL")
            )
        except Exception as e:
            self.ui.lineEdit.returnPressed.disconnect(self.send)
            self.ui.pushButton.setDisabled(True)
            self.append_system_information('请添加“AI_BASE_URL”与“AI_API_KEY”的环境变量，或者该目录下创建".env“文件，要求使用兼容openai的接口')
            self.ui.pushButton.setDisabled(True)
            logging.warning(str(e))
            return
        self.thread = AiStreamWork(self.client)
        self.end_message = True
        self.thread.text_received.connect(self.tackle_message)
        self.thread.finished.connect(self.finish)
        self.thread.function_calling.connect(self.function_calling)

    def finish(self, message: str):
        self.end_message = True
        if message:
            self.append_system_information(message)
            self.history.pop()
        if config.stream:
            self.ui.pushButton.setDisabled(False)
            self.ui.lineEdit.returnPressed.connect(self.send)

    def function_calling(self, message: str):
        if message:
            if config.stream:
                self.ui.pushButton.setDisabled(True)
                self.ui.lineEdit.returnPressed.disconnect(self.send)
            self.append_information("正在使用工具")
            tool_calls_set = json.loads(message)
            tool_results = []
            for tool_call in tool_calls_set["tool_calls"]:
                if tool_call["function"]["name"] in tools.all_tools:
                    arguments = json.loads(tool_call["function"]["arguments"])
                    result = tools.all_tools[tool_call["function"]["name"]][0](**arguments)
                    if result is None:
                        result = ""
                    tool_results.append({
                        "role": "tool",
                        "tool_call_id": tool_call["id"],
                        "content": result
                    })
            self.history.append(tool_calls_set)
            self.history.extend(tool_results)
            self.thread.prepare(self.history, None)
            if config.stream:
                self.append_assistant_information("")
            self.thread.start()

    def send(self):
        user_input = self.ui.lineEdit.text().strip()
        if not user_input:
            return
        self.ui.lineEdit.setText("")
        self.append_user_information(user_input)
        match user_input:
            case x if len(x) > config.user_input_max_length:
                self.append_system_information(f"输入过长，请限制在{config.user_input_max_length}字以内。")
            case x if x.strip().lower() == "/clear_history":
                self.history = []
                self.append_system_information("历史记录已清除")
                self.save_history()
            case x if x.strip() == "/重新开始" or x.strip().lower() == "/restart":
                self.history = []
                self.ui.textBrowser.setPlainText("")
                self.append_system_information("新的开始")
                self.save_history()
            case _:
                user_input = user_input.strip()
                if len(user_input) > 8 and user_input[0:8].lower() == "/resend ":
                    if len(self.history) >= 2:
                        self.history = self.history[0:-2]
                        user_input = user_input[8:]
                        self.ui.textBrowser.setPlainText("")
                        self.initialize_view()
                        self.append_user_information(user_input)
                    elif len(self.history) == 0:
                        self.append_system_information("不可重新发送")
                        return
                # 获取回复
                self.thread.prepare(self.history, user_input)
                self.thread.start()
                if config.stream:
                    self.ui.pushButton.setDisabled(True)
                    self.ui.lineEdit.returnPressed.disconnect(self.send)
                    self.append_assistant_information("")
                self.history.append({"role": "user", "content": user_input})
        return

    def tackle_message(self, message: str):
        # 保存对话历史（可选，用于保持上下文）
        if self.end_message:
            self.history.append({"role": "assistant", "content": message})
            self.end_message = False
        else:
            self.history[-1]["content"] += message
        if config.stream:
            cursor = self.ui.textBrowser.textCursor()
            cursor.movePosition(cursor.MoveOperation.End)
            self.ui.textBrowser.setTextCursor(cursor)
            self.ui.textBrowser.insertPlainText(message)
        else:
            self.append_assistant_information(message)
        if len(self.history) > config.historical_dialogue_limit * 2:
            self.history = self.history[-config.historical_dialogue_limit * 2:]
        return

    def append_information(self, s: str):
        self.ui.textBrowser.setTextColor(self.information_color)
        self.ui.textBrowser.append(f"[提示] : {s}")

    def append_system_information(self, s: str):
        self.ui.textBrowser.setTextColor(self.system_color)
        self.ui.textBrowser.append(f"\n[系统] : {s}")

    def append_user_information(self, s: str):
        self.ui.textBrowser.setTextColor(self.user_color)
        self.ui.textBrowser.append(f"\n[{config.user_name}] : {s}")

    def append_assistant_information(self, s: str):
        self.ui.textBrowser.setTextColor(self.assistant_color)
        self.ui.textBrowser.append(f"\n[{config.Ai_name}] : {s}")

    def initialize_view(self):
        self.append_information("按下回车或者点击send以发送")
        if self.history:
            for i in self.history:
                match i["role"]:
                    case "user":
                        self.append_user_information(i["content"])
                    case "assistant":
                        if i["content"]:
                            self.append_assistant_information(i["content"])
                        elif i["tool_calls"]:
                            self.append_information("正在使用工具")
                    case _:
                        logging.error("history 出现其他值")

    def save_history(self):
        if config.save_history:
            try:
                with open(Path(config.save_path) / config.save_history_file, "w", encoding="utf-8") as f:
                    json.dump(self.history, f)
            except Exception as e:
                logging.exception(f"history.json 写入失败: {str(e)}")

    def save_memory(self):
        with open(config.save_path / "memory.json", "w") as f:
            json.dump(tools.memory, f)

    def __del__(self):
        self.save_history()
        self.save_memory()

    def closeEvent(self, event, /):
        self.save_memory()

def main():
    app = QApplication([])
    w = MyAi()
    w.show()
    app.exec()

if __name__ == '__main__':
    main()
