"""具有名称和描述的基类模块"""

import attrs


@attrs.define(slots=True)
class INameAndDescription:
    """具有名称和描述的基类

    - name: 名称
    - description: 描述, 如果未提供则默认为 "这是动作 {name} 的描述信息"
    """

    name: str
    """名称"""

    description: str = attrs.field(default=None)
    """描述"""

    def __attrs_post_init__(self) -> None:
        """初始化动作

        Examples:
            >>> action = INameAndDescription(name="测试动作")
            >>> action.name
            '测试动作'
        """
        if self.description is None:
            self.description = f"这是动作 {self.name} 的描述信息"
