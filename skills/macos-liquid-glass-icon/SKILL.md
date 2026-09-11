---
name: macos-liquid-glass-icon
description: 为 macOS / Apple 平台产品设计并生成 Liquid Glass 风格的 App Icon、产品图标或一组同风格入口图标。优先直接使用当前 ChatGPT/宿主提供的图像生成能力，不调用外部图像 API，不要求 API Key。适用于从产品语义、品牌资产或现有 UI 推导图标概念、生成候选稿、迭代成稿，并给出 Icon Composer 分层交付说明；不用于普通 SF Symbols、16px 工具栏线性小图标或纯代码 SVG 图标库。
---

# macOS Liquid Glass Icon

为 Apple 平台产品建立可识别、可缩放、与现有品牌一致的 Liquid Glass 图标方向，并在宿主具备图像生成能力时直接生成图片。

本 Skill 的默认目标是 **App Icon / 产品图标**，不是把所有 UI 小图标都做成玻璃球。Apple 平台生产级 Liquid Glass App Icon 是分层资产；ChatGPT 生成的扁平 PNG 更适合作为视觉成稿、候选稿和生产参考，不能冒充可编辑的 Icon Composer 源文件。

## 硬性规则

1. **直接使用宿主图像生成。** 当前 ChatGPT 或宿主有可调用的 image generation / image edit 能力时，必须直接使用它生成或编辑图标。
2. **不调用外部图像 API。** 不接 OpenAI Images API、第三方 provider、CLI 中转或远程生图服务；不索要 API Key。
3. **没有图像工具时不伪造结果。** 只交付完整 icon brief、style spec、最终 prompt、分层方案和验收清单，并明确尚未生成图片。
4. **先设计，后生图。** 先锁定产品语义、核心隐喻、轮廓、层级和颜色，再调用图像生成；不要靠反复“抽卡”替代设计。
5. **优先真实产品上下文。** 用户给了 logo、截图、站点、设计 Token、现有 App Icon 或品牌资产时，先从这些资产推导，不直接套通用玻璃模板。
6. **保持简单。** 一个主隐喻，少量形状，强轮廓；32–64 px 仍需一眼辨认。避免小字、复杂场景、过多零件和装饰性噪声。
7. **生产分层不要预烘焙系统效果。** 面向 Icon Composer 的源层不要依赖预制圆角遮罩，也不要把镜面高光、折射、模糊、半透明和层间阴影烘焙成不可编辑效果；这些由系统/Icon Composer 处理更合适。

## 先判断任务类型

- **单个 App Icon / 产品图标**：默认直接产出一个强方向；概念明显不确定时先做 2×2 候选稿，再基于最佳方向生成单图。
- **同一产品的图标家族**：先冻结共同的 palette、材质、视角、圆角语言、层级和 motif，再逐个生成；不要让每张图各自“自由发挥”。
- **基于现有图片改图标**：保留用户指定的主体和品牌识别，使用图像编辑能力修改材质、构图、颜色或简化细节。
- **普通工具栏/菜单符号**：不要使用本 Skill 的重材质 App Icon 方法；优先系统符号或项目现有 icon system。

## Workflow

### 1. 建立 Icon Brief

从上下文直接提取，缺少但不影响设计时做保守假设，不为了形式化而反复追问。

至少明确：

- 产品 / App 名称与一句话功能；
- 最重要的一个用户心智或对象；
- 目标平台（macOS 为主，或 Apple 多平台）；
- 已有品牌色、logo、视觉资产与禁用元素；
- 需要单图、候选方向还是图标家族；
- 是否需要后续进入 Icon Composer。

### 2. 选择一个核心隐喻

把功能压缩成一个可视对象或动作，例如：

- 知识库 → 层叠卡片 / 发光书页，而不是“数据库 + AI + 搜索 + 对话”全部塞入；
- 水文预测 → 水滴 / 河道曲线 + 预测轨迹，而不是完整仪表盘；
- 开发工具 → 代码结构 / 连接节点，而不是笔记本电脑屏幕截图。

