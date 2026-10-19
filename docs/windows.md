# Windows PowerShell 使用与验证

本地开发环境只有Linux，没有原生Windows或pwsh。新增GitHub Actions的ubuntu-latest/windows-latest核心矩阵，实际运行状态和链接统一列在[最终验收](final-acceptance.md)；未运行的任务不能当通过。Windows核心任务还执行本文件的PowerShell验证入口；可选WebGL完整导出为单独手动任务。

在仓库根目录，安装 Python 3.10+、Git 和 FFmpeg（含 ffprobe），并将它们加入 PATH。

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
$env:PYTHONUTF8 = '1' # Python3.10–3.14一致的UTF-8工程/日志环境
python -m pip install -r requirements.txt
python -m playwright install chromium
python engine/get_fonts.py
python engine/get_fonts.py --check
ffmpeg -version
ffprobe -version
```

有本机 Google Chrome 时默认使用它；没有时使用 Playwright Chromium。可显式选择：

```powershell
$env:VK_BROWSER = 'C:\Program Files\Google\Chrome\Application\chrome.exe'
# 删除覆盖设置：Remove-Item Env:VK_BROWSER
```

检查显式路径：`Test-Path $env:VK_BROWSER`。不存在时删除该覆盖变量，渲染器会优先本机Chrome，再尝试Playwright Chromium；路径错误不会悄悄换浏览器。首次安装后可运行：

```powershell
.\scripts\verify.ps1
# 包括可选3D镜头、持久恢复重复运行和音画合成，只渲6秒：
.\scripts\verify.ps1 -Scene
# 无可用GPU/WebGL2时可显式尝试软件后端，再执行上面的Scene验证：
$env:VK_SOFTWARE_GL = '1'
```

脚本在仓库根目录执行，逐条检查原生命令退出码，finally恢复当前目录；不修改调用者的浏览器变量。Scene模式先装固定版本可选Three，再运行测试，避免静默跳过可选测试。缓存用msvcrt内核文件锁、relative concat清单及参数数组；这些Windows分支仍待Windows机器实测。

下面原有36秒完整重算命令保留供需要时使用，本轮验证优先用上面的6秒入口，不必重做长片。

建片（已有 film.js 不会被无意覆盖）：

```powershell
python scripts/new_film.py ..\my-film --world custom
# 写好 facts.md / direction.md / storyboard.md，再按镜头实现 film.js
python engine/render.py ..\my-film --serve
```

直接验证本次原创样片：

```powershell
python -m unittest discover -s tests -v
python engine/render.py examples/descent_studio --sheet 5.5 10.5 17 24.5 30
python engine/render.py examples/descent_studio --motion 8.8 13.2
python engine/render.py examples/descent_studio --det
python engine/render.py examples/descent_studio --jobs 3
if ($LASTEXITCODE -ne 0) { throw 'render failed' }
python engine/render.py examples/descent_studio --events
if ($LASTEXITCODE -ne 0) { throw 'events failed' }
python engine/audio.py examples/descent_studio
if ($LASTEXITCODE -ne 0) { throw 'audio failed' }
python scripts/check_media.py examples/descent_studio/renders/final.mp4 --duration 36 --output examples/descent_studio/review/media.json
if ($LASTEXITCODE -ne 0) { throw 'media validation failed' }
Start-Process examples/descent_studio/renders/final.mp4
```

原版回归：

```powershell
python engine/render.py examples/fold_C --det
python engine/render.py examples/pigeon_B --det
python engine/render.py examples/fold_C --clip 23 26 join
python engine/render.py examples/pigeon_B --clip 29 32 arrival
```

`--clip` 用主时间轴，输出中第0秒仍对应所选起点。不要直接用全片事件音给局部 clip 合音；先重渲全片再合片。
确定性只保证同一浏览器/字体版本/平台；跨 Windows 与 Linux 可能出现抗锯齿差异。

本次实测环境是 Linux + Chromium；以上为 PowerShell 兼容命令，**未在 Windows 主机执行**。有些系统限制脚本激活，可直接用 `.\.venv\Scripts\python.exe` 执行。

本轮公共视听组件与8秒样例：

```powershell
.\scripts\verify.ps1 -AV
Start-Process examples/resonance/audio/sfx.wav
Start-Process examples/resonance/audio/music.wav
Start-Process examples/resonance/renders/final.mp4
# 用户音乐的候选节奏分析（不自动判定downbeat/乐句）：
python scripts/analyze_music.py ..\music.wav --out ..\music-analysis.json
```

`-AV`安装可选Three，跑完整测试、确定性、8秒分段渲染、分轨、编码同步及媒体检查。关闭浏览器预览后再删除可选`engine/vendor/three`即可卸载；无npm服务/注册表改动。缓存可在停止渲染后删除工程renders/.vk-cache；不要在渲染中清理。新音频模块复用已有NumPy/SciPy和FFmpeg，无新增Python依赖。此PowerShell入口仍未在Windows原生执行，不能将Linux成功等同跨平台已验收。

## 完整自主作品与当前版本检查

Agent负责主题、资料、剧本和艺术决定；用户不需要按阶段审批。源文件完成后可一次执行：

```powershell
python scripts/produce.py examples/atlas --assets geo --chunk 4 --jobs 1
if ($LASTEXITCODE -ne 0) { throw 'production failed; read review/production.json' }
Start-Process examples/atlas/renders/final.mp4
# 单独复查声明的实际绘制条件（不是通用语义识别）：
python scripts/check_visual.py examples/atlas --video examples/atlas/renders/final.mp4 --require four-area one-area end-complete
```

历史无指纹导出须保留后重新渲染/导事件/合音，不能把旧audio/events.json认领为新film.js。输入编辑后请重跑生产入口；--resume按内容复用合法段。相同时长与FPS不代表相同版本。生成目录audio/review/renders不可放输入素材。

可选地理依赖为本地固定D3与Natural Earth数据，无浏览器CDN请求；卸载时关闭预览后删除engine/vendor/geo。核心CI不强制安装地理或Three，因此会明确跳过对应可选测试；本地完整验收需先安装。完整作品的WebGL之外地理分支由Linux本地实际导出验证。
