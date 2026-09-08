# a_share_quant

A 股量化学习项目。当前学习进度见 [docs/progress.md](docs/progress.md)。

## 初始化环境（Linux / Windows）

先安装 Python 3.10 或更高版本。首次安装依赖需要联网。
虚拟环境 `.venv` 是本项目独立存放 Python 和第三方工具的目录；
`requirements.txt` 记录需要安装的工具，包括处理表格的 Pandas 和绘图的 Matplotlib。

在项目根目录运行以下命令。

Linux：

```bash
python3 scripts/init_env.py
```

Windows（PowerShell 或 cmd）：

```powershell
py -3 scripts/init_env.py
```

如果 Windows 没有 `py` 命令，但 `python --version` 能正常显示版本，使用：

```powershell
python scripts/init_env.py
```

脚本会创建或复用 `.venv`、安装依赖并验证 Pandas 能否导入。
预期最后输出 Pandas 版本号和 `Environment ready.`，随后显示激活命令。
重复运行会复用现有环境；遇到不完整或来自另一操作系统的 `.venv` 会报错，
请先将该目录改名备份，再重试。脚本不会自动删除已有目录。

脚本通过自己的位置定位项目，因此也可用脚本的绝对路径从其他目录运行。
依赖目前未锁定版本，不同时间首次安装得到的版本可能不同。

## 使用环境

激活环境就是让当前终端的 `python` 命令使用项目的 Python。
初始化脚本不能替父终端完成激活，需要在项目根目录手动运行。

Linux：

```bash
source .venv/bin/activate
```

Windows PowerShell：

```powershell
.\.venv\Scripts\Activate.ps1
```

Windows cmd：

```bat
.venv\Scripts\activate.bat
```

激活后验证：

```bash
python -c "import pandas as pd; print(pd.__version__)"
```

预期输出版本号且没有报错。若 PowerShell 阻止激活脚本，
可以直接使用环境内的 Python，无需修改执行策略：

```powershell
.\.venv\Scripts\python.exe -c "import pandas as pd; print(pd.__version__)"
```

## 本次验收问题

1. 初始化结束时是否出现 `Environment ready.`？
2. 使用环境内的 Python，是否能打印 Pandas 版本号？
3. 为什么要为项目创建独立的 `.venv`？
