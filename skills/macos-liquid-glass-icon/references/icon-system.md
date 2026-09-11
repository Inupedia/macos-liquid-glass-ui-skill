# Liquid Glass Icon 设计系统

这是一套用于 AI 生图与产品方向探索的设计基线，不是 Apple 官方尺寸模板。真实 App Icon 上线前仍需使用 Apple Design Resources、Icon Composer 和 Xcode 验证。

## 1. 设计目标

一个好的 App Icon 应同时满足：

- **识别快**：缩小后仍能认出主对象；
- **品牌强**：颜色、轮廓或 motif 能和产品建立稳定联系；
- **结构简单**：2–4 个深度层足够，不靠大量装饰表现“高级”；
- **材质克制**：Liquid Glass 是材质语言，不是把所有元素都做成透明水晶；
- **可生产**：视觉概念能够拆成少量清晰图层，而不是只能存在于一张复杂 raster 图里。

## 2. 构图基线

### 画布

- 概念图使用 1:1 方形画布，默认 1024×1024。
- 主体居中，四周保留明显安全留白。
- 不主动绘制设备边框、Dock、桌面、手机或展示 mockup。
- 不在生成图里放营销文案、图标名称或水印。

### 轮廓

先设计 32–64 px 时还能辨认的 silhouette，再添加材质。

优先形态：

- 一个强主轮廓；
- 一个辅助切口、轨迹或叠层；
- 方向明确的前后层级。

避免：

- 5 个以上同权重小物件；
- 依赖细线才能理解的结构；
- 类似 UI 截图的复杂面板；
- 小尺寸后只剩一团高光的透明结构。

## 3. Layer System

默认使用 2–4 个逻辑层：

1. **Background layer**：提供品牌色场或低对比基底；
2. **Mid layer**：定义主容器、主几何或第二层语义；
3. **Foreground layer**：最关键的识别元素；
4. **Accent layer（可选）**：小范围强调，不应比主对象更抢眼。

如果一个概念无法用 4 层以内解释，先简化概念，不要直接增加层数。

### 面向 Icon Composer 的生产提醒

Apple 的 Liquid Glass 图标由系统/ Icon Composer 对图层动态施加材质效果。准备真实生产源层时：

- 不要自己预先裁出系统圆角；
- 不要把镜面高光、折射、模糊、半透明和层间阴影作为不可编辑像素效果烘焙到层里；
- 让图层本身保持干净、清晰、可拆分；
- 优先可扩展的矢量图形，无法矢量化时再使用高质量 PNG；
- 图层命名按后到前编号，例如 `01-background`, `02-shape`, `03-symbol`。

ChatGPT 生图得到的最终 PNG 可以作为视觉参考，但默认不是这些可编辑源层本身。

## 4. Liquid Glass Material

AI 概念图中可以模拟 Liquid Glass，以便快速判断方向。推荐描述：

- controlled translucency；
- subtle refraction；
- restrained specular edge highlight；
- shallow optical depth；
- soft internal light response；
- crisp silhouette despite transparency。

避免：

- chrome / mirror metal；
- jelly candy / gummy toy；
- inflated plastic bubble；
- full-scene ray-traced 3D render；
- excessive bloom / glow；
- glass so clear that the symbol disappears。

### 材质强弱

- 背景：低到中等材质感；
- 主体：中等玻璃感，保持识别；
- 小 accent：可以更亮，但面积要小；
- 边缘高光：辅助轮廓，不替代轮廓。

## 5. Color System

每个方向锁定 2–4 个核心颜色并写十六进制值。

建议角色：

- `brand-primary`：主品牌色；
- `brand-secondary`：次品牌色；
- `glass-tint`：玻璃染色；
- `accent`：小面积强调。

同一图标家族必须复用 palette，不允许每个图标独立生成“相似颜色”。

注意：透明材质会改变感知色，不要只依赖透明度制造层级；至少有一个稳定的色块或轮廓能支撑主体。

## 6. Detail Budget

默认：

- 主对象：1；
- 次级结构：1–2；
- accent：0–2；
- 纹理：尽量 0；
- 文字：0，除非字母/字标本身是品牌。

把“高级感”建立在比例、层次、材质和光学关系上，不建立在零件数量上。

## 7. Brand Adaptation

用户提供真实产品资产时，优先提取：

- 主品牌色；
- logo 中最有识别度的几何；
- UI 中反复出现的形状或 motif；
- 产品真正的核心对象；
- 已有 icon 的历史识别元素。

然后把这些元素压缩成 App Icon，而不是先选一个通用“3D 玻璃风”再给它染品牌色。

## 8. 候选方向策略

当产品概念有多种合理隐喻时，2×2 候选稿可以分别变化：

- A：最直接对象；
- B：对象 + 动作；
- C：更抽象的品牌几何；
- D：更具情绪或记忆点的隐喻。

四格必须锁定：相同 palette、材质强度、镜头/透视和细节预算。否则无法公平比较。

## 9. 不适用场景

以下情况不要强用 Liquid Glass App Icon 方法：

- 16–24 px 工具栏符号；
- 菜单、列表、表格中的功能 icon；
- 已明确要求 SF Symbols 的系统图标；
- 需要纯 SVG sprite 或 icon font 的工程资产。

这些更适合简洁矢量/系统符号体系。
