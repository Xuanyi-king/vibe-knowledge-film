# 地理画面：复用投影而非重画海岸线

用于真实地理位置、球面与地图尺度；不是所有题材的默认视觉母题。

```powershell
python engine/get_geo_assets.py
```

```js
const G=await import('/engine/vk-geo.mjs');
const A=await G.loadAtlas(); // 固定版本本地D3和Natural Earth；离线渲染
const p=G.cylindrical(0).scale(225).translate([960,540]);
G.paintMap(ctx,A,p); // 海陆、海岸线、经纬网；D3球面裁剪和自适应采样
const k=G.localScale(60,0); // {x:2,y:2,area:4}：球面模型的局部微分尺度
```

`cylindrical(morph)`在Mercator与赤道标准纬线的Lambert柱面等面积投影之间插值；0/1是端点，中间状态是演示性投影，不是新的命名标准。`localScale`给数学比例；画面放大示意须明确位置、单位和基准，不可用微分比例声称任意大小国家面积精确放大四倍。

正射地球用`A.d3.geoOrthographic()`；投影的scale/translate/rotate/clipExtent由绝对时间驱动。同一海岸线或经纬母题形成连续性，同尺度比较不可为了填版分别fitSize。设计意图是让观众观察局部尺度的变化，不是装饰转场。检查中间态，数值不能提前显示最终结论；独立放大图须标明原位置并与地图连线。

安装器逐文件SHA256校验D3及数据，保留完整许可证。依赖位于忽略的engine/vendor/geo，可在停止渲染后删除卸载；旧Canvas/Three工程无需安装。D3不提供3D材质、卫星照片、政治边界或地名事实核验。

[完整原创作品](../examples/atlas/README.md)展示这种能力怎样服务推理。失败例与同刻返工见[evidence](../evidence/atlas/review.md)。
