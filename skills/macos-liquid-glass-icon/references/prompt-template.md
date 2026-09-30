# ChatGPT Image Prompt 模板

目标：让宿主的图像生成能力直接产出 Liquid Glass App Icon 概念图或定稿，不经过外部 API。

## 1. 单个 App Icon

把方括号替换成真实内容；不要原样保留占位符。

```text
Create one polished app icon artwork for [product/app name], a [one-sentence product purpose].

Core metaphor: [one clear object/action].
Silhouette: [simple outer shape that stays recognizable at small size].
Layer structure: [background], [mid layer], [foreground], optional [small accent]. Keep the depth structure clear and limited to 2–4 layers. The background layer must be a plain solid color or a simple gradient — no glass, gloss or texture on the background.

Use this locked palette:
- primary: [#HEX]
- secondary: [#HEX]
- glass tint: [#HEX]
- accent: [#HEX, optional]

Visual direction: premium Apple-platform app icon, Liquid Glass-inspired material with controlled translucency, subtle refraction, restrained specular edge highlights, shallow optical depth, and crisp edges. The material should support the symbol, not obscure it. Keep the design simple, memorable, and brand-specific rather than generic 3D glass.

Composition: one single square 1024×1024 px canvas, centered subject, generous safe margin, strong readable silhouette, balanced depth, no tiny decorative details. It must remain recognizable at 64 px, 32 px and hold its main silhouette at 16 px.

This artwork is a visual concept only. Do not bake in specular highlights, refraction, blur, rounded-rectangle masking or inter-layer shadows as fixed pixel effects; those are applied later by the system.

Avoid: text, letters, labels, fake letters, watermark, UI screenshot, device mockup, desktop/Dock scene, busy background, photoreal environment, chrome, gummy candy, inflated plastic, excessive glow, excessive reflections, noisy texture, clutter.

Output only the icon artwork, no presentation frame or caption.
```

## 2. 2×2 候选方向

只在概念歧义明显时使用。四格要比较“隐喻/构图”，不要同时比较四种完全不同的视觉风格。

输出规格固定，保证复现可预期：**总画布 1024×1024，四格 2×2，每格 ≥512×512 且格间留可见间距**。

```text
Create a 2×2 concept sheet containing four alternative app icon directions for [product/app name], a [purpose].

Output canvas: one single 1024×1024 px image containing a 2×2 grid of four square app icon concepts. Each cell must be at least 512×512 px, with a visible gutter between cells; keep every concept fully inside its own cell, centered, with generous inner margin.

All four concepts must use the exact same brand system:
- palette: [HEX list]
- Liquid Glass material strength: [low/medium]
- perspective: [front-facing / slight dimensional depth]
- detail budget: minimal
- overall sophistication and rendering quality: identical

Only vary the central metaphor/composition:
A. [direct object]
B. [object + action]
C. [abstract brand geometry]
D. [memorable symbolic metaphor]

Each cell must contain one centered square app icon concept. Keep every concept readable at small size. The background of each concept is a plain solid color or simple gradient — no material, gloss or texture on the background. Do not bake in specular highlights, refraction, blur or inter-layer shadows as fixed pixel effects.

No labels inside the icon artwork, no text, no letters, no watermark, no device mockup, no UI screenshot, no decorative background scene, no caption outside the grid.
```

候选图只用于选择方向。确定方向后必须重新生成单图，不要直接从宫格截图裁切当最终 icon。

## 3. 基于现有图标做 Liquid Glass 改造

如果用户提供了原图，使用图像编辑能力，并把“保留项”和“修改项”分开写清楚。

```text
Edit the provided app icon while preserving its core identity.

Must preserve:
- [logo/symbol silhouette]
- [brand colors or recognizable geometry]
- [specific composition element]

Change only:
- simplify small details for 32–64 px readability;
- reorganize the artwork into 2–4 clear depth layers;
- introduce restrained Liquid Glass material cues: subtle translucency, refraction, and edge highlights;
- improve depth separation and contrast;
- [requested color/material change].

Keep the background as a plain solid color or simple gradient; do not add glass, gloss or texture to the background, and do not bake specular highlights, refraction, blur or inter-layer shadows into the artwork — those come later from the system.

Do not replace the icon with a different metaphor. Do not add text, letters, watermark, device mockup, extra objects, busy backgrounds, chrome, gummy/plastic styling, or excessive glow.
```

## 4. 图标家族

先写共享 style spec，再为每个图标只替换 `metaphor`。

```text
Generate one icon in an existing app-icon family.

Shared family spec — do not change:
- palette: [HEX values]
- silhouette language: [description]
- layer count: [N, max 4]
- perspective: [description]
- Liquid Glass strength: [description]
- edge/radius language: [description]
- accent rule: [description]
- detail budget: [description]
- appearance behaviour: [same metaphor and silhouette across default/dark/clear/tinted]

This icon's concept only:
[name] — [single concrete metaphor]

Match the family exactly. Do not invent a new material, palette, camera angle, lighting setup, or detail density.
```

## 5. 生产分层 Handoff 文案

宿主生成的 PNG 确认方向后，给真实设计/开发交付如下结构：

```text
Icon Composer layer map
01-background — [solid color / gradient only; no material]
02-mid — [main container/object]
03-foreground — [recognition symbol]
04-accent — [optional small accent; max 4 layers total, back to front]

Target appearances: default / dark / clear light / clear dark / tinted light / tinted dark
(clear and tinted are checked inside Icon Composer under Mono → Options)
Target system versions: [e.g. 26 and 27 — rendering differs before 27]
Color space: [sRGB | Gray Gamma 2.2 | Display P3]

Keep source artwork clean and editable. Do not pre-mask the platform icon shape. Leave dynamic specular, refraction, translucency, blur, and inter-layer shadow decisions for Icon Composer/system rendering. Background colors and gradients are removed before export and rebuilt in Icon Composer. Rebuild the approved raster concept as clean vector layers (SVG/PDF) where practical.
```

## Prompt 编写规则

- 产品语义和主隐喻写在最前面；风格形容词排在后面。
- 颜色用明确 HEX 锁定，不只写“蓝紫色”“科技蓝”。
- 明确画布与单格尺寸（单图 1024×1024；2×2 总画布 1024×1024、每格 ≥512 且留间距），避免模型自由排版。
- 描述玻璃时同时描述“克制”和“主体可读”，避免模型把玻璃强度拉满。
- 负向约束必须覆盖四类：文字 / 水印、设备 mockup 与 UI 截图、烘焙的镜面高光·折射·模糊·层间阴影、给背景加材质。
- 不要堆砌十几个风格关键词；每多一个互相竞争的形容词，风格一致性就更差。
- 一次迭代只改 1–2 个条件；复用原 prompt，其余锁定。
