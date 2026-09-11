# ChatGPT Image Prompt 模板

目标：让宿主的图像生成能力直接产出 Liquid Glass App Icon 概念图或定稿，不经过外部 API。

## 1. 单个 App Icon

把方括号替换成真实内容；不要原样保留占位符。

```text
Create one polished app icon artwork for [product/app name], a [one-sentence product purpose].

Core metaphor: [one clear object/action].
Silhouette: [simple outer shape that stays recognizable at small size].
Layer structure: [background], [mid layer], [foreground], optional [small accent]. Keep the depth structure clear and limited to 2–4 layers.

Use this locked palette:
- primary: [#HEX]
- secondary: [#HEX]
- glass tint: [#HEX]
- accent: [#HEX, optional]

Visual direction: premium Apple-platform app icon, Liquid Glass-inspired material with controlled translucency, subtle refraction, restrained specular edge highlights, shallow optical depth, and crisp edges. The material should support the symbol, not obscure it. Keep the design simple, memorable, and brand-specific rather than generic 3D glass.

Composition: square 1024×1024 icon artwork, centered subject, generous safe margin, strong readable silhouette, balanced depth, no tiny decorative details. It must remain recognizable at 64 px and 32 px.

Avoid: text, fake letters, watermark, UI screenshot, device mockup, desktop/Dock scene, busy background, photoreal environment, chrome, gummy candy, inflated plastic, excessive glow, excessive reflections, noisy texture, clutter.

Output only the icon artwork, no presentation frame or caption.
```

## 2. 2×2 候选方向

只在概念歧义明显时使用。四格要比较“隐喻/构图”，不要同时比较四种完全不同的视觉风格。

```text
Create a 2×2 concept sheet containing four alternative app icon directions for [product/app name], a [purpose].

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

Each cell must contain one centered square app icon concept with generous spacing between cells. Keep every concept readable at small size. No labels inside the icon artwork, no text, no watermark, no device mockup, no UI screenshot, no decorative background scene.
```

候选图只用于选择方向。确定方向后必须重新生成单图，不要直接从宫格截图当最终 icon。

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

Do not replace the icon with a different metaphor. Do not add text, watermark, device mockup, extra objects, busy backgrounds, chrome, gummy/plastic styling, or excessive glow.
```

## 4. 图标家族

先写共享 style spec，再为每个图标只替换 `metaphor`。

```text
Generate one icon in an existing app-icon family.

Shared family spec — do not change:
- palette: [HEX values]
- silhouette language: [description]
- layer count: [N]
- perspective: [description]
- Liquid Glass strength: [description]
- edge/radius language: [description]
- accent rule: [description]
- detail budget: [description]

This icon's concept only:
[name] — [single concrete metaphor]

Match the family exactly. Do not invent a new material, palette, camera angle, lighting setup, or detail density.
```

## 5. 生产分层 Handoff 文案

ChatGPT 生成的 PNG 确认方向后，给真实设计/开发交付如下结构：

```text
Icon Composer layer map
01-background — [shape/color role]
02-mid — [main container/object]
03-foreground — [recognition symbol]
04-accent — [optional small accent]

Keep source artwork clean and editable. Do not pre-mask the platform icon shape. Leave dynamic specular, refraction, translucency, blur, and inter-layer shadow decisions for Icon Composer/system rendering. Rebuild the approved raster concept as clean vector layers where practical.
```

## Prompt 编写规则

- 产品语义和主隐喻写在最前面；风格形容词排在后面。
- 颜色用明确 HEX 锁定，不只写“蓝紫色”“科技蓝”。
- 描述玻璃时同时描述“克制”和“主体可读”，避免模型把玻璃强度拉满。
- 不要堆砌十几个风格关键词；每多一个互相竞争的形容词，风格一致性就更差。
- 一次迭代只改 1–2 个条件；复用原 prompt，其余锁定。
