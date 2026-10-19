# 可声明的视觉动作条件

编码同步只问“最终AAC是否保持源混音的时间”。视觉动作同步问“声音锚点对应的实际帧上，对象是否满足接触、到达、分离等条件”。两者不能互相代替。

```js
const {visualChecks}=await import('/engine/vk-checks.mjs');
window.VK_CHECKS=visualChecks(SCORE,[{
  id:'contact',event:'hit',offset:0,min:-.005,max:.005,unit:'scene m',
  description:'槌球表面与被敲物实际网格的间隙',
  measure:()=>gapFromCurrentMeshes()
}]);
```

`measure`读取`seek(t)`实际使用的对象状态或几何；不要返回理想公式/重复事件时间/固定true。数值越界、NaN、缺失事件、重复ID、范围无效都失败。事件起点默认anchor=start；可设end与offset秒。帧只在最后取整，并报告量化误差；END本身不是已编码帧，结束条件用end-1/FPS。

```powershell
python engine/render.py <project> --events
python scripts/check_visual.py <project> --require contact
# 若要求关联实际成片，还须验证其输入/事件/文件指纹：
python scripts/check_visual.py <project> --video <project>/renders/final.mp4 --require contact
```

检查器先真实seek并截图，再调用measure；截图与时间点、量化误差、测量值、单位、范围、关联事件和是否有声音一起存入review/visual-sync.json。没有条件不能显示通过，失败/输入过期不会保留旧绿色报告。

《一击之后》的最小例子在film.js：射线读取实际三角面，槌球间隙减实际半径，毡块对其面内多个截面取最早接触；检查前帧分离、当帧接触、后帧回弹。它只证实声明截面，不是通用碰撞求解/图像识别/审美评分。新增探针曾抓出旋转体绕向错误导致前表面被剔除，旧名义尺寸测试漏掉了这一点；已修正绕向，原样片保留。

模型应选对知识重要的1–几项条件，不为每个装饰写测试。遮挡、构图、材质和可理解性仍需看图；声音质感仍需听音。Agent可在技术检查后否决一个普通镜头，不能因条件变绿而停止审片。
