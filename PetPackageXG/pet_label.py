from .deps import *
from . import config, styles

# logging.basicConfig(level=logging.INFO)

class Direction(Enum):
    no_direction = 0
    right_down = 1
    left_down = 2
    left_up = 3
    right_up = 4

class MyPet(QLabel):
    resource_dir = config.idle
    count = 1
    timer = QTimer()
    timer_seq = 40
    end_circle = Signal()
    move_direction = Direction.no_direction
    new_x = 0
    new_y = 0
    run_arrive = False
    reverse_pic = True
    grab = False

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
        self.font = QFont()
        if font_name:
            self.font.setFamily(font_name)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground,True)
        self.setWindowFlags(Qt.WindowType.Tool | Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.pixmap = QPixmap(self.resource_dir + "1.png")
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
        if self.resource_dir == config.runback or self.resource_dir == config.runforward:
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

    def change_pixmap(self):
        pixmap_to_change = QPixmap(self.resource_dir + f"{self.count}.png")
        if self.reverse_pic:
            pixmap_to_change = pixmap_to_change.transformed(QTransform().scale(-1,1))
        self.setPixmap(pixmap_to_change)
        self.count += 1
        if not QFile(self.resource_dir + f"{self.count}.png").exists():
            self.end_circle.emit()
            self.count = 1

    def end_animate(self):
        random_1 = random.random()
        if self.resource_dir == config.idle:
            if random_1 < config.motion_probability:
                self.resource_dir = config.idle_motion
            elif config.motion_probability <= random_1 < config.motion_probability + config.run_probability:
                if self.quiet_action.text() == config.action_text.quiet_action_normal and not self.grab:
                    self.change_to_run()
        elif self.run_arrive or self.resource_dir == config.idle_motion:
            self.run_arrive = False
            self.resource_dir = config.idle

    def change_to_run(self):
        if self.screen().geometry().width() <= self.width() or self.screen().geometry().height() <= self.height():
            logging.warning("Failed to change to run")
            return
        for i in range(100):
            self.new_x = random.randint(0,self.screen().geometry().width() - self.width())
            self.new_y = random.randint(0,self.screen().geometry().height() - self.height())
            if abs(self.new_x - self.x()) >= self.width() or abs(self.new_y - self.y()) >= self.height():
                logging.info("Change to run")
                logging.info(f"New x: {self.new_x}, new y: {self.new_y}")
                break
            elif i == 99:
                logging.warning("Failed to change to run")
                return
        match self.judge_direction():
            case Direction.right_down:
                self.move_direction = Direction.right_down
                self.resource_dir = config.runforward
                self.reverse_pic = False
            case Direction.right_up:
                self.move_direction = Direction.right_up
                self.resource_dir = config.runback
                self.reverse_pic = False
            case Direction.left_down:
                self.move_direction = Direction.left_down
                self.resource_dir = config.runforward
                self.reverse_pic = True
            case Direction.left_up:
                self.move_direction = Direction.left_up
                self.resource_dir = config.runback
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
        if self.resource_dir == config.runback or self.resource_dir == config.runforward:
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