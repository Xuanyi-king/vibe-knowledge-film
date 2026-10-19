# 动作、摄影机、音乐和拟音：一份时间源

先读当前分镜，不先选音效。每个重要动作写 `准备 → 接触/变化 → 反馈 → 稳定/余音`；确定观看任务和声学含义，再选组件。没有声音的动作也是有效决定。

## 先复用哪些能力

| 要解决的问题 | 公共能力 | 必须由作品决定 |
|---|---|---|
| 多对象/镜头交错与保持 | `track([[秒,值],...], t)`，值可为向量；边界clamp；重复值形成hold | 开始、落点、停留与曲线；不是所有动作都缓出 |
| 重量、反弹、次级响应 | `spring(dt,{from,to,velocity,frequency,damping})`、`impulse(dt,{velocity,frequency,damping})` | 频率Hz与阻尼比；0.3有余振，1临界，>1过阻尼；不是数值物理求解器 |
| 接触后回弹 | `contact(t,{time,from,to,lead,restitution})` → `{position,incomingSpeed}` | 预设加速接近 + 解析弹簧回退；接触速度不为零。真实自由落体/机械匀速须另用物理方程 |
| 沿曲线运动 | `path([p0,p1,p2,p3],u)` | 三次Bezier参数不是弧长；匀速需求须做弧长参数化 |
| 有目的的机位 | `camera(threeCamera, [[秒,{position,target,fov}],...], t)` | 省略fov时保持首次调用前的机位fov，乱序seek不会累积；一次移动引向一个观看目标；先保持接触可见，再移动；无需一直运镜 |
| 遮挡、曲面、光影 | [场景层](complex-scenes.md)的`solid/rod/lathe/studio/surface` | 形状比例、统一光源、粗糙度、UV尺度；不再手写法线与投影 |
| 动态文字/数值 | `track`驱动位置/透明度/数值，原`fr.text/VKit`画字 | 字号层级、阅读停顿、单位与精度。可用同运动match cut，不强制字字配音 |

全部按绝对秒计算，不依赖上一帧；同一个t乱序调用应一致。`spring`支持欠/临界/过阻尼，时间单位为秒；`frequency`是无阻尼固有频率，不能拿它冒充真实物体实测频率。

## 公共事件契约（VK_SCORE v1）

```js
const {score,contact}=await import('/engine/vk-motion.mjs');
const motion={from:1.8,to:.19,lead:.7,restitution:.35};
const S=score({end:8,fps:30,
  tempo:[{beat:0,bpm:90}], // 可增加 {beat:8,bpm:80}；拍号从0开始
  shots:[{id:'s1',start:0,end:8}],
  tracks:{sfx:{room:.08,t60:.32,highpass:45},music:{gain:[[0,.4],[2,0],[6,.4]]}},
  events:[{id:'contact',shot:'s1',beat:3,duration:3.7,object:'disc',
    action:'collision',material:'metal',position:[-.45,1.62,.02],motion,
    speed:contact(2,{time:2,...motion}).incomingSpeed,intensity:.8,
    sound:{kind:'impact',frequency:220,pan:-.15,gain:.7}}]});
window.VK_SCORE=S;
const hit=S.event('contact');
// 每帧：物体的接触、反馈、声音共读hit，不重复写2秒。
mallet.position.z=contact(t,{time:hit.start,...hit.motion}).position;
```

`event.start`为相对shot起点的秒；未设shot则全局秒。`beat`是全局拍号，不能与start同时给。`duration`含声音尾部，`end`若给则为**全局秒**。归一化输出的start/end都是全局秒。shot边界、事件ID、范围会验证。

`S.time(拍号)` / `S.beat(秒)`为分段常数BPM的双向转换；不提前取整。最后才`round(t*FPS)`或`round(t*48000)`。变速段是阶梯BPM，不支持连续tempo ramp。镜头/音乐段落也可用无sound的事件表达；不强制所有转场卡拍。

动作语义、对象、材质、位置、速度、强度为设计数据；**位置不会自动变声像**，坐标到声场的映射需符合机位。声音字段可省略。有声事件必须给正时长；不会猜测所有物体的声学模型。

## 声音制作与分轨

`render.py --events`将共享score和旧fr.sfx事件一起导出；有score时`audio.py`使用score，旧事件不再重复发声。旧工程保持原行为。

支持的原创合成方法：

