"""主程序入口"""

from pathlib import Path

import attrs

from zeicold_bot.actions.move_hentai_action import MoveHentaiAction
from zeicold_bot.zeicold_bot import ZeicoldBot


@attrs.define(slots=True)
class MoveHentaiBot(ZeicoldBot):
    """移动 Hentai 机器人"""

    icon: Path = Path(__file__).parent / "assets/icons/robot.ico"
    """机器人图标路径"""

    name: str = "MoveHentaiBot"
    """机器人名称"""

    description: str = "一个用于自动移动 Hentai 图片的机器人"
    """机器人描述"""

    src_dir: Path = Path.home() / "Downloads"
    """Hentai 图片的源目录"""

    dst_dir: Path = Path.home() / "Pictures" / "Hentai"
    """Hentai 图片的目标目录"""

    def __attrs_post_init__(self) -> None:
        super().__attrs_post_init__()
        self.actions.append(
            MoveHentaiAction(
                bot=self,
                arg_values={
                    "src_dir": str(self.src_dir),
                    "dst_dir": str(self.dst_dir),
                    "process_once": True,
                },
            )
        )


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="启动 MoveHentaiBot 机器人")
    parser.add_argument(
        "--src-dir",
        "-s",
        type=Path,
        help="Hentai 图片的源目录, 默认 %(default)s",
        default=Path.home() / "Downloads",
    )
    parser.add_argument(
        "--dst-dir",
        "-d",
        type=Path,
        help="Hentai 图片的目标目录, 默认 %(default)s",
        default=Path.home() / "Pictures" / "Hentai",
    )
    parser.add_argument(
        "--notify",
        action="store_true",
        help="启用桌面通知功能, 默认 %(default)s",
        default=False,
    )
    args = parser.parse_args()
    bot = MoveHentaiBot(
        src_dir=args.src_dir,
        dst_dir=args.dst_dir,
        notify=args.notify,
    )
    bot.run()
