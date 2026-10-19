# 轻音乐：让观众有空间观察

先写声音的叙事任务，再选音色。默认可从简洁、有温度的轻音乐探索；这是起点，不是所有科学/历史题材的硬风格。钢琴、木琴、拨弦、环境或弦乐均须符合主题。

## 一张音乐弧线卡

把剧情时间写成“期待／观察／发现／思考／回到生活”，各写一个声音决定：何时新声部进入、何时撤掉低音、何时让动作独响、哪处留静默、结尾如何收束。先按乐句组织，再决定少数动作拍点；不要每句字幕都点一下音。

用听得见的具体做法替代“电影级”：开场两个音后留空；实验比较时降低伴奏密度；揭晓等观众看清再落和声；思考处允许整拍不强调；结尾回用动机，但不要把不确定科学结论配成胜利宣言。

## 可复用真实乐器路径

现有`sample`可离线播放有许可录音；现在可用小型音符bank，不必装DAW或让模型自己合成钢琴：

```powershell
python scripts/prepare_instrument.py examples/mirror examples/mirror/piano.json
python scripts/produce.py examples/mirror --assets scene --chunk 4 --jobs 1
```

这是Agent内部制作命令；主题用户无需执行或批准。准备器校验HTTPS源SHA256，采用最近采样根音的带限重采样，输出项目内FLAC与bank.json。版本身份包含manifest、准备器源码和FFmpeg版本；内容损坏、缺失音符或输入变化重建。成功后才替换bank索引，失败保留旧索引。变调同时改变录音衰减时长，不冒充复杂采样钢琴/踏板/力度层模型。

```js
import {score} from '/engine/vk-motion.mjs';
import {phrase} from '/engine/vk-music.mjs';
const bank=await (await fetch('assets/piano/bank.json')).json();
const clock=score({end:12,tempo:[{beat:0,bpm:80}]});
const events=phrase(clock,{
 id:'question',beat:0,instrument:bank,tail:1.2,gain:.14,pan:.12,
 // [相对拍号, MIDI或null休止, 持续拍数, 相对力度]
 notes:[[0,64,1,.7],[1.5,null,1],[3,67,2,.6]]
});
const SCORE=score({end:12,tempo:[{beat:0,bpm:80}],events});
```

音符跨BPM变化时按共享clock转换两端；不预先舍入毫秒。持续拍数+释放尾部可重叠，尾部受采样可用时长/片尾限制。它只编排准备好的音符，不自动创作和声，也不把每个动作量化到拍点。`SCORE.event(id)`继续驱动动作/拟音；两种编排在同一秒轴上。

[完整原创配乐](../examples/mirror/score.mjs)使用VSCO2 CE真实钢琴录音：CC0，保留Simon Dalzell/Ivy Audio与Versilian来源、固定commit、许可和文件SHA。只下载三个根音，不搬整套乐库，不复制参考片音乐。更换乐器时提供自己的来源manifest和音符集合；不要把“能下载”当作授权。

## 混音与验收

先独听music/sfx，再听合成。减少同时发声的中高频音符比单纯降低master更有用；音乐退让给阅读与动作，有意静默放进score.silence，混响余尾也受同一时间轴控制。

检查谱包络/峰值/响度/最终AAC延迟，排查爆音与失败；母带继续使用master_audio.py的编码后真峰值保护。**响度正常不证明舒服，采样真实不证明编曲动人。** 未能听音就保留分轨与混音供审查，写“主观听审未完成”。不要因参考片大声而追随它的LUFS/真峰值。

清理：关闭渲染后可删项目assets/piano生成目录及临时目录vk-music-source-v1下载缓存；源码piano.json/score.mjs/许可保留，重跑即可恢复。无系统音频驱动、注册表或新Python包。
