"""状态枚举类模块"""

from enum import StrEnum


class ActionStatus(StrEnum):
    """状态枚举类"""

    STOPPED = "已停止"
    IDLE = "空闲"
    PROCESSING = "处理中"
    SUCCESS = "成功"
    FAILURE = "失败"
    TIMEOUT = "超时"
