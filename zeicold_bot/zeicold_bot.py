"""机器人基类"""

from pathlib import Path
from threading import Thread

import attrs
import FreeSimpleGUIQt as sg
from loguru import logger

from zeicold_bot.action_status import ActionStatus
from zeicold_bot.bot_action import BotAction
from zeicold_bot.i_name_and_description import INameAndDescription


class IconNotFoundError(RuntimeError):
    """图标未找到错误"""


@attrs.define(slots=True)
class ZeicoldBot(INameAndDescription):
    """机器人基类"""

    icon: Path = Path.cwd() / "robot.ico"
    """机器人的图标路径, 默认值为当前文件夹下的 robot.ico"""

    tray: sg.SystemTray = attrs.field(init=False)
    """系统托盘对象"""

    actions: list[BotAction] = attrs.field(factory=list)
    """机器人行为列表"""

    auto_start: bool = True
    """是否自动启动机器人行为, 默认 True"""

    notify: bool = False
    """是否启用通知弹窗, 默认 False"""

    @property
    def action_status(self) -> dict[str, ActionStatus]:
        """返回所有动作的状态字典

        Returns:
            dict[str, ActionStatus]: 动作状态字典
        """
        return {a.name: a.status for a in self.actions}

    @property
    def menu(self) -> list:
        """返回菜单

        Returns:
            list: 菜单
        """
        start_stop_actions = []
        for a in self.actions:
            if a.status == ActionStatus.STOPPED:
                start_stop_actions.append(f"启动 {a.name}")
            else:
                start_stop_actions.append(f"停止 {a.name}")

        status_msg = [f"!{n}: {s.value}" for n, s in self.action_status.items()]

        if not status_msg:
            status_msg = ["!没有行为运行"]

        result = [
            "menu",
            [
                *start_stop_actions,
                "---",
                *status_msg,
                "---",
                "退出",
            ],
        ]

        return result

    def update_menu(self) -> None:
        """更新系统托盘菜单"""
        self.tray.update(menu=self.menu)

    def __attrs_post_init__(self) -> None:
        """初始化动作

        Examples:
            >>> action = ZeicoldBot(name="测试动作")
            >>> action.name
            '测试动作'
        """
        super().__attrs_post_init__()
        self.tray = sg.SystemTray(menu=self.menu, filename=str(self.icon))
        self.show_message("机器人已启动", f"机器人 {self.name} 已启动")

    def show_message(self, title: str, message: str) -> None:
        """显示弹窗消息

        Examples:
            >>> bot = ZeicoldBot(name="测试机器人")
            >>> bot.show_message("提示", "这是一个测试消息")

        Args:
            title (str): 消息标题
            message (str): 消息内容
        """
        if title in ["警告", "warning", "warn"]:
            logger.warning(f"显示消息: {title} - {message}")
        elif title in ["错误", "error", "err"]:
            logger.error(f"显示消息: {title} - {message}")
        else:
            logger.info(f"显示消息: {title} - {message}")
        if self.notify:
            self.tray.ShowMessage(title, message)

    def start(self, name: str | None = None) -> None:
        """启动机器人行为

        Args:
            name (str | None): 机器人行为名称, 如果为 None 则启动所有行为
        """
        started = []
        for a in self.actions:
            if name is not None and a.name != name:
                continue
            if a.status != ActionStatus.STOPPED:
                continue
            a.status = ActionStatus.IDLE
            Thread(target=a.start, daemon=True).start()
            started.append(a.name)
        if started:
            self.show_message("信息", f"已启动行为 {', '.join(started)}")
        else:
            self.show_message("信息", "没ile is not a zip file有找到要启动的行为")
        self.update_menu()

    def stop(self, name: str | None = None) -> None:
        """停止机器人行为

        Args:
            name (str | None): 机器人行为名称, 如果为 None 则停止所有行为
        """
        stopped = []
        for a in self.actions:
            if name is not None and a.name != name:
                continue
            if a.status == ActionStatus.STOPPED:
                continue
            a.status = ActionStatus.STOPPED
            a.stop()
            stopped.append(a.name)

        if stopped:
            self.show_message("信息", f"已停止行为 {', '.join(stopped)}")
        else:
            self.show_message("信息", "没有找到要停止的行为")
        self.update_menu()

    def run(self) -> None:
        """机器人主循环"""

        if self.auto_start:
            self.start()

        while True:
            event = self.tray.Read()
            if event == "退出":
                break

            if event.startswith("停止 "):
                action_name = event.removeprefix("停止 ")
                self.show_message("停止行为", f"正在停止行为 {action_name} ...")

                if action := next((a for a in self.actions if a.name == action_name), None):
                    action.stop()
                    self.tray.update(menu=self.menu)
                continue

            if event.startswith("启动 "):
                action_name = event.removeprefix("启动 ")
                self.start(action_name)
                continue
