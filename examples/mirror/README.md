# 另一种你

主题：为什么镜子里的你，有时比照片好看？112秒、16:9、无旁白，以两次揭盲区分朝向熟悉与拍摄距离，最后回到同一张人像。

[有声影片与证据](../../evidence/mirror/README.md) · [事实与边界](facts.md) · [分镜](storyboard.md) · [艺术/声音方向](direction.md)

一张原创AI生成的虚构肖像，仅作水平翻转。它不是用户或1977研究参与者；不拿个人选择证明群体效应。独立灰色三维头模型只用于投影，不冒充2018论文平均脸或前段人物。

## 可复现制作（Bash或PowerShell）

在仓库根目录，先按主README安装Python/FFmpeg/Playwright及字体：

```powershell
python scripts/prepare_instrument.py examples/mirror examples/mirror/piano.json
python scripts/produce.py examples/mirror --assets scene --chunk 4 --jobs 1
# Windows下任一命令失败立即停止：
if ($LASTEXITCODE -ne 0) { throw 'production failed; see examples/mirror/review/production.json' }
```

Bash应分别检查退出码或使用`set -e`；PowerShell每条原生命令后检查`$LASTEXITCODE`。最终输出`examples/mirror/renders/final.mp4`，分轨在audio/，声明条件/媒体/生产报告在review/。不依赖Blender、MakeHuman程序、npm服务或浏览器CDN。Three为当前工程已有可选版本。

单独预览与检查：

```powershell
python engine/render.py examples/mirror --serve
python engine/render.py examples/mirror --sheet 2 17 36 40 67 73 100 110
python engine/render.py examples/mirror --motion 57.5 68
python scripts/check_visual.py examples/mirror --video examples/mirror/renders/final.mp4 --require same-pixels-reversed self-count partner-count near-camera completed-ending
python scripts/check_av.py examples/mirror
```

修改任何项目输入后重跑produce；它会重导事件并按内容失效缓存，不能把旧events或final认领为新版。新版准备器本身变化时先重跑prepare；bank索引持久且按准备器/manifest/FFmpeg版本失效。不要同时编辑/准备资产和渲染。

## 复用方法

`portrait.mjs`读取已许可的面部网格，用现有vk-scene建立真实相机/光照；近远对照不改变网格/姿态。投影标记读取实际BufferGeometry与相机矩阵，脸颊参照归一化；当前模型比值不是论文30%。照片对照来自同一画布的水平像素翻转；vk-image公共放置器保持原比例，镜框和照片不拉瘦或拉宽人像。

`score.mjs`调用公共`phrase`编排真实钢琴音符，并让照片移动/翻转/相机靠近共读SCORE事件。它不是新的独立视频引擎；替换剧情/对象/音乐时保持共享时钟即可。

模型数据`assets/portrait.json`为MakeHuman hm08 CC0图形资产的肩上裁取。`build_portrait.py`可从固定源SHA重建；不包含或复制AGPL程序代码。`assets/person.png`为本轮imagegen生成，来源记录在assets/provenance.json。钢琴原录音仅下载固定三个CC0根音，生成目录不进Git，完整许可证保留。

技术检查、抽样动态检查、完整观看与主观听音分别记录在证据页。不能把技术通过称为电影/音乐质量通过；本例也不是普通模型能力提升的隔离实验。
