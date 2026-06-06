from .setting.deps import *
from .setting import config, styles
from .setting.config import logger

class PetState(Enum):
    idle = 0
    motion = 1
    run_forward = 2
    run_back = 3

class Direction(Enum):
    no_direction = 0
    right_down = 1
    left_down = 2
    left_up = 3
    right_up = 4

class MyPet(QLabel):
    count = 0
    timer = QTimer()
    timer_seq = 40
    end_circle = Signal()
    move_direction = Direction.no_direction
    new_x = 0
    new_y = 0
    run_arrive = False
    reverse_pic = True
    grab = False
    animation_path = {
        PetState.idle: config.idle,
        PetState.motion: config.idle_motion,
        PetState.run_forward: config.runforward,
        PetState.run_back: config.runback
    }
    pixmap_dict: dict[PetState, list[QPixmap]] = {}

    def __init__(self, font_name=None):
        super().__init__()
        self.oldpos = self.pos()
        self.icon = QIcon(config.datafile + config.logo_file)
        self.setWindowIcon(self.icon)
        self.show_action = QAction(self, text=config.action_text.show_action, icon=self.icon)
        self.reset_action = QAction(self, text=config.action_text.reset_action, icon=self.icon)
        self.quiet_action = QAction(self, text=config.action_text.quiet_action_normal, icon=self.icon)
        self.chat_action = QAction(self, text=config.action_text.chat_action, icon=self.icon)
        self.music_action = QAction(self, text=config.action_text.music_action, icon=self.icon)
        self.quit_action = QAction(self, text=config.action_text.quit_action, icon=self.icon)
        self.menu = self.get_menu()
        self.menu.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.menu.setWindowFlags(self.menu.windowFlags()
                            | Qt.WindowType.FramelessWindowHint
                            | Qt.WindowType.NoDropShadowWindowHint)
        self.font = QFont()
        if font_name:
            self.font.setFamily(font_name)
        self._pet_state = PetState.idle
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground,True)
        self.setWindowFlags(Qt.WindowType.Tool | Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.load_pixmap()
        self.pixmap = self.pixmap_dict[PetState.idle][0]
        self.petheight = self.pixmap.height()//2+1
        self.width_divide_height = self.pixmap.width()/self.pixmap.height()
        self.reset_pet()
        self.setScaledContents(True)
        self.set_tray_icon()
        self.end_circle.connect(self.end_animate)
        self.timer.timeout.connect(self.change_pixmap)
        self.timer.start(self.timer_seq)
        self.set_right_click()
        self.setStyleSheet(styles.pet_label_style)
        self.menu.setFont(self.font)

    def set_right_click(self):
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)

    def show_context_menu(self,point):
        if (self.get_pet_state == PetState.run_back or self.get_pet_state == PetState.run_forward) and not self.run_arrive:
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

    def load_pixmap(self):
        if not self.pixmap_dict:
            for key, value in self.animation_path.items():
                count = 1
                self.pixmap_dict[key] = []
                while QFile(value + f"{count}.png").exists():
                    self.pixmap_dict[key].append(QPixmap(value + f"{count}.png"))
                    count += 1

    def change_pixmap(self):
        pixmap_to_change = self.pixmap_dict[self.get_pet_state][self.count]
        if self.reverse_pic:
            pixmap_to_change = pixmap_to_change.transformed(QTransform().scale(-1,1))
        self.setPixmap(pixmap_to_change)
        self.count += 1
        if self.count >= len(self.pixmap_dict[self.get_pet_state]):
            self.end_circle.emit()
            self.count = 0

    def end_animate(self):
        random_1 = random.random()
        if self.get_pet_state == PetState.idle:
            if random_1 < config.motion_probability:
                self.set_pet_state(PetState.motion)
            elif config.motion_probability <= random_1 < config.motion_probability + config.run_probability:
                if self.quiet_action.text() == config.action_text.quiet_action_normal and not self.grab:
                    self.change_to_run(*(self.get_random_position()))
        elif self.run_arrive or self.get_pet_state == PetState.motion:
            self.run_arrive = False
            self.set_pet_state(PetState.idle)

    def get_random_position(self):
        if self.screen().geometry().width() >= self.width() and self.screen().geometry().height() >= self.height():
            for i in range(100):
                new_x = random.randint(0,self.screen().geometry().width() - self.width())
                new_y = random.randint(0,self.screen().geometry().height() - self.height())
                if abs(new_x - self.x()) >= self.width() or abs(new_y - self.y()) >= self.height():
                    logger.info("Change to run")
                    logger.info(f"New x: {new_x}, new y: {new_y}")
                    return new_x, new_y
        logger.warning("Failed to get random position")
        return None

    def change_to_run(self, x, y):
        self.new_x = x
        self.new_y = y
        match self.judge_direction():
            case Direction.right_down:
                self.move_direction = Direction.right_down
                self.set_pet_state(PetState.run_forward)
                self.reverse_pic = False
            case Direction.right_up:
                self.move_direction = Direction.right_up
                self.set_pet_state(PetState.run_back)
                self.reverse_pic = False
            case Direction.left_down:
                self.move_direction = Direction.left_down
                self.set_pet_state(PetState.run_forward)
                self.reverse_pic = True
            case Direction.left_up:
                self.move_direction = Direction.left_up
                self.set_pet_state(PetState.run_back)
                self.reverse_pic = True
        self.timer.timeout.connect(self.move_run)

    def judge_direction(self):
        if self.new_x - self.x() > 0:
            if self.new_y - self.y() >= 0:
                return Direction.right_down
            else:
                return Direction.right_up
        else:
            if self.new_y - self.y() >= 0:
                return Direction.left_down
            else:
                return Direction.left_up

    def move_run(self):
        speed = self.width() / 40
        if self.new_y - self.y() != 0:
            delta_x_divide_delta_y = abs((self.new_x - self.x())/(self.new_y - self.y()))
            angle = math.atan(delta_x_divide_delta_y)
            speed_x = round(speed*math.sin(angle))
            speed_y = round(speed*math.cos(angle))
        else:
            speed_x = speed
            speed_y = 0
        if self.move_direction == Direction.right_down:
            self.move(self.x() + speed_x, self.y() + speed_y)
        elif self.move_direction == Direction.left_down:
            self.move(self.x() - speed_x, self.y() + speed_y)
        elif self.move_direction == Direction.left_up:
            self.move(self.x() - speed_x, self.y() - speed_y)
        else:
            self.move(self.x() + speed_x, self.y() - speed_y)
        if abs(self.x() - self.new_x) <= self.width()/10 or abs(self.x() - self.new_x) <= 10 or self.judge_direction() != self.move_direction:
            self.run_arrive = True
            self.timer.timeout.disconnect(self.move_run)

    def lick_paw(self) -> str:
        """桌宠小光：舔一次爪子"""
        if self.grab:
            return "用户正在使用鼠标抓着桌宠小光"
        self.set_pet_state(PetState.motion)
        return "成功"

    def run_to_position(self, relative_x: float, relative_y: float) -> str:
        """桌宠小光：逐步跑动到相对坐标的位置[x,y]，相对坐标取值范围[0,1], 屏幕左上角为[0,0]"""
        try:
            if self.grab:
                return "用户正在使用鼠标抓着桌宠小光"
            elif 0 <= relative_x <=1 and 0 <= relative_y <=1:
                self.change_to_run(relative_x * (self.screen().geometry().width() - self.width()),
                                   relative_y * (self.screen().geometry().height() - self.height()))
                return "成功"
            else:
                return "相对坐标不在0到1内"
        except Exception as e:
            logger.error(str(e))
            return str(e)

    def set_mode(self, mode: Literal["quiet", "normal"]) -> str:
        """桌宠：跑动设置
        - normal：随机跑动
        - quiet：不随机跑动"""
        if mode == "quiet":
            self.quiet_action.setText(config.action_text.quiet_action_quiet)
        elif mode == "normal":
            self.quiet_action.setText(config.action_text.quiet_action_normal)
        else:
            return "没有这个选项"
        return "成功"

    def set_pet_state(self, state: PetState):
        self.count = 0
        self._pet_state = state
        return

    @property
    def get_pet_state(self):
        return self._pet_state

    def set_tray_icon(self):
        tray_icon = QSystemTrayIcon(self)
        tray_icon.setIcon(self.icon)
        tray_icon.activated.connect(lambda reason:(self.show() if reason == QSystemTrayIcon.ActivationReason.Trigger else 0))
        tray_icon.show()
        tray_icon.setContextMenu(self.menu)

    def get_menu(self):
        menu = QMenu(self)
        menu.setObjectName("DIY_menu")
        self.show_action.triggered.connect(self.show_hide_act)
        self.reset_action.triggered.connect(self.reset_pet)
        self.quiet_action.triggered.connect(self.quiet_mode)
        self.quit_action.triggered.connect(QApplication.exit)
        menu.addAction(self.show_action)
        menu.addAction(self.reset_action)
        menu.addAction(self.quiet_action)
        menu.addAction(self.chat_action)
        menu.addAction(self.music_action)
        menu.addAction(self.quit_action)
        return menu

    def show_hide_act(self):
        if self.isHidden():
            self.show()
        else:
            self.hide()

    def quiet_mode(self):
        if self.quiet_action.text() == config.action_text.quiet_action_quiet:
            self.quiet_action.setText(config.action_text.quiet_action_normal)
        else:
            self.quiet_action.setText(config.action_text.quiet_action_quiet)

    def reverse_pixmap(self):
        self.reverse_pic = not self.reverse_pic

    def mousePressEvent(self,event):
        if event.buttons() == Qt.MouseButton.LeftButton or event.buttons() == Qt.MouseButton.MiddleButton:
            self.oldpos = event.globalPosition().toPoint()
            self.grab = True
        if (self.get_pet_state == PetState.run_back or self.get_pet_state == PetState.run_forward) and not self.run_arrive:
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

    def mouseReleaseEvent(self, ev, /):
        self.grab = False

def main():
    app = QApplication([])
    w = MyPet()
    w.show()
    app.exec()

if __name__ == '__main__':
    main()