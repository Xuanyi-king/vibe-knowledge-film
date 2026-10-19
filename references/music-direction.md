# 音乐参与导演，不接管知识

只在外部音乐/音乐驱动作品需要时加载。简单作品继续使用现有 `phrase`、真实钢琴音符和 `VK_SCORE`；没有新音频引擎或必需依赖。

## 按主题选择

先确定主题所需的情绪、节奏与静默，再选择原创或合法素材。系列候选 **We Never — Hi Noise** 仅在气质合适且有本地可用文件与实际授权时考虑，无需每次重新研究其身份。参考片是否使用它目前**未确认**；曲名、文件名和BPM都不是音频身份鉴定。选择它时须有适当授权，但不能挤压知识、手机阅读和独立艺术判断。

- `signature`：适合且有合法本地资产时使用；无资产/授权不可用时自动回到原创或已授权替代，不中断全片。
- `original`：继续现有原创编曲/授权录音路径，不固定BPM、乐器或高潮位置。准备器不会替Agent创作音符。
- `custom`：用户指定可嵌入的音乐；缺文件/授权时明确失败，Agent应另选合适方案再继续。
- `rights.scope: platform-only`：仅输出平台添加的剪辑提示，不嵌入该曲；Agent使用现有分轨能力导出音效版并在交付中说明需要平台添加。库中有歌不代表获得任意商业、改编或跨平台权利。

授权由用户/资产记录声明，不是程序鉴定。商业原曲放本地 `assets/private-music/`（Git忽略），不要提交、上传参考片或把其提取音轨作为配乐再分发。发布成片也须在实际授权范围内。

## 准备一次，所有镜头共享

```powershell
python scripts/analyze_music.py <project>/assets/private-music/song.wav --out <project>/review/music/analysis.json
# Agent核对候选与听感后，写入项目根music.json
python scripts/prepare_music.py <project>
python scripts/produce.py <project>
```

`produce`只在存在`music.json`时预备音乐；历史工程不变。配置、资产或剪辑修改后重新prepare，再重新导出事件和成片，不能沿用旧events。正式渲染期不做DSP。底层直接render时，导入适配器同样在READY前校验计划、配置和音源三种指纹。

最小配置（以下指纹/授权必须替换为真实值；秒数由导演决定，不是系列默认）：

```json
{
  "mode":"signature", "track":"用户指定的候选曲名", "end":14,
  "src":"assets/private-music/song.wav", "source_sha256":"实际文件SHA256",
  "rights":{"scope":"embed","statement":"实际来源、许可及使用范围"},
  "clips":[{"id":"opening","start":0,"source_in":2,"duration":14,"fade_in":0.4,"fade_out":1,"gain":0.25}],
  "anchors":[{"id":"discovery","clip":"opening","source_time":9.8}]
}
```

工程已有`assets/music-plan.mjs`后，在原score模块中组合，不创建第二个时钟：

```js
import {MUSIC,anchor} from './assets/music-plan.mjs';
import {score} from '/engine/vk-motion.mjs';
export const SCORE=score({end:14,events:[...MUSIC.events,
  {id:'discovery',start:anchor('discovery'),action:'computed-answer'}]});
```

文件位置决定相对import；以上假设score模块在项目根。画面通过 `SCORE.event('discovery').start` 使用同一时刻，声明关键动作条件到`VK_CHECKS`；音频仍是现有sample事件/混音器。`anchor`只做显式源秒→影片秒映射，不偷偷吸附到机器拍点。original降级没有外部锚点，Agent需改用自身score事件；不能无条件调用不存在的anchor。

`prepare(project, config)`第一次可初始化根`music.json`；已有文件时必须先显式保存配置，再传同样内容。CLI `--config`只能初始化或匹配已有规范配置，不静默覆盖它。生成JSON/加载器中断不一致时会拒绝渲染，重跑即可。配置即使只改排版也需重备，这是保守失效。

## 候选不是乐理事实

分析保留源SHA、实现/解码器/库/FFmpeg身份、秒单位、两类周期估计、多个半拍/双拍候选、相位候选、起音、1秒能量/起音密度、局部周期和段落变化候选。完整混音的首次活动不是配乐开始；音效可污染起音。算法不自动确认拍号、强拍、乐句、高潮、速度变化或歌曲身份。

确实听/核对后，可用`--annotations`提供绑定source_sha256与reviewer的beats/downbeats/phrases；少数校正点不等于整张网格通过，只有明确`complete_grid:true`才声明完整网格已核对。换音源、改变播放速度、修改分析方法/注释均失效缓存；损坏输入保留旧分析但报错，不认领为新结果。

## 把音乐变成故事结构

分镜写短的“知识任务—可用音乐段—动作锚点—阅读停留—声音留白”。先保证推理成立和手机文字读完，再利用前奏建立疑问、稳定段陪伴实验、乐句变化承接新理解。揭晓可用和声/配器变开阔、轻微重音或短暂停顿，不能一律增大音量。每拍不必动、每字幕不必响、每镜不必切。提前铺垫→落定→观察可跨数拍。

裁切必须显式填写源入点/时长/淡入出。相邻段重叠不能超过双方淡化；同一源段重复需`allow_source_reuse:true`且`rights.allows_loop:true`，仍须实际听审乐句衔接。程序不自动寻找可循环点，不用stream_loop，不自动变速。不好剪就换曲，不能让一行字幕中间重启音乐。

最终独听music/sfx/full，听首尾、接缝、静默、重要读数和接触声；母带峰值/响度、编码波形同步、声明视觉条件分别检查。任何技术通过都不能替代听感、导演品质和实际平台验收。

[真实参考分析与未确认边界](../evidence/music-direction/README.md) · [现有14秒音乐/画面证据](../evidence/torque/mobile/README.md)
