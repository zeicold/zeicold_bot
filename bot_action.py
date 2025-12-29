"""机器人动作基类模块"""

from abc import abstractmethod
from typing import Any

import attrs

from zeicold_bot.action_status import ActionStatus
from zeicold_bot.i_name_and_description import INameAndDescription


@attrs.define(slots=True)
class BotAction(INameAndDescription):
    """机器人动作基类, 每一个 Action 都包含

    - bot 属性, 用于表示所属的机器人实例
    - status 属性, 用于表示动作的当前状态
    - start 方法, 用于启动动作
    - stop 方法, 用于停止动作
    """

    bot: "ZeicoldBot" = attrs.field(default=None)  # type: ignore[forward-references]
    """所属机器人实例"""

    args: dict[str, type] = attrs.field(factory=dict)
    """行为参数字典, 用于存储行为的配置信息"""

    arg_values: dict[str, Any] = attrs.field(factory=dict)
    """行为参数值字典, 用于存储行为的配置信息值, key 为参数名, value 为参数值.
    Zeicold Bot 可以通过该字典来获取行为的配置信息
    # TODO: ZeicoldBot 需要提供一个界面来让用户配置这些参数
    """

    status: ActionStatus = attrs.field(init=False, default=ActionStatus.STOPPED)
    """动作状态, 默认 `ActionStatus.STOPPED`"
    """

    @abstractmethod
    def start(self) -> None:
        """启动动作"""
        self.status = ActionStatus.IDLE
        self.bot.show_message("信息", f"动作 {self.name} 已启动")

    @abstractmethod
    def stop(self) -> None:
        """停止动作"""
        self.status = ActionStatus.STOPPED
        self.bot.show_message("信息", f"动作 {self.name} 已停止")
