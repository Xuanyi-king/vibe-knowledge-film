# 两题心理学原始来源核查

核查日期：2026-10-19（UTC）。未修改 `/workspace/vibe-knowledge-film`。下载、网络结果及文本提取保存在 `/workspace/psychology-research/`；完整逐次 HTTP 记录见 `access-log.json`。全程保留代理和 TLS 校验，未读取凭据。HTTP 200 本身不代表拿到论文：下表明确区分挑战页面、索引摘要与实际全文。

## 实际访问与阅读范围

| 论文/入口 | 实际访问 URL | HTTP/工具结果 | 真正读到的范围 |
|---|---|---|---|
| Wegner 等，1987，PubMed 3612492 | https://pubmed.ncbi.nlm.nih.gov/3612492/ | 本地 HTTP 203；网页工具同样只读到挑战页 | 没读到 PubMed 正文或摘要，不能把这一入口写成已成功阅读全文 |
| 同文索引摘要 | https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID:3612492&format=json&resultType=core | HTTP 200，JSON | 对应 PMID 的元数据和完整摘要，`wegner1987_epmc.json` |
| 同文作者学术存档 | https://dtg.sites.fas.harvard.edu/DANWEGNER/pub/Wegner%2CSchneider%2CCarter%2C%26White%201987.pdf | HTTP 200，实际 PDF；网页工具也成功解析 | 9页，期刊页5–13；核读摘要、实验1方法/结果、实验2方法/结果和限制讨论；`wegner1987_archive.pdf/.txt` |
| Wegner，1994 | https://dtg.sites.fas.harvard.edu/DANWEGNER/pub/Wegner%20Ironic%20Processes%201994.pdf | HTTP 200，19页扫描PDF；文字提取为空 | 实际PDF已保存；核读开头理论部分（期刊页34–37，OCR/页面图像），不是声称逐页读完19页 |
| Mita、Dermer、Knight，1977，DOI | https://doi.org/10.1037/0022-3514.35.8.597 | 重定向至 doi.apa.org 后 HTTP 403；APA索引另一次也403 | 出版商入口未读到内容 |
| 同文作者ResearchGate PDF | https://www.researchgate.net/profile/Marshall-Dermer/publication/232497305_Reversed_facial_images_and_the_mere-exposure_hypothesis/links/566a2daf08aea0892c49ea00/Reversed-facial-images-and-the-mere-exposure-hypothesis.pdf | 本地下载403；网页工具成功打开并解析5页，工具不提供HTTP码 | 期刊页597–601全文，包括两个研究的方法/结果/讨论；网页工具原始返回保存在 `web2.json`、`web3.json`。不能声称本地存有此PDF |
| Ward等，2018，DOI | https://doi.org/10.1001/jamafacial.2018.0009 | 重定向至Sage后403 | 未读到出版商全文 |
| 同文PMC | https://pmc.ncbi.nlm.nih.gov/articles/PMC5876805/ | HTTP 200，但实际内容为reCAPTCHA；网页工具也返回挑战 | 不能称为成功读取PMC全文 |
| 同文作者官网PDF | https://www.ohadf.com/papers/WardWardFriedPaskhover_JAMA2018.pdf | HTTP 200，实际PDF | 3页，在线版E1–E3，完整研究信正文、图表、方法、结果、讨论；`selfie2018_author.pdf/.txt` |
| 同文Europe PMC索引 | https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID:29494735&format=json&resultType=core | HTTP 200 | PMID/DOI、作者、出版信息、关联评论索引，无摘要；`selfie2018_epmc_record.json` |

补充失败入口：旧Harvard `www.wjh.harvard.edu/~wegner/pdfs/...` 两个地址返回代理隧道403；未尝试绕过。Europe PMC全文XML接口返回500，Europe PMC网页与Rutgers机构索引本地请求403。网页搜索仅用于找到真实原文，未把媒体文章当作论文结果。

## 白熊：1987年的实验事实

