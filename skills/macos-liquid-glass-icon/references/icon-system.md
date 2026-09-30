# Liquid Glass Icon 设计系统

这是一套用于 AI 生图与产品方向探索的设计基线，不是 Apple 官方尺寸模板。真实 App Icon 上线前仍需使用 Apple Design Resources、Icon Composer 和 Xcode 验证。

适用范围：**iOS / iPadOS / macOS 的 1024×1024 方形分层 App Icon**。watchOS / tvOS / visionOS 规格不同（详见 [SKILL.md](../SKILL.md) §8），不要套用本文尺寸基线。

## 1. 设计目标

一个好的 App Icon 应同时满足：

- **识别快**：缩小后仍能认出主对象；
- **品牌强**：颜色、轮廓或 motif 能和产品建立稳定联系；
- **结构简单**：2–4 个深度层足够，不靠大量装饰表现“高级”；
- **材质克制**：Liquid Glass 是材质语言，不是把所有元素都做成透明水晶；
- **外观一致**：6 种系统外观下保持同一 metaphor、轮廓和特征；
- **可生产**：视觉概念能够拆成少量清晰图层，而不是只能存在于一张复杂 raster 图里。

## 2. 构图基线

### 画布

- 概念图使用 1:1 方形画布，默认 1024×1024。
- 主体居中，四周保留明显安全留白。
- 不主动绘制设备边框、Dock、桌面、手机或展示 mockup。
- 不在生成图里放营销文案、图标名称或水印。

### 轮廓

先设计 **16–64 px** 时还能辨认的 silhouette，再添加材质。

优先形态：

- 一个强主轮廓；
- 一个辅助切口、轨迹或叠层；
- 方向明确的前后层级。

避免：

- 5 个以上同权重小物件；
- 依赖细线才能理解的结构；
- 类似 UI 截图的复杂面板；
- 小尺寸后只剩一团高光的透明结构。

小尺寸的可判定阈值（最小笔画宽度、对比下限、色差容差）见 [验收清单](validation.md) §3。

## 3. Layer System

默认使用 2–4 个逻辑层（Icon Composer 的 group 上限也是 4，不要规划第 5 层）：

1. **Background layer**：品牌色场或低对比基底，**只用纯色或渐变，不加材质感**；
2. **Mid layer**：定义主容器、主几何或第二层语义；
3. **Foreground layer**：最关键的识别元素，材质主要在这里表达；
4. **Accent layer（可选）**：小范围强调，不应比主对象更抢眼。

如果一个概念无法用 4 层以内解释，先简化概念，不要直接增加层数。

### 面向 Icon Composer 的生产提醒

Apple 的 Liquid Glass 图标由系统 / Icon Composer 对图层动态施加材质效果。准备真实生产源层时：

- 不要自己预先裁出系统圆角；
- 不要把镜面高光、折射、模糊、半透明和层间阴影作为不可编辑像素效果烘焙到层里；
- **背景层不要加材质**：只给纯色或渐变；
- **导出前移除背景色与渐变**，背景在 Icon Composer 里用 solid color / gradient 重建（官方说明背景层支持纯色和渐变，多数情况不必导入自定义背景图）；
- 若确实要自导入背景图：必须 **full-bleed 且 opaque**，否则会被系统材质和留白裁掉；
- 让图层本身保持干净、清晰、可拆分；
- 优先可扩展的矢量图形（SVG 或 PDF），无法矢量化时再使用高质量 PNG；SVG 不保留字体，文字必须转轮廓，不支持的特性改用 PNG；
- 图层最多 4 个 group，z 轴从后到前；
- 图层命名要**有意义 + 从后到前编号**，例如 `01-background`、`02-shape`、`03-symbol`、`04-accent`。

宿主生图得到的最终 PNG 可以作为视觉参考，但默认不是这些可编辑源层本身。

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