优先：**一个主对象 + 一个辅助动作或层**。文字和字母只有在它们本身就是品牌标识时才使用。

### 3. 冻结 Style Spec

完整规范见 [图标设计系统](references/icon-system.md)。最少锁定：

- `metaphor`：主隐喻；
- `silhouette`：远看轮廓；
- `layers`：2–4 个清晰深度层；
- `palette`：2–4 个主色，写明十六进制色值；
- `material`：玻璃的透明、折射、边缘高光强度；
- `background`：背景层角色，不把背景做成复杂风景；
- `detail_budget`：允许的细节数量；
- `avoid`：明确禁用文字、水印、设备 mockup、杂乱纹理等。

同一图标家族必须复用同一份 style spec，只改变语义对象。

### 4. 生成 Prompt

使用 [生图 Prompt 模板](references/prompt-template.md)。Prompt 必须描述：

- 产品用途与图标隐喻；
- 1024×1024 方形图标画布；
- 中央构图和安全留白；
- 2–4 层明确前后关系；
- 锁定色板；
- Liquid Glass 的材质表现；
- 小尺寸可读性；
- no text / no watermark / no device mockup 等负向约束。

如果要做候选方向，要求每格保持同一品牌系统，只改变隐喻或构图，不同时改变颜色、材质和视角。

### 5. 直接调用 ChatGPT 图像生成

宿主有图像生成能力时直接生成：

- 单个定稿：优先生成 **1 张 1024×1024 正方形图**；
- 高歧义概念：先生成 **2×2 候选方向图**，选择最强方向后再生成单图；
- 已有图标需要改造：使用图像编辑，而不是重新凭文字猜测原图。

不要因为“更方便”改走外部 API，也不要让用户去配置 provider。

### 6. 迭代时只改一个维度

优先顺序：

1. 隐喻是否准确；
2. 轮廓是否清楚；
3. 构图和层级；
4. 品牌颜色；
5. 玻璃材质强弱；
6. 小细节。

每轮尽量只调整 1–2 个维度，避免整张图漂移成新风格。

### 7. QA

按 [验收清单](references/validation.md) 检查：

- 1024 px 看材质，256 px 看构图，64 px / 32 px 看轮廓；
- 是否一眼能说出主对象；
- 是否仍像图标而不是插画、海报或 3D 商品渲染；
- 玻璃是否克制，主体是否被透明和高光吃掉；
- 是否有乱码、伪文字、水印、边缘脏点、异常手柄或错误透视；
- 深色 / 浅色背景下是否仍有足够边界；
- 图标家族是否保持同一颜色、视角、材质和细节密度。

不通过就编辑或重生失败项，不把“生成成功”当作“设计通过”。

### 8. 交付

正常交付包含：

- 最终 PNG（宿主可生成时）；
- 最终 icon brief；
- 冻结后的 style spec；
- 最终生成 prompt，便于后续复现；
- 若用于真实 Apple App Icon，再附 **Icon Composer layer map**：背景 / 中层 / 前景分别是什么，以及哪些玻璃效果应留给 Icon Composer。

如果用户只要图片，可把文字说明缩短，但仍要保留必要的生产提醒。

## 与 UI Skill 的关系

`macos-liquid-glass-ui` 管页面、组件、布局、材质和交互；本 Skill 管 App Icon / 产品图标。两者可以共享品牌色与材质语言，但 **不要直接把页面 glass panel 缩小后当 App Icon**。

需要同时做 UI 和 App Icon 时：先从产品品牌与 UI 提取共同 token，再让图标形成更强的单一轮廓和更低的细节预算。

## 官方生产参考

Apple 当前的 App Icon 与 Liquid Glass 生产流程以官方 Human Interface Guidelines 和 Icon Composer 文档为准：

- https://developer.apple.com/design/human-interface-guidelines/app-icons
- https://developer.apple.com/icon-composer/
- https://developer.apple.com/documentation/xcode/creating-your-app-icon-using-icon-composer

本 Skill 的视觉参数属于跨项目生成基线，不声称替代 Apple 官方模板、Icon Composer 或 Xcode 的最终验证。
