from ..setting.deps import *
from ..setting import config
from . import ai_ui, tools
from ..setting.config import logger

class AiStreamWork(QThread):
    text_received = Signal(str)
    function_calling = Signal(str)
    def __init__(self, client: OpenAI):
        super().__init__()
        self.function_tools: list[Any] = [{
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
        self.client = client
        self.history: list[dict[Any, Any]] | None = None
        self.prompt: list[dict[Any, Any]] | None = None
        self.memory: dict[Any, Any] | None = None
        self.error: str = ""
        self.message_stream: str = ""
        self.this_history: list[dict[Any, Any]] = []
    def prepare(self, history: list[Any], prompt: list[dict[Any, Any]] | None, memory: dict[Any, Any]):
        self.history = history
        self.prompt = prompt
        self.memory = memory
    def run(self):
        messages: list[dict[Any, Any]] = [
            {"role": "system", "content": config.SYSTEM_PROMPT.substitute(memory=json.dumps(self.memory))}
        ]
        if self.history:
            messages.extend(self.history)
        # 添加当前用户消息
        if self.prompt:
            self.this_history.extend(self.prompt)
        if self.this_history:
            messages.extend(self.this_history)
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
                tools= self.function_tools,
                tool_choice="auto"
            )
            assistant_tool_message: dict[str, str | None | list[dict[str, str | dict[str, str]]]] = {
                "role": "assistant",
                "content": None,
                "tool_calls": []
            }
            use_tool = False
            if config.stream:
                tool_calls_set = {}
                charactor_start_time = time.time()
                for chunk in response:
                    stream_delta = chunk.choices[0].delta
                    if stream_delta.tool_calls:
                        use_tool = True
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
                            self.message_stream += i
                            charactor_start_time = time.time()
                self.this_history.append({"role": "assistant", "content": self.message_stream})
                self.message_stream = ""

                if tool_calls_set:
                    for idx, tc in tool_calls_set.items():
                        tool_call_obj = {
                            "id": tc["id"],
                            "type": "function",
                            "function": {
                                "name": tc["name"],
                                "arguments": tc["arguments"]
                            }
                        }
                        assistant_tool_message["tool_calls"].append(tool_call_obj)
                    self.this_history.append(assistant_tool_message)
                    self.function_calling.emit(json.dumps(assistant_tool_message))
            else:
                content = response.choices[0].message.content
                self.text_received.emit(content)
                self.this_history.append({"role": "assistant", "content": content})
                if response.choices[0].message.tool_calls:
                    use_tool = True
                    for tool_call in response.choices[0].message.tool_calls:
                        tool_call_obj = {
                            "id": tool_call.id,
                            "type": "function",
                            "function": {
                                "name": tool_call.function.name,
                                "arguments": tool_call.function.arguments
                            }
                        }
                        assistant_tool_message["tool_calls"].append(tool_call_obj)
                    self.this_history.append(assistant_tool_message)
                    self.function_calling.emit(json.dumps(assistant_tool_message))
            if use_tool:
                tool_results = []
                for tool_call_obj in assistant_tool_message["tool_calls"]:
                    if tool_call_obj["function"]["name"] in tools.all_tools:
                        arguments = json.loads(tool_call_obj["function"]["arguments"])
                        result = tools.all_tools[tool_call_obj["function"]["name"]][0](**arguments)
                        if result is None:
                            result = ""
                        tool_results.append({
                            "role": "tool",
                            "tool_call_id": tool_call_obj["id"],
                            "content": result
                        })
                self.this_history.extend(tool_results)
                self.prompt = None
                self.run()
        except Exception as e:
            self.error = f"{config.Ai_name}遇到了一点问题: {str(e)}"
            logger.error(f"调用API出现问题: {str(e)}")

class MyAi(QWidget):
    information_color = 0x777777
    user_color = 0x19A31B
    assistant_color = 0x307CC7
    system_color = 0xF00004
    def __init__(self, font_name: str | None=None):
        super().__init__()
        self.setWindowOpacity(0.9)
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint)
        self.set_style()
        QApplication.styleHints().colorSchemeChanged.connect(self.set_style)
        self.font: QFont = QFont()
        if font_name:
            self.font.setFamily(font_name)
        self.font.setPointSize(12)
        self.setFont(self.font)
        self.ui: ai_ui.Ui_Form = ai_ui.Ui_Form()
        self.ui.setupUi(self)
        self.font.setBold(True)
        self.setFont(self.font)
        self.ui.pushButton.clicked.connect(self.send)
        self.ui.lineEdit.returnPressed.connect(self.send)
        self.history: list[Any] | None = None
        self.memory: dict[Any,Any] | None = None
        self.text_browser_is_empty: bool = True
        try:
            if os.path.exists(Path(config.save_path) / config.save_history_file) and config.save_history:
                with open(Path(config.save_path) / config.save_history_file, "r", encoding="utf-8") as history_file_stream:
                    self.history = json.load(history_file_stream)
        except Exception as e:
            logger.error(f"history.json 读取失败: {str(e)}")
        try:
            if os.path.exists(config.save_path / "memory.json"):
                with open(config.save_path / "memory.json", "r") as f:
                    self.memory = json.load(f)
        except Exception as e:
            logger.error(f"memory.json 读取失败: {str(e)}")
        if self.history is None:
            self.history = []
        if self.memory is None:
            self.memory = {}
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
            logger.warning(str(e))
            return
        self.thread: AiStreamWork |None = None

    def get_ai_work(self):
        self.thread = AiStreamWork(self.client)
        self.thread.text_received.connect(self.tackle_message)
        self.thread.finished.connect(self.finish)
        self.thread.function_calling.connect(self.function_calling)

    def finish(self):
        if self.thread.error:
            self.append_system_information(self.thread.error)
            self.thread.error = ""
        else:
            self.history.extend(self.thread.this_history)
        self.thread.this_history.clear()
        if config.stream:
            self.set_send_disabled(False)
        if len(self.history) > config.historical_dialogue_limit * 2:
            self.history = self.history[-config.historical_dialogue_limit * 2:]
        self.save_history()

    def function_calling(self):
            self.append_information("正在使用工具")
            if config.stream:
                self.append_assistant_information("")

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
                self.history.clear()
                self.append_system_information("历史记录已清除")
                self.save_history()
            case x if x.strip() == "/重新开始" or x.strip().lower() == "/restart":
                self.history.clear()
                self.ui.textBrowser.setPlainText("")
                self.text_browser_is_empty = True
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
                if not self.thread:
                    self.get_ai_work()
                self.thread.prepare(self.history, [{"role": "user", "content": user_input}], self.memory)
                self.thread.start()
                if config.stream:
                    self.set_send_disabled(True)
                    self.append_assistant_information("")
        return

    def set_send_disabled(self, arg: bool):
        if arg:
            self.ui.pushButton.setDisabled(arg)
            self.ui.lineEdit.returnPressed.disconnect(self.send)
        else:
            self.ui.pushButton.setDisabled(arg)
            self.ui.lineEdit.returnPressed.connect(self.send)


    def tackle_message(self, message: str):
        # 保存对话历史（可选，用于保持上下文）
        if config.stream:
            cursor = self.ui.textBrowser.textCursor()
            cursor.movePosition(cursor.MoveOperation.End)
            self.ui.textBrowser.setTextCursor(cursor)
            self.ui.textBrowser.insertPlainText(message)
        else:
            self.append_assistant_information(message)
        return

    def append_information(self, s: str):
        self.ui.textBrowser.setTextColor(self.information_color)
        if not self.text_browser_is_empty:
            self.ui.textBrowser.append("")
        else:
            self.text_browser_is_empty = False
        self.ui.textBrowser.append(f"[提示] : {s}")

    def append_system_information(self, s: str):
        self.ui.textBrowser.setTextColor(self.system_color)
        if not self.text_browser_is_empty:
            self.ui.textBrowser.append("")
        else:
            self.text_browser_is_empty = False
        self.ui.textBrowser.append(f"[系统] : {s}")

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
                    case "tool":
                        pass
                    case _:
                        logger.error("history 出现其他值")

    def save_history(self):
        if config.save_history:
            try:
                with open(Path(config.save_path) / config.save_history_file, "w", encoding="utf-8") as history_file_stream:
                    json.dump(self.history, history_file_stream)
            except Exception as e:
                logger.exception(f"history.json 写入失败: {str(e)}")

    def memory_tool(self, action: Literal["add", "edit", "delete"], key: str, value: str = "") -> str:
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
            match action:
                case "add":
                    self.memory[key] = value
                case "edit":
                    self.memory[key] = value
                case "delete":
                    del self.memory[key]
            self.save_memory()
            return "操作成功"
        except Exception as exc:
            logger.error(str(exc))
            return str(exc)

    def save_memory(self):
        with open(config.save_path / "memory.json", "w") as memory_file_stream:
            json.dump(self.memory, memory_file_stream)

    def set_style(self):
        scheme = QApplication.styleHints().colorScheme()
        if scheme == Qt.ColorScheme.Light:
            palette = self.palette()
            palette.setColor(self.backgroundRole(), "aliceblue")
            self.setPalette(palette)
        if scheme == Qt.ColorScheme.Dark:
            palette = self.palette()
            palette.setColor(self.backgroundRole(), "#231F1A")
            self.setPalette(palette)


def main():
    app = QApplication([])
    w = MyAi()
    w.show()
    app.exec()

if __name__ == '__main__':
    main()
