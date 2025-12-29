"""移动 Hentai 文件的机器人示例"""

import shutil
import time
from functools import cached_property
from pathlib import Path
from typing import Any
from zipfile import ZipFile

import attrs
import json5
from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer
from watchdog.observers.api import BaseObserver

from zeicold_bot.bot_action import BotAction
from zeicold_bot.zeicold_bot import ZeicoldBot


# FileSystemEventHandler 和 attrs.define 冲突
class MoveHentaiHandler(FileSystemEventHandler):
    """移动 Hentai 文件的文件事件处理器"""

    bot: ZeicoldBot
    """所属机器人实例"""

    src_dir: Path
    """源目录, 用于监控文件变化, 默认下载目录"""

    dst_dir: Path
    """目标目录, 用于存放移动后的文件"""

    process_once: bool = True
    """是否确保每个文件只处理一次, 默认 True"""

    # pylint: disable-next=too-many-positional-arguments,too-many-arguments
    def __init__(
        self,
        bot: ZeicoldBot,
        dst_dir: Path,
        src_dir: Path = Path.home() / "Downloads",
        process_once: bool = True,
    ) -> None:
        super().__init__()
        self.bot = bot
        self.dst_dir = dst_dir
        self.src_dir = src_dir
        self.process_once = process_once

    @cached_property
    def processed_files(self) -> list[Path]:
        """只读属性, 处理过的文件列表, 防止重复处理, 仅在 process_once 为 True 时启用

        Returns:
            list[Path]: 处理过的文件列表
        """
        return []

    @cached_property
    def supported_suffixes(self) -> tuple[str, ...]:
        """只读属性, 支持的文件后缀名

        Returns:
            tuple[str, ...]: 支持的文件后缀名
        """
        return (".jpg", ".jpeg", ".png", ".gif", ".webp")

    def on_modified(self, event: FileSystemEvent) -> None:
        """文件修改, 创建时执行的事件

        Args:
            event (FileSystemEvent): 文件系统事件
        """
        file_path = Path(event.src_path).resolve(strict=False).absolute()  # type: ignore
        if self.process_once:
            if file_path in self.processed_files:
                return
            self.processed_files.append(file_path)
        zip_name = file_path.name
        if file_path.suffix.lower() != ".zip":
            return

        # 解析压缩包内的信息
        try:
            with ZipFile(file_path, "r") as zip_ref:
                # 检查压缩包中是否 90% 文件都是图片
                has_info_json = False
                total_pics = 0.0
                total_files = float(len(zip_ref.namelist()))
                for file_name in (n.lower() for n in zip_ref.namelist()):
                    if file_name == "info.json":
                        has_info_json = True
                    if file_name.endswith(self.supported_suffixes):
                        total_pics += 1.0

                if total_pics / total_files < 0.5:
                    msg = f"压缩包 {file_path} 不是图片包, 图片文件比例过低 ({total_pics}/{total_files})"
                    self.bot.show_message("错误", msg)
                    return

                if has_info_json:
                    info_jsons = zip_ref.read("info.json").decode("utf-8")
                    info_json_dict = json5.loads(info_jsons)
                    if "gallery_info" not in info_json_dict:  # type: ignore
                        self.bot.show_message("警告", f"压缩包 {file_path} info.json 中缺少 gallery_info")
                    else:
                        zip_name = str(info_json_dict["gallery_info"]["source"]["gid"]) + ".zip"  # type: ignore
                else:
                    self.bot.show_message("警告", f"图片压缩包 {file_path} 缺少 info.json 文件")
        except Exception as e:  # pylint: disable=broad-except
            self.bot.show_message("错误", f"处理 zip 文件 {file_path} 失败: {e}")
            return

        # 移动文件到目标目录
        dest_path = self.dst_dir / zip_name
        shutil.move(file_path, dest_path)
        self.bot.show_message("信息", f"已将图片 {file_path.name} 移动到 {dest_path}")


@attrs.define(slots=True)
class MoveHentaiAction(BotAction):
    """移动 Hentai 文件的机器人行为, 用于添加在机器人 `ZeicoldBot` 中"""

    name: str = "MoveHentaiAction"
    """行为名称"""

    description: str = "一个用于自动移动 Hentai 图片的行为"
    """行为描述"""

    args: dict[str, type] = attrs.field(
        init=False,
        default={
            "src_dir": str,
            "dst_dir": str,
            "process_once": bool,
        },
    )
    """行为参数类型字典"""

    arg_values: dict[str, Any] = attrs.field(factory=dict)
    """行为参数值字典"""

    handler: MoveHentaiHandler = attrs.field(init=False)
    """文件事件处理器"""

    observer: BaseObserver = attrs.field(init=False)
    """文件系统观察者"""

    @property
    def src_dir(self) -> Path:
        """源目录, 默认下载目录

        Returns:
            Path: 源目录
        """
        return Path(self.arg_values.get("src_dir", Path.home() / "Downloads"))

    @property
    def dst_dir(self) -> Path:
        """目标目录, 默认用户图片目录下的 Hentai 子目录

        Returns:
            Path: 目标目录
        """
        return Path(self.arg_values.get("dst_dir", Path.home() / "Pictures" / "Hentai"))

    def __attrs_post_init__(self) -> None:
        """初始化移动 Hentai 行为"""
        super().__attrs_post_init__()
        self.handler = MoveHentaiHandler(
            bot=self.bot,
            src_dir=self.src_dir,
            dst_dir=self.dst_dir,
            process_once=self.arg_values.get("process_once", True),
        )

    def start(self) -> None:
        self.observer = Observer()
        self.observer.schedule(self.handler, str(self.src_dir), recursive=True)
        self.observer.start()
        self.bot.show_message(
            "信息",
            f"已启动移动 Hentai 行为, 监控目录: {self.src_dir}, 目标目录: {self.dst_dir}",
        )
        super().start()
        try:
            while True:
                time.sleep(1)
        finally:
            self.stop()

    def stop(self) -> None:
        self.observer.stop()
        self.observer.join()
        del self.observer
        super().stop()


@attrs.define(slots=True)
class MoveHentaiBot(ZeicoldBot):
    """移动 Hentai 机器人"""

    icon: Path = Path(__file__).parent / "robot.ico"
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
    hentai_mover_bot = MoveHentaiBot(
        src_dir=args.src_dir,
        dst_dir=args.dst_dir,
        notify=args.notify,
    )
    hentai_mover_bot.run()