- `impact`：metal/glass的非整数模态与不同衰减、wood/paper/felt短促响应，叠加材质滤波接触噪声。`intensity`控制激励。
- `friction`：滤波噪声、颗粒调制、`speed`包络控制能量。适合擦动与滑动，不冒充实录拟音。
- `whoosh`：移动气流的起落包络；不用来替代接触声。
- `pluck`：MIDI音高、衰减泛音；音乐由显式音符事件编排，**无默认Drone或自动和弦**。不要每次使用样例的五个音。
- `string`：原创Karplus–Strong延迟反馈拨弦，MIDI音高，`feedback`在(0,1)内控制延音；固定采样率产生有限音高量化，不冒充真实乐器录音。[完整地图配乐](../examples/atlas/score.mjs)给出低音/音型/退让/静默/收束的编排。
- `sample`：用户/合法素材，通过FFmpeg解码为48kHz双声道。`src`为项目内路径，必须给`license`来源记录；`trim`裁前置秒，`anchor`是裁后素材中对应画面时刻的秒，可对齐attack或peak。禁止照搬第三方统一延迟常数。采样不支持直接pitch移调，应提供处理后的源文件。

所有声源支持gain（标量或局部秒的自动化）、pan（-1..1，自动化可用）、cutoff；合成支持pitch半音。采样声像是立体声balance，中心保持原声场；合成是等功率mono pan。音轨为music/sfx/ambience；轨道gain用**全局秒**，可设置highpass/lowpass、room/t60。房间响应和各事件随机种子固定，不随事件顺序改变。

```js
// 用户BGM应进入同一分轨与参考混音；来源记录不等于已获许可。
{id:'bgm',start:0,duration:8,sound:{kind:'sample',src:'assets/music.wav',
  license:'作者/许可/来源URL/取得日期，或用户拥有权利',track:'music',gain:.18}}
```

score模式不要额外传`--bgm`；工具会拒绝以免最终混音与同步参考不同。旧事件模式的`--bgm`仍兼容。长素材显式裁长；短素材不会自动循环，按叙事需要明确安排。采样音高处理、专业多段压缩、卷积IR资产库、自动混响空间推导不是现有功能。

多轨浮点相加后仅用一个共同headroom增益保护峰值；`--stems`输出music/sfx/ambience独听。总线滤波、自动化、短房间混响后再用既有FFmpeg loudnorm合成；独听轨是处理前mastering的参考，**不会每轨分别拉满音量**。`silence:[[起,止]]`在所有轨与余音之后作用，10ms边沿防爆音，可表现有意安静。它不是自动修复混音的开关。

## 音乐选择与审查

先在direction.md写音乐的角色：脉冲/悬念/轻盈/重量/安静，以及何时让位给动作。优先使用用户音乐或有许可素材，或显式编排原创音符/节奏。不要把“有配乐”当“专业音乐已完成”。

`python scripts/analyze_music.py music.wav --out analysis/music.json`产生起音、BPM候选和1秒能量。它不识别downbeat/和声/乐句，软起音、变速、切分与半倍/双倍拍必须听取并人工标注。允许自由时间事件、J/L cut、乐句转场和不打重音的动作。

## 检查与返工

```powershell
python engine/render.py examples/resonance --motion 1.7 2.5
python engine/render.py examples/resonance --resume 2
python engine/render.py examples/resonance --events
python engine/audio.py examples/resonance --stems
python scripts/check_av.py examples/resonance
python scripts/check_media.py examples/resonance/renders/final.mp4 --duration 8 --loudness
```

`check_media --loudness`额外测量最终音轨的integrated LUFS、intersample true peak与LRA，静音测不出时返回null，不设统一响度审美目标。

`check_av`对源混音与**最终AAC解码**逐事件窗口互相关，报告编码延迟、相关度、帧量化误差；没有有效事件不能通过。无声/身份不清会失败，不假装同步。输入指纹先拒绝旧事件/旧片/被改混音，报告异常时立即作废旧绿灯。它验证编码链保留了调度，**不能从波形证明画面真的接触**；须同时看接触前/当刻/之后和Motion Strip。无声动作无需检查；声效需要豁免时给`sync:'exempt', sync_reason:'...'`并保留原因。

| 症状 | 先改什么 | 证据 |
|---|---|---|
| 接触像软着陆 | 检查到达速度、回弹和接触影；不要所有段都smoothstep | 接触前后3–5帧、速度/间隙 |
| 余振像随机抖动 | 主体静止参考、次级响应频率/衰减、触发同一事件 | 同刻乱序回放；动作条 |
| 动作正确但声音晚 | 素材内部anchor与编码延迟分开量 | 源独听轨+最终解码，不套AAC常数 |
| 音乐淹没材质 | 降音乐轨、避开该频段/时刻；先独听 | sfx/music/master对比 |
| 相机使关系难懂 | 先在接触保持，等观众看清后再靠近 | 起点/移动中/落点截图 |
| 静音被判异常 | 对照声明silence；检查前后余音与音乐返回 | 真实听音与时间表 |

[8秒完整公共能力样例](../examples/resonance/README.md)含真实渲染与局部返工。当前执行环境不能试听，故未主观验收音色、混音舒适度和完整节奏；不要用峰值/相关度代替听音。

关键动作再用[实际帧条件](action-checks.md)读真实几何间隙或实际绘制状态：`python scripts/check_visual.py <project> --video <project>/renders/final.mp4`。编码同步和声明动作条件分层，未声明的动作不在自动证明范围。
