# Windows PowerShell 使用与验证

在仓库根目录，安装 Python 3.10+、Git 和 FFmpeg（含 ffprobe），并将它们加入 PATH。

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
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