- **背景：不加材质**，纯色或渐变；不要给背景加玻璃、光泽或纹理；
- 主体：中等玻璃感，保持识别；
- 小 accent：可以更亮，但面积要小；
- 边缘高光：辅助轮廓，不替代轮廓。

### 由系统处理、不要烘焙的效果

镜面高光（specular highlights）、折射（refraction）、模糊、层间阴影、圆角遮罩、半透明合成，都由系统 / Icon Composer 在图层之上动态施加。概念图里的这些效果只用于判断方向，**不要写进交付源层**。

版本差异：早于 27 的系统上，选择 Inside 或 Outside 时 specular highlights 常开，且 Refraction 设置没有可见效果——这是预期行为，不算缺陷，也**不需要**为它改图层。

## 5. Color System

每个方向锁定 2–4 个核心颜色并写十六进制值。

建议角色：

- `brand-primary`：主品牌色；
- `brand-secondary`：次品牌色；
- `glass-tint`：玻璃染色；
- `accent`：小面积强调。

同一图标家族必须复用 palette，不允许每个图标独立生成“相似颜色”。

注意：透明材质会改变感知色，不要只依赖透明度制造层级；至少有一个稳定的色块或轮廓能支撑主体。

交付时色彩空间从 HIG 允许的三项里选一并在 brief 里写明：**sRGB / Gray Gamma 2.2 / Display P3**。优先矢量（SVG 或 PDF）。位深与 alpha 要求以提交渠道现场文档为准（见 [验收清单](validation.md) §9）。

## 6. Detail Budget

默认：

- 主对象：1；
- 次级结构：1–2；
- accent：0–2；
- 纹理：尽量 0；
- 文字：0，除非字母/字标本身是品牌。

把“高级感”建立在比例、层次、材质和光学关系上，不建立在零件数量上。

这份预算同时是 QA 判据：超出即不通过，先删细节再谈材质（见 [验收清单](validation.md) §3）。

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

输出规格：**总画布 1024×1024，每格 ≥512 且格间留可见间距**，保证复现结果可预期；确定方向后必须用单图重生成，不要从宫格截图裁切当最终稿。

## 9. 外观变体（Appearance Variants）

iOS / iPadOS / macOS 的 App Icon 有 6 种系统外观，全部要覆盖：

| 外观 | 在 Icon Composer 中的位置 | 设计要点 |
| --- | --- | --- |
| default | 主外观选择器 | 基线：完整色彩与材质关系 |
| dark | 主外观选择器 | 不换隐喻，压暗背景色场，主体对比仍要够 |
| clear light | Mono → Options | 依赖系统材质与背景，靠形状和高光读出主体 |
| clear dark | Mono → Options | 同 clear light，深色下轮廓不要被背景吞掉 |
| tinted light | Mono → Options（Tinted 开关 + tint 色） | 单色化，靠明度层级而不是色相区分主次 |
| tinted dark | Mono → Options（Tinted 开关 + tint 色） | 同上，检查 tint 后主体与背景仍有对比 |

Icon Composer 的主外观选择器只给出 **default / dark / mono**；clear 与 tinted 藏在 **Mono → Options**（Light/Dark 切换、Tinted 开关和 tint 色）。

硬性要求：

- 6 种外观必须保持**同一 metaphor、同一轮廓、同一特征**，只改变表现方式，不换主体；
- clear / tinted 下不要靠“再画一版”解决，靠层级和明度关系；
- 镜面高光、折射、模糊、层间阴影、圆角遮罩、半透明合成一律由系统处理，不要烘焙进层里；
- 早于 27 的系统上 Refraction 无可见效果属预期，验收要按目标系统版本分别进行（见 [验收清单](validation.md) §8）。

## 10. 不适用场景

以下情况不要强用 Liquid Glass App Icon 方法：

- 16–24 px 工具栏符号；
- 菜单、列表、表格中的功能 icon；
- 已明确要求 SF Symbols 的系统图标；
- 需要纯 SVG sprite 或 icon font 的工程资产。

这些更适合简洁矢量/系统符号体系。
