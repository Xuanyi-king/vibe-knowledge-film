# 系列母版音乐导演

当前系列唯一指定《运气的形状》参考视频实际使用的音乐；不仿作、不换曲。实际文件可用性按本次工作区和用户素材核实，不把历史[状态记录](../evidence/music-direction/shape-of-luck.json)当作当前机器必然缺文件。原视频已经找到、独立纯音乐母版已核实、公开许可已就绪，是三件不同的事。旧替代曲目讨论只留历史证据，不再进入创作候选。

## 新系列与旧工程

Agent 从主题自主完成叙事；先决定知识任务、阅读时间与镜头，再安排母版段落。新系列建片：

```bash
python scripts/new_film.py <project> --world custom --duration 150 --series shape-of-luck
```

B/C 仍可按主题选择。系列骨架生成显式锁定的 music.json，并将 MUSIC.events 合入已有 VK_SCORE；把本片 SFX/Ambience 加入同一 events 数组。缺母版、索引、剪辑许可或段落计划会阻塞生产，不降级 original/custom/platform-only。骨架加载处也核对系列身份，删除配置后重建旧 original 计划仍会失败。所有新系列作品默认使用此入口，用户不必选择技术参数。

旧 B/C 工程、无系列标记的 new_film、旧 music.json 和合法原创/采样接口保持兼容；旧无锁 signature 的历史降级行为仅用于非系列工程，不能用于本系列规避锁定。

## 取得真正母版后只建一次索引

优先独立录音。原参考 MP4 历史身份为 SHA256 456effa50dd4a65c6cb2960cd6d18129afb809fbd0bc3e8247fcc3cecb29998e、13,249,698字节、130秒；这是视频身份，绝不是音乐母版SHA。其AAC双声道44.1kHz是完整混音，起音含旧动画音效，不等于干净背景音乐。

重新提供原片时先核实真实字节/流信息，再本地提取音频；若混有音效，独立评估可选分离工具，保存工具/参数/产物SHA并实际独听残留，不能把自动分离成功当干净母版。没有工具/听审能力时标为未验收，不引入强制ML依赖。第三方原片、提取/分离轨、许可证副本仅置本地 assets/private-music（Git忽略），不公开提交。

用户明确要求使用其提供的原视频音轨作本地审看时，可制作清楚标记的参考混音预览：如实记为`reference-mix`，列出可能残留的原片SFX和实际用途，保留三轨及原录音身份。不要把这种预览写成独立母版、伪造已核实片段或改签Standard/Release认证；公开授权另外核实。没有独立母版不等于必须静音等待，也不允许悄悄换歌。

复用现有分析器的JSON作为母版索引，无第二套分析文件格式：

```bash
python scripts/analyze_music.py <master.wav> --out <master-index.json> --annotations <master-notes.json>
```

索引保留真实source_sha256、源格式source_format（原采样率/声道/codec/sample_fmt）、时长、起音/速度/节拍候选、能量与变化候选，以及绑定源SHA的人工注释。注释结构：

```json
{
  "source_sha256":"真实独立音乐SHA256",
  "reviewer":"实际核听者与方法",
  "master":{"id":"shape-of-luck","kind":"independent-music","music_only":false,"reviewer":"","evidence":""},
  "sections":[]
}
```

上例故意未验收，不能直接通过锁定。真实听审后才填 music_only:true、reviewer/evidence。分离录音用 kind:separated-music，并在确实独听检查后填 residual_sfx_checked:true。完整混音不能冒充上述类型。软件核验的是绑定与声明，不会自动鉴定曲目、授予版权或替人听审。

sections 每项包含 id、start、end、roles（如 suspense/explore/reveal/reflect/close，按叙事自由命名）、verified；需要段内裁切时列出已听审 cuts 秒数。只用 verified:true 的边界/裁切；情绪用途来自实际听审，不从RMS自动命名。beats/downbeats/phrases 沿用既有注释接口；BPM候选不是准确乐句，不能每四拍自动划段。

索引完整性与源/分析器/解码器/库/FFmpeg/确认注释身份均校验。相同母版字节与索引可复制到多部工程复用，准备阶段只核验、不重复DSP。相关身份变化会明确要求重新分析/核对，不能继续读过期锚点。分析不在 seek(t) 中运行。

