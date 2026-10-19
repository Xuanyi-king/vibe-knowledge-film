# Windows PowerShell 使用与验证

本地开发环境只有Linux，没有原生Windows或pwsh；原生GitHub Actions的windows-latest核心矩阵已执行，最新计数与代码身份见[最终验收](final-acceptance.md)，不能用历史成功替代新增代码的验证。可选WebGL完整导出为单独手动任务，本轮未触发；Windows的`-Scene`/`-AV`和完整地图/镜像影片生产仍未实测。

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

脚本在仓库根目录执行，逐条检查原生命令退出码，finally恢复当前目录；不修改调用者的浏览器变量。Scene模式先装固定版本可选Three，再运行测试，避免静默跳过可选测试。缓存用msvcrt内核文件锁、relative concat清单及参数数组；核心缓存/失败恢复回归已在Windows CI执行，完整Scene模式仍待实测。

下面原有36秒完整重算命令保留供需要时使用，本轮验证优先用上面的6秒入口，不必重做长片。

建片（已有 film.js 不会被无意覆盖）：

```powershell
# Agent先写好facts/direction/storyboard，决定world与完整时长；以下只演示变量传参：
$filmWorld = 'custom' # 按实际艺术方向，也可B/C
$filmSeconds = 78.5  # 示例数值，不是默认；改为完整分镜决定的时长
python scripts/new_film.py ..\my-film --world $filmWorld --duration $filmSeconds
if ($LASTEXITCODE -ne 0) { throw 'film scaffold failed' }
# 按已完成的分镜逐镜实现，内部检查后自动继续整片
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

本地实测为Linux + Chromium，另有原生Windows CI核心与PowerShell静帧验收；以上36秒重算及手工播放命令**未逐项在Windows执行**。有些系统限制脚本激活，可直接用 `.\.venv\Scripts\python.exe` 执行。

本轮公共视听组件与8秒样例：

```powershell
.\scripts\verify.ps1 -AV
Start-Process examples/resonance/audio/sfx.wav
Start-Process examples/resonance/audio/music.wav
Start-Process examples/resonance/renders/final.mp4
# 用户音乐的候选节奏分析（不自动判定downbeat/乐句）：
python scripts/analyze_music.py ..\music.wav --out ..\music-analysis.json
```

`-AV`安装可选Three，跑完整测试、确定性、8秒分段渲染、分轨、编码同步及媒体检查。关闭浏览器预览后再删除可选`engine/vendor/three`即可卸载；无npm服务/注册表改动。缓存可在停止渲染后删除工程renders/.vk-cache；不要在渲染中清理。新音频模块复用已有NumPy/SciPy和FFmpeg，无新增Python依赖。`-SkipTests`已在Windows原生执行，`-AV`尚未执行；不能将Linux完整导出成功等同Windows可选3D已验收。

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

本轮首次真实Windows CI找到并修复系统MIME映射问题：预览服务器现在显式把.js/.mjs作为JavaScript响应，不依赖Windows注册表把模块判成text/plain。测试通过真实HTTP模拟坏映射；最终原生重跑链接见最终验收。Windows CI固定Playwright Chromium；本机Google Chrome频道和可选WebGL的Windows整片仍分别列为未验证，不外推。

## 镜子与照片：本轮原创作品

沿用现有Python/FFmpeg/Playwright安装，不需要MakeHuman、Blender或新Python包。Agent选择授权真实钢琴时先准备音符，再生产；每条原生命令失败都应停止：

```powershell
python scripts/prepare_instrument.py examples/mirror examples/mirror/piano.json
if ($LASTEXITCODE -ne 0) { throw 'piano preparation failed; old bank retained' }
python scripts/produce.py examples/mirror --assets scene --chunk 4 --jobs 1
if ($LASTEXITCODE -ne 0) { throw 'film production failed; inspect review/production.json' }
Start-Process examples/mirror/renders/final.mp4
```

prepare按固定SHA下载三个CC0钢琴根音，带限离线重采样到manifest的音符；生成assets/piano不进Git。项目完整原始来源/许可保留，生成失败不替换旧bank索引。断网时已准备好的正确bank可重用；修改piano.json或准备器后要先重跑prepare，不能在准备失败后继续合成。关闭制作后可删除生成目录以及系统临时目录中的vk-music-source-v1缓存来卸载，不改注册表或音频驱动。

此前代码7403640已在原生windows-latest执行：70项中63通过、7项可选跳过，230.982秒；采样准备与共享拍点新增测试实际执行，verify.ps1 -SkipTests成功。完整镜像作品/可选Three渲染未在Windows实测。Linux同代码首次截图超时，重跑失败任务通过；不声称已修复间歇根因。详见[当前CI记录](../evidence/director-story/ci.json)。用户要求停止原创作品开发后，此处保留复现命令，不再继续样片制作。

最后小范围修复代码3994838已再次完成原生Windows核心验收：75项中68通过、7可选跳过，189.313秒，verify.ps1 -SkipTests成功；Linux同代码68通过/7跳过。新增脚手架/诊断及采样准备算法的测试实际执行。此结果仍不覆盖上列完整Three/真实钢琴bank联网下载/整片流程，也不覆盖本页原样备份命令的Windows手工执行；见[最新证据](../evidence/closeout/ci.json)。

## 曜石鎏金可选组件

旧B/C与Canvas工程不需安装新的包。按需加载vk-art文字角色时须保留正式HTML模板的字体声明；缺声明/未加载会明确失败，不能只凭磁盘字体存在认领实际字形。3D美术复用已有固定Three运行时。

```powershell
python engine/get_scene_assets.py
if ($LASTEXITCODE -ne 0) { throw 'scene runtime installation failed' }
$env:VK_SOFTWARE_GL = '1' # 仅在需要软件后端时显式选择
python -m unittest tests.test_art.CinematicTest tests.test_art.SceneAdapterTest -v
if ($LASTEXITCODE -ne 0) { throw 'cinematic component smoke failed' }
# 恢复原设置；若原来未设置，可 Remove-Item Env:VK_SOFTWARE_GL
```

14秒器具镜头的完整钢琴准备/生产/对照命令见[工程说明](../examples/torque/README.md)。本轮核心CI之后新增软件WebGL组件烟测，仅安装现有Three，不下载乐器、不生产影片；与Windows完整有声MP4导出是不同范围。实际原生结果见[美术验收](../evidence/torque/README.md)，未运行部分不外推。
