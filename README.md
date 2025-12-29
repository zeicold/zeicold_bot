# zeicold_bot

FreeSimpleGUIQt 写的系统托盘程序

## 1. 安装

```bash
cd zeicold_bot
pip install .
```

## 2. 使用示例

`example/hentai_mover/hentai_mover.py` 包含了一个简单的使用示例, 用于将指定目录下的 hentai 图片包文件移动到另一个目录.

首先, 参考 [uv 文档: Installing uv](https://uv.run/docs/getting-started/installation).
然后, 安装 uv 并运行下面的命令来运行示例代码.


```bash
cd examples/hentai_mover
uv sync
uv run hentai_mover.py -h
```

这将显示帮助信息, 你可以根据需要指定源目录和目标目录.

## 3. 开发

```bash
cd zeicold_bot
uv sync
pre-commit install
pre-commit autoupdate
```
