# 从主题到成片：执行策略与恢复

创作与验收原则以 [SKILL](../SKILL.md) 为准，本页只解释工具边界。主题即任务开始；简单记录可合在 `review/notes.md`，复杂研究/导演文档按需展开。先明确问题与证据，尽早试画高风险概念，再完成全片叙事，不要求固定候选数、表格数或返工轮数。

## 选择当前所需成本

```bash
python scripts/new_film.py <project> --world custom --duration <预计全片秒数>
python scripts/produce.py <project> --mode draft               # 默认 sheet 16
python scripts/produce.py <project> --mode draft --stills 2 8.5
python scripts/produce.py <project> --mode draft --motion 8 10
python scripts/produce.py <project> --mode draft --clip 8 11    # renders/draft.mp4，无声
python scripts/produce.py <project> --mode standard
python scripts/produce.py <project>                            # 默认 release
```

| 策略 | 自动执行 | 报告与含义 |
|---|---|---|
| Draft | 字体/显式可选依赖、选定预览；无参数生成全片拼图 | review/draft.json，preview_needs_review；不修改正式 production.json 或 final.mp4 |
| Standard | 检查作品能力、确定性、resume全片、事件、分轨、母带、适用音频/动作同步、完整媒体检查 | standard_complete_needs_release_and_review；仍未发行/主观验收 |
| Release | Standard + 最终编码手机尺寸/压力证据 | technical_complete_needs_subjective_review；实际看图/观看/听音后才判断交付 |

`--assets geo scene` 仅在用到时指定，下载器会复用本地资产。字体安装器自身只下载缺项。`--chunk 4 --jobs 1` 旧参数保留。旧 Python 调用 `produce(project, chunk, jobs, assets)` 默认 Release，底层所有渲染命令继续可用。

Draft 不能作为单主题任务默认最终交付。只调构图用静帧，动作/转场用 Motion Strip，速度与动态问题再渲局部片段；不需要为一帧执行 Release。全片首次生产用 Standard，交付前用 Release；直接执行默认命令也可完成全部技术链。

新工程 `world` 由 Agent 显式决定，custom 要求正数 duration，可在试画后修改。显式 B/C 旧命令保留带警告的 30 秒骨架；已有工程无需迁移，骨架不是作品。

## 复用已有结果

生产入口不建立新的任务编排系统，只在 `review/production-cache.json` 保存两组已成功结果：Standard 技术链与手机证据。每次先写 running，再准备音乐/字体/依赖，读取当前作品与运行时身份；符合以下全部条件才复用：

- 当前全部本地输入与引擎 SHA256 一致，包括字体、可选依赖、事件源码和 Markdown。素材必须放 assets，不能依赖生成目录或联网素材/符号链接。
- 生产脚本、requirements、Python/系统、NumPy/SciPy/Pillow/Playwright 版本、浏览器版本/路径、场景后端、软件 GL、FFmpeg/ffprobe 版本和分段参数一致。
- 事件、原始画面、final、侧车、参考混音/分轨、媒体/同步报告与检查图片字节全部匹配；手机证据还绑定当前 final。缺文件、损坏记录或内容变化均失效。
- 结束时重新验证源码稳定、事件/视频身份和适用报告指向同一 final。没有指纹的历史导出不能自动认领为当前输入。

复用报告明确区分 `stages`（本轮执行）、`reused` 和耗时，不把未执行检查写成重跑通过。Standard→Release 可直接补手机证据；手机图片损坏只重做手机组。中断仍依赖已有 resume 分段恢复；当前实现不对改过的 JS 做逐镜依赖推断，源码变化保守重跑。`review/notes.md` 不作为输入，避免写制作笔记使画面失效；真实浏览器输入不要放在 review。

复用是本地缓存，不是防恶意篡改签名，也不支持多个 produce 同时写同一工程。需要强制重新测量时可删除 `review/production-cache.json`，底层 resume 仍校验缓存段，不能手改摘要获得“通过”。

## 失败与验收

入口逐步写 active_stage；中断不会遗留上轮成功。合音前备份旧 final/侧车，后续失败回滚，硬中断查 production.json 的备份路径；磁盘破坏不在事务保证内。失败记录不得当发行许可。

`VK_SCORE` 触发编码音频同步检查，`VK_CHECKS` 触发实际帧声明条件检查，无声明时明确 not_declared。两者都不等于通用动作识别、知识准确或审美评分。母带从参考混音做恒定增益与 AAC 后峰值验收；旧 fr.sfx 保留，旧外混 BGM 不自动假定在参考混音里。

Release 从最终编码生成 390/320px 原图与压力副本，须实际看图并按问题返工。压力参数不代表抖音官方转码。完整观看、独听分轨与成片听审分别声明；环境无法执行就记未验收，不能用正常响度代替舒适听感。

外部配乐只在根 music.json 存在时准备，复用 VK_SCORE；[音乐导演](music-direction.md)保留合法素材、自选原创与平台授权边界。无可用候选不阻塞原创制作，不另造音乐时间轴。

[动作与相机组件](choreography.md) · [视觉动作探针](action-checks.md) · [真实审片](review.md) · [手机布局](mobile.md) · [Windows](../docs/windows.md)