原文：[Paradoxical Effects of Thought Suppression](https://dtg.sites.fas.harvard.edu/DANWEGNER/pub/Wegner%2CSchneider%2CCarter%2C%26White%201987.pdf)，*Journal of Personality and Social Psychology* 53(1), 5–13；[对应PMID摘要索引](https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID:3612492&format=json&resultType=core)。

- 实验1：34名大学生，随机分为两组，各17人；一组先抑制再表达，另一组顺序相反。先有5分钟口述练习；两个正式阶段各5分钟。参与者独处，对录音机持续说出思绪。
- 铃是真实方法：想到或说出白熊时摇铃。分析把“铃与提及同时出现”“只有铃”“只有提及”分开编码；这是行为报告，不是脑活动测量。
- 重要纠偏：后阶段 expression 明确要求“试着想白熊”，不是无指令的自由思考。可以称“解除抑制、转入表达”，若称“自由表达”必须补上仍受表达指令约束。主要反弹证据是：先抑制组在随后表达阶段的思维记录多于从开始就表达的对照组。
- 抑制时仍报告白熊，不等于“抑制越用力当下想得越多”；实验1表达阶段的记录整体高于抑制阶段。实验2加入指定替代念头（红色大众汽车）的组，其后反弹较弱，但抑制当下的侵入并未可靠减少。
- 限制：短时实验、大学生、指定中性念头、口述与自报铃；不能直接推出强迫症/创伤机制或治疗建议。作者也讨论测量和情境限制。秒数缩短的网页互动不是原实验复现，某个观众一次想到/没想到白熊不能证明或反驳群体效应。

## 白熊：1994年的机制解释是什么地位

原文：[Ironic Processes of Mental Control](https://dtg.sites.fas.harvard.edu/DANWEGNER/pub/Wegner%20Ironic%20Processes%201994.pdf)，*Psychological Review* 101(1), 34–52。

这篇文章提出解释心理控制的理论：操作过程寻找符合目标的内容；监测过程寻找不符合目标的内容，以检查是否需要继续控制。前者更依赖认知容量；容量减少时，监测可能令相反内容更容易被激活。它不主张每次控制都失败，理论也解释正常情况下成功的控制。

适合画成两股功能性活动，但应标注“理论示意”。不要画成实验已直接看到的两条脑神经通路，不要写“科学家扫描发现，大脑必定启动某个脑区”；1987的铃数据没有测量这些过程。也不要把“脑子不理解‘不要’”当作论文结论。

## 镜像偏好：1977年的证据与强度

原文：[Reversed Facial Images and the Mere-Exposure Hypothesis](https://www.researchgate.net/profile/Marshall-Dermer/publication/232497305_Reversed_facial_images_and_the_mere-exposure_hypothesis/links/566a2daf08aea0892c49ea00/Reversed-facial-images-and-the-mere-exposure-hypothesis.pdf)，*Journal of Personality and Social Psychology* 35(8), 597–601；[DOI](https://doi.org/10.1037/0022-3514.35.8.597)。

两研究都将同一底片印成镜像/普通照片，随机左右位置，比较本人和熟人的偏好。研究1有33对女性大学生与女性好友：本人21/33选镜像，好友20/33选普通，各自单独检验均未达常用显著性标准；加入4名未带好友的本人后，本人偏好显著。研究2有38名女性，其中28名带男性伴侣；每人选5次。首选时伴侣普通照片偏好仍不显著；以5次的多数偏好计，本人20/28选镜像，伴侣19/28选普通，均显著。文中p值均为单尾。

适合称“群体结果与熟悉性解释一致”，不能称“每个人都喜欢镜像、所有朋友都喜欢普通照”。样本狭窄，终生曝光次数是研究假设而非随机分配；作者承认该范式不能区分多种中介解释。偏好不是漂亮的客观测量，也不能证明某个人不喜欢照片的原因就是曝光。原文所谓true image只是普通照片朝向，不是他人眼中完整、动态、三维的‘真正的你’。

## 自拍近距透视：2018年研究讲了什么

原文：[Nasal Distortion in Short-Distance Photographs: The Selfie Effect](https://www.ohadf.com/papers/WardWardFriedPaskhover_JAMA2018.pdf)，*JAMA Facial Plastic Surgery* 20(4), 333–335；[DOI](https://doi.org/10.1001/jamafacial.2018.0009)。

这是投影几何模型，使用已有的人体测量均值，把脸近似为不同深度的平行面；不是随机分组观察大量观众满意度的试验。比较约30.48cm、约1.5m和无限距离的投影。固定颧间宽，30.48cm时模型的鼻宽相对无限远正投影约增加男性30%、女性29%；1.5m时差异接近于无。另一个7%使用的是固定鼻宽下的鼻尖相关间距，不能与前述30%当成同一测量。

不要改写为“每张自拍鼻子大30%”“近照让脸真的变形”“前置镜头坏了”。几何原因是相对距离；普通镜头的光学畸变、相机角度、光线、表情、瞬间姿态、处理/美颜、观看距离也可能影响实际照片，这篇模型没有逐项检验。论文明确说自拍是否影响满意度和医疗决策、不同垂直水平角度，还需要研究。镜像翻转与近距投影是两个变量：水平翻转不会消除距离造成的比例变化。

## 可用于叙事的演示事实与解释边界

| 主题 | 合理演示 | 可说的事实 | 不能从一位观众体验推出 |
|---|---|---|---|
| 白熊 | 先短暂提示不要想白熊，让观众按键标记出现；随后解除限制。明确这是体验环节。讲到1987时再用两个顺序不同的组呈现真正比较，表达阶段注明仍要求想白熊 | 禁止一个念头不保证它消失；原研究在先抑制者的后续表达阶段发现更多思维记录 | 按过按钮就证明发生反弹、没按说明控制更强、短演示证实理论双过程、个人有心理疾病 |
| 镜像/照片 | 使用同一张照片的水平翻转对比；另用相同面孔的近远距离投影示意，清楚标明演示图片/几何示意 | 同一底片的翻转版本曾呈现本人/熟人不同的群体偏好；相机距离也会改变相对投影比例 | 选哪张就证明熟悉性是唯一原因；普通照是他人眼里更丑/更美的你；某张自拍恰好膨胀30%；单次偏好可衡量颜值或自信 |

推荐一句话叙事：“你熟悉的朝向，可能影响你偏爱哪一张；拍摄距离，又会改变照片里的比例。”两句话的证据分别来自1977与2018研究，不能揉成一项单一心理机制。

## 本地审计文件

- `access-log.json`：实际本地HTTP、最终地址、文件和字节数。下载时间为本次会话，日期见本报告开头。
- `web1.json`–`web4.json`：网页工具完整返回，包括1977论文五页提取文本。工具未提供HTTP状态的地方本报告没有补造。
- `wegner1987_archive.pdf/.txt`、`wegner1994_archive.pdf`、`wegner1994-page-01...04.png/.txt`、`selfie2018_author.pdf/.txt`：获取到的论文及阅读提取。
- 原始挑战/失败HTML也保留，便于区分“收到页面”与“读到论文”。
