# 小规模目标模型验证

当前未配置用于本探针的提供商凭据，**没有真实目标模型对照结果**。现有两部36秒影片的美术简报不一致，不能隔离归因于Skill。六秒Three镜头验证的是技术制作能力，不是模型能力。

`scripts/compare_skill.py`提供一个有限的单镜头实现探针：6秒曲柄滑块，两个臂收到字节相同的中性用户提示、数学条件和公共API资料；同一精确模型ID、temperature=.2、最大输出token预算、一次生成。只替换system里的Skill指导（原版commit62d5150与本分支主Skill+复杂场景指导）。两臂均可使用同一Canvas/可选Three运行时，均不获得已有样片源码或额外美术提示。

```powershell
# 填提供商实际支持的精确ID；不预设或虚构“V4.1 Flash”的API别名。
$ModelId = 'YOUR_EXACT_PROVIDER_MODEL_ID'
python scripts/compare_skill.py --model $ModelId --out ..\neutral-probe
# 默认只准备request.json、共同index.html和manifest.json，不联网、不收费。
```

在提供商账户配置好环境变量VK_MODEL_API_KEY及VK_MODEL_BASE_URL（OpenAI兼容chat/completions端点的根地址）后，再显式运行同一目录：

```powershell
python scripts/compare_skill.py --model $ModelId --out ..\neutral-probe --run
# 恰好两次生成请求，消耗提供商额度；默认每臂max_tokens=3000。
```

不把密钥写到命令、日志或请求文件。模型无关，不预设提供商或URL。旧DEEPSEEK_API_KEY/DEEPSEEK_BASE_URL仅保留可选兼容别名，不能代替显式端点。不使用OpenAI SDK。协议不支持、HTTP失败或无效JSON时停止并保留原始结果；不会自动重试增加预算。已经开始的实验不能用同一目录重跑，避免重复付费。准备后不能修改一臂的共同提示或参数；工具会拒绝不一致输入。
若使用浅克隆，原版commit不在本地，需要先`git fetch origin 62d51508aad00003dc6209afa80c4b5dc540de59`。

生成后，两臂使用相同命令和同一浏览器、字体、GPU：

```powershell
python engine/get_scene_assets.py
python engine/render.py ..\neutral-probe\original --sheet 1.5 3 4.5
python engine/render.py ..\neutral-probe\upgraded --sheet 1.5 3 4.5
# 先看实际图片；要比较动作时，两臂都做--det和--resume 2，时长均6秒。
```

manifest记录共同提示hash、实际指导文本hash、请求及返回模型ID、各臂wall time与提供商usage。实际输入长度不同，不能只凭相同max_tokens宣称总成本完全一致。两个reported_model不一致时不能作为同模型对照；未返回精确版本时保留unknown。

把输出去掉版本标识、随机排序后评审：旋转→往复是否能看懂，连杆是否闭合，遮挡/光影/构图是否帮助解释，是否像可观察的实体或有意义的图形。保留时间点与画面证据，不用亮度/颜色数评分；不要先看版本再挑赢家。

这个探针只评估一次有共同API的复杂镜头执行，不覆盖完整导演流程、长片叙事或多轮看图返工；n=1不能证明普遍提升。JSON格式失败也计作该预算下的失败，不给某一臂额外人工修图/提示。需要返工实验时，预先给两臂相同次数、相同形式的实际画面反馈，再做下一轮。

本仓库只对离线准备、无凭据不联网、以及本地假HTTP服务上的两次请求/结果记录做自动化测试；假服务token用量不是模型测量值。当前没有为节省消耗而重跑会话模型或制作两部长片。
