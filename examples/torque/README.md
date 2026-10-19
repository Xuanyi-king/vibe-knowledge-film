# 力的远近 · 14秒知识镜头

同一个2 N静载，沿水平杆从0.35移到0.70 m。锁角台架比较力矩，真实网格位置的叉积驱动0.70→1.40 N·m读数。落放与接触是受控编排，非自由碰撞/完整动力学实验；载荷外形不用于推断密度。

[事实与出处](facts.md) · [艺术方向](direction.md) · [认知分镜](storyboard.md) · [公开成片、对照与验收](../../evidence/torque/README.md)。完成状态以证据页实际报告为准，不由源码存在推断成片或听审通过。

当前源码包含手机返工：单一动态距离带代替三处微刻度、减少重复读数和小字、局部补光分离支撑。原版母片/静帧保持在上述证据页；[移动端前后同刻证据](../../evidence/torque/mobile/README.md)单独归档。不是新题材，也不是9:16裁切。

```powershell
python scripts/prepare_instrument.py examples/torque examples/torque/piano.json
if ($LASTEXITCODE -ne 0) { throw 'instrument preparation failed' }
python scripts/produce.py examples/torque --assets scene --chunk 3.5 --jobs 1
if ($LASTEXITCODE -ne 0) { throw 'production failed; see review/production.json' }
python examples/torque/compare.py
if ($LASTEXITCODE -ne 0) { throw 'comparison capture failed' }
Start-Process examples/torque/renders/final.mp4
```

produce完成后会自动生成review/mobile：从最终MP4抽取声明的接触前/当刻/后、3.2秒、滑移中间态、8.5/12秒停留帧，输出390/320px原始与720p/CRF30压力预览；状态仍为待真实视觉审查。另可运行`python scripts/check_mobile.py examples/torque/renders/final.mp4 --project examples/torque --profile 540p-crf33 --output examples/torque/review/mobile-strong`，不会覆盖母版。模拟参数不是抖音官方转码条件。

旧灯光baseline.html与正式index共用所有几何、运动、相机、配色、文字与score，仅对比旧studio/表面响应与新灯光/表面；倒角与排版双方都有，不假称旧版做不到。compare.py只调用正式渲染器seek截图，不替代produce或输出另一套视频。

可复用能力在engine/vk-art.mjs（文字角色/实际测量）、vk-cinematic.mjs（可配置柔光环境、灯光比例、拉丝PBR和真实倒角）；没有本片道具、剧情或音乐藏在组件内。旧B/C不加载这些模块。

HTML保留正式模板全部字体声明；自写页面不能只引入vk.js就认定字体已加载。type遇到未注册/未加载的VK字体会明确失败。磁盘get_fonts检查与页面实际字体检查分别有作用。

钢琴：Simon Dalzell/Ivy Audio录制，Versilian Studios VSCO2 CE以CC0重分发。固定源码commit与SHA在piano.json，完整许可/Info在assets。仅准备5个需要的音符，原创新编84 BPM，不复制参考片音轨。生成bank/audio/renders/review不进Git，最终短MP4与必要证据单独归档。卸载时停止渲染后可删生成目录，无新Python依赖。

技术边界：方向光PCF滤波阴影与环境PBR，不是路径追踪、真正面积光阴影、SSAO或光学景深。材质/文字/相机确定性只保证同浏览器/驱动/字体环境。完整动态与主观音乐评价的范围见证据页。

静载成立（2.7秒）时力矩标签、数值和单位一起出现；接触前/当下/回弹不显示空读数或孤立单位。物理状态、相机与score时刻不变。
