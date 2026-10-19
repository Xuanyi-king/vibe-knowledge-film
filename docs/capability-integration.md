# 本轮开源能力融合记录

先复用已完成的导演/审片/渲染研究，只补读视听与复杂场景。下列commit固定本轮实读版本，未根据Star判断优劣；没有复制这些项目的音视频、logo、纹理或源码段落。引入的唯一可选运行时仍是已验证的Three.js，不安装另一套视频框架。

| 项目 / commit | 实读入口与实现 | 采用的机制 / 取舍 | 许可处理 |
|---|---|---|---|
| [javascript-animation-skills](https://github.com/iart-ai/javascript-animation-skills) `f7d0882` | javascript-animation的starter.html、render.mjs、storyboard；soundtrack的score/groove模板、sync-check.mjs、真实示例HTML | 共享EVENTS/SHOTS/SECTIONS、离线样本调度、音乐/SFX bus、seeded room → VK_SCORE+NumPy。无须增加OfflineAudioContext渲染链。实跑原sync-check空cues会0/0退出0，故新检查拒绝空检查；不移植±100ms万能阈值、单HTML和所有动作卡拍 | MIT ©2026 iart.ai；仅方法参考 |
| [video-shotcraft](https://github.com/Vincentwei1021/video-shotcraft) `310c1bc` | music-beat-sync、sound-design、aesthetic-rules、guided-free-creation；shots/camera/space-camera-moves；assets/lib和camera demo | shot-local声音、素材内部峰值与编码偏移分开、机位/构件共享进度、合片后回测。固定音量、强制卡拍和广告镜头次数限制不作为通用规则 | Apache-2.0；不复制参考正文/实现/音效；assets/audio不可统一视为MIT |
| [remotion-motion-graphics-skill](https://github.com/Liamrjohnston/remotion-motion-graphics-skill) `b860c79` | cinematic-camera/SKILL；motion-graphics的visual-critic与critic-output | 连续世界、focal/zoom同时间轴、hold→move→hold；保留观看目标与真实帧评审。不移植固定版式、禁止发光/暗背景或必须匹配品牌素材的个人约束 | MIT ©2026 Promptible；仅方法参考，未复制商标与样片 |
| [motion-design-skills](https://github.com/iart-ai/motion-design-skills) `3c129f7` | animation-principles十二原则/curves、art-direction playbook、composition、beat-sync、color、background、logo | 把预备/接触/反馈/停稳、PURPOSE/HERO/TRANSITION/BEAT变成分镜任务与诊断；拍点末端取整。非成熟动画运行库；不移植持续动、禁linear、最多两曲线等硬限制 | MIT ©2026 iart.ai；仅方法参考 |
| [video-motion-craft](https://github.com/vibegameengine/video-motion-craft) `c17ab30` | motion-laws/beat-sync/sound-design/remotion-patterns/review-checklist、gen-sfx及NOTICES | 借鉴空档/转场叠压/编码失败复查；同步方法追溯shotcraft，不重复归因。SFX仍有Math.random，不当确定性实现；不照搬统一提前2–3帧 | 原创MIT，相关参考为Apache-2.0派生；未复制 |
| [webgl-animation-skills](https://github.com/iart-ai/webgl-animation-skills) `50697d6` | threejs/particle/shader Skill、resource-disposal、particle-recipes、showcase、probe-mp4 | 绝对mixer.setTime/u_time、seed属性、资源生命周期；现有场景层可接入。粒子fixed-step末尾越步须修，不新增无需求粒子/Shader框架 | MIT ©2026 iart.ai；仅方法参考 |
| [motion-canvas](https://github.com/motion-canvas/motion-canvas) `7b91435` | core/tweening/spring.ts及测试，flow/all.ts、sequence.ts、tween.ts | 并发/交错编排思想→绝对事件；120Hz状态积分spring不直接移植，自己实现标准阻尼振子解析解，可任意seek | MIT ©2022 motion-canvas；未复制runtime |
| [remotion-dev/skills](https://github.com/remotion-dev/skills) `1441a11` | remotion-best-practices；remotion-markup timing/audio/sequencing/audio-visualization | 局部时间、边界clamp、显式trim与自动化。当前路径已重组；无须React/Remotion适配器 | checkout无LICENSE且package无license字段，**不复制代码/正文**；不推断为MIT |
| [marketing-videos](https://github.com/sub-level/marketing-videos) `696073f` | GeometryWords/SfxCue/MusicBed、example/script、gotchas、device-stage、audio README | 同一叙事数据、多轨gain关键帧、先更新相机材质再提交帧、持续主体。没有引入R3F；不强制一曲音乐或固定三层音量 | 源码MIT ©2026 Sub Level；配乐另有商业许可，不复制资产 |

实际落地：`engine/vk-motion.mjs`（解析运动/tempo/score/camera）、`score_audio.py`（材质激励/样本/分轨/自动化）、`check_av.py`（编码回测）、`analyze_music.py`（保守分析候选），统一接入原render.py/audio.py。组件是本任务原创实现，公开算法与方法不是第三方资产授权。

验证见[8秒样例](../examples/resonance/README.md)与[修订记录](pr1-revision.md)。仅“读过参考”的能力不列为已实现；自动downbeat、语义乐句、完整物理仿真、任意3D资产加载、实时WebAudio试听仍是扩展方向。

## 地图完整制作的定向补充

没有重复九仓库调研。新增D3地理算法解决真实海岸线、球面裁剪和投影形变，取代每次手写整套地图图形算法；不引入D3动画计时器。实际读3.1.1的mercator/cylindricalEqualArea/orthographic实现并验证导数与球面多边形绕序，全部本地确定性驱动。d3-geo3.1.1+d3-array3.2.4与Natural Earth110m数据共约208KB（含许可），不安装整套D3或独立框架。固定版本/散列由get_geo_assets.py管理；[许可](../THIRD_PARTY_NOTICES.md)、[调用与失败经验](../references/cartography.md)。

音乐复用Karplus–Strong公开方法补充可衰减拨弦，不加入新DSP依赖；与现有score、分轨和同步共用。实际原创24小节配乐用于72秒作品，尚不能从技术检测推断听感专业。未实现自动作曲审美、自动downbeat/乐句、通用地理事实核验或电影级后期库。
# 曜石鎏金增量

复用已固定Three r180的MeshPhysicalMaterial各向异性/PMREM/PCF及ExtrudeGeometry倒角，提供可选美术适配；文字角色复用Frame.text/measure，验证页面实际字体，不新建排版引擎。未再次调研九个仓库、未引入包、未复制外部道具/音乐。真实对照、条件与边界见[evidence/torque](../evidence/torque/README.md)。