## 用现有 clips 编排不同主题

music.json 沿用 end/src/source_sha256/rights/clips/anchors，额外的显式锁为：

```json
"signature":{"id":"shape-of-luck","required":true,"index":"assets/private-music/master-index.json","index_sha256":"真实索引SHA256"}
```

mode 必须 signature。rights 沿用 scope:embed 与真实 statement，另要求 allows_edit:true，以及 evidence:{src:"assets/private-music/license.txt",sha256:"真实许可凭据SHA256"}。必须先有真实的使用/剪辑许可再填写；公开发行还须实际发布授权，不能靠配置布尔值或本工具生成许可。原来的 platform-only 声明不允许导出本系列指定音乐。

每个音乐 clip 用已有 id/start（影片秒），按知识任务写 role 或指定 section。准备器选择匹配用途、优先未使用的已核实段落；默认用完整段落，显式 source_in/duration 必须匹配已核实的 cuts。不会自动截断句子、变速、移调或补循环。不合适就重新安排音乐进入/有意留白，不能为凑音乐重写论证。

有意无音乐可在 clips 中写 {id,start,duration,silence:true,reason}；它只描述 Music 留白，绝不映射到 VK_SCORE 的全局 silence（后者会影响全部轨道）。至少保留一个真实母版片段，不得用全静默冒充配乐完成。120–180秒作品可跨段取用、安排阅读留白；无足够合适段落就报告计划不足。重复源范围同时要求 allow_source_reuse:true 与 rights.allows_loop:true，并有实际重用许可；不自动 stream_loop。

标量 gain 保留旧淡入出行为。需要退让时用 clip.gain 的 [[相对秒,线性增益],...] 曲线，时间严格递增，0和duration两端增益为0；首个正增益关键点不早于fade_in，末个不晚于duration−fade_out，保证声明的淡化长度，crossfade仍受双方淡化限制。不突然放大冒充高潮，不能用全零Music冒充配乐。它映射到既有 sample.sound.gain，不增加第二条音乐时钟。

anchors 沿用显式 {id,clip,source_time}，仅映射实际选中范围；换段后旧锚点必须重新核对。准备后导入：

```js
import {MUSIC,anchor} from './assets/music-plan.mjs';
import {score} from '/engine/vk-motion.mjs';
window.VK_SCORE=score({end:150,events:[...MUSIC.events,
  {id:'contact',start:anchor('contact'),duration:.3,sound:{kind:'impact',track:'sfx'}}]});
```

索引与许可凭据也由加载器在READY前校验SHA；改配置/母版/索引/凭据都须重备。不能无条件调用不存在的anchor。节目动作接触时刻继续由同一个score管理。

## 混音与验收

始终独立 Music / SFX / Ambience。先听仅Music版，再逐项加入必要拟音；大多数移动和文字可以无声。碰撞、摩擦等声音确有叙事意义才保留，抢音乐、过尖、重复就减轻或删除，不能因事件已经登记而必须发声。Ambience也可以有意安静，避免默认轰鸣。保留三轨能力不等于要求三轨持续有声音。

Music是这一系列的听觉主体。先调整SFX的密度、音色与增益，再决定是否需要极少数音乐让位；禁止按每个动作自动duck、逐字提示或反复whoosh。完整参考混音可能已有旧SFX，不能盲叠同类声音。段落接缝、循环或变速必须确有需要并核对听感，不能为机械凑150秒破坏完整乐句。

继续运行原produce、分轨、master_audio、check_av、check_visual及媒体检查；独听music/sfx/ambience/full，实际听首尾、接缝、阅读退让、接触声与自然收束。最终AAC测响度/真峰值与编码偏移。技术通过不等于听感或艺术通过。

真实母版缺失时仅跑 tests.test_signature_music 的合成夹具：pipeline-test-only 不是指定歌曲，不作为该母版20–30秒实际验收。真实母版与许可到位后才制作20–30秒两种情绪安排的最小试听，导出Music/SFX/Full Mix，记录听审及编码结果，不必制作完整新影片。

[历史混音分析](../evidence/music-direction/README.md) · [当前阻塞输入](../evidence/music-direction/shape-of-luck.json)
