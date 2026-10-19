# 事实、推导与边界

本次输入只有`brief.txt`的一句主题，没有外部提供分镜、美术、音乐或技术路线。当前Agent自主选择下面的范围；这是一次完整制作实践，不是模型能力的随机对照实验。

核心问题不是“哪幅地图最真实”，而是为什么保局部角度与保面积需要不同取舍。球面模型下，纬度φ的纬圈周长为2πR cosφ；60°时为赤道一半。柱面投影x=Rλ把经线画成等距直线，东西尺度k_x=secφ。

Mercator的y=R ln tan(π/4+φ/2)，导数dy/dφ=R secφ，因此南北尺度k_y=secφ。60°的微小区域，长度两个方向均2倍，面积4倍。这是**局部微分尺度、赤道真尺度的球面模型**，不是声称任意大小国家面积精确放大4倍。保角也不等于所有大轮廓/距离不变。

Lambert柱面等面积（赤道标准纬线）y=R sinφ，k_y=cosφ；k_x k_y=1，但60°局部形状横向2倍、纵向1/2，圆变椭圆。中间投影形变仅作变化演示，不把所有中间态命名为标准投影。

来源：

- [Snyder 1987, USGS Professional Paper1395, Map projections: A working manual](https://pubs.usgs.gov/publication/pp1395)，DOI10.3133/pp1395。其概要明确不同投影的保角/等面积用途。PDF在本环境网页工具403，**没有假称已阅读全文**。
- [USGS: How are different map projections used?](https://www.usgs.gov/faqs/how-are-different-map-projections-used)：等面积图形状有失真，不能一概把某投影称为最真实。
- [D3地理投影文档](https://d3js.org/d3-geo/cylindrical)及实际读取的3.1.1 `src/projection/mercator.js`、`cylindricalEqualArea.js`、`orthographic.js`。上列公式与实现一致；尺度导数在源码测试中独立验算。
- 海岸线是[Natural Earth110m land](https://www.naturalearthdata.com/about/terms-of-use/)，public domain。固定commit/hash和许可由`engine/get_geo_assets.py`记录。只使用陆地，不加入政治边界或未经核实地名数字。

不讨论椭球细节、具体国家面积、所有投影分类或地图政治史；正射地球是球面可视化，不是卫星照片。相同经纬格并非相同地表面积，影片不会把它们混淆。用无穷小圆的局部尺度图解释定量值，真实海岸线负责空间识别。

球面不能不伸缩地摊平成平面，是所有地图存在失真的背景事实（上述USGS说明）。本片用两种柱面投影揭示具体的尺度取舍，**不是高斯曲率定理的完整证明**，也不声称两种投影涵盖所有方法。
