# Liquid Glass 材质与光学规则

> 适用范围：Web / 跨端视觉近似。这里描述的是 Agent 的设计与实现决策，不是 Apple 官方固定数值。原生 SwiftUI / AppKit 请求优先使用系统组件与原生材质，见 `macos-liquid-glass-native-ui`。

## 1. 先区分功能层与内容层

Liquid Glass 首先是一种**功能层（functional layer）**语言，用来承载导航、控制、临时交互和浮层，让内容在其下方保持连续感。

默认规则：

- 导航、工具栏、侧栏、浮动控制、Popover、临时操作：可以使用 Liquid Glass。
- 正文、文章、表格主体、图表画布、编辑器正文、长列表内容：默认使用稳定内容材质，不整块玻璃化。
- 内容区里的 Toggle、Slider、临时浮动按钮等交互对象，可以在激活或悬浮时带少量玻璃反馈，但不能让整个内容卡片都变成玻璃。
- 当没有任何有意义的内容从下方通过时，不要为了“看起来像 Liquid Glass”强行增加透明和模糊。

判断问题只有一个：**这块玻璃是否在帮助用户理解“这是控制/导航层，而下面是内容”？** 如果不是，优先使用普通 surface。

## 2. 材质等级

Agent 从下表选择，而不是自由发明每块玻璃：

| Token | 建议视觉 | 典型用途 | 不适用 |
|---|---|---|---|
| `content-solid` | 不透明、稳定底色 | 正文、图表、表格、长表单 | 导航浮层 |
| `glass-light` | 轻透明、轻 blur | 顶部轻导航、辅助 toolbar | 高对比复杂背景 |
| `glass-regular` | 中等透明、清晰边缘 | Toolbar、Sidebar 控制层、浮动控制 | 大面积正文 |
| `glass-clear` | 更透明、更依赖背景 | 图片/视频等视觉丰富背景上的少量控制 | 文本密集、纯白背景 |
| `glass-thick` | 高不透明度、较强 blur | 菜单、Popover、Sheet、关键浮层 | 大面积常驻页面 |
| `glass-tinted` | regular/clear + 小范围品牌染色 | 选中、关键操作、品牌强调 | 每个组件都着色 |

建议 Web 基线：

```css
--lg-content: #fff;
--lg-glass-light: rgba(255,255,255,.62);
--lg-glass-regular: rgba(250,251,253,.78);
--lg-glass-clear: rgba(255,255,255,.42);
--lg-glass-thick: rgba(250,251,253,.92);
--lg-blur-light: 20px;
--lg-blur-regular: 24px;
--lg-blur-thick: 32px;
--lg-saturation: 140%;
```

这些只是起点。真实背景越复杂，越需要提高不透明度、增加局部暗化或退回稳定 surface。

## 3. Regular 与 Clear 的选择

### Regular

默认选择。适合：

- Toolbar
- Sidebar / Inspector 上的控制区
- 浮动按钮组
- Search / Filter 控制区
- Popover / 菜单容器

目标：背景可感知，但控件本身必须始终清晰。

### Clear

只在视觉丰富背景上使用，例如：

- 图片浏览器
- 视频播放器
- 地图
- 大型封面或媒体画布

Clear 不等于“透明度越低越高级”。如果白色或浅色内容从下面经过后导致按钮消失，应立即提高材质密度、加局部 dimming / scrim 或改用 regular。

## 4. 玻璃必须有结构，不只是一层 blur

完整玻璃至少考虑四个因素：

1. **Background transmission**：能感知后方内容，但不影响前景可读性。
2. **Edge highlight**：轻微高光帮助轮廓成立。
3. **Depth separation**：通过边界、亮度和阴影把功能层从内容层分开。
4. **Controlled refraction**：只作为轻微质感，不允许把文字和图标扭曲到难读。

推荐边缘：

```css
border: 1px solid rgba(255,255,255,.55);
box-shadow:
  inset 0 1px 0 rgba(255,255,255,.45),
  0 8px 28px rgba(25,40,65,.08);
```

不要同时叠加：强 blur + 强 glow + 强高光 + 多层透明卡片 + 彩色渐变。高质量来自克制和层级，不来自效果数量。

## 5. 玻璃容器合并规则

同一区域内多个相关控件优先共享一个 glass container，而不是每个按钮各自一颗“玻璃糖果”。

适合共享：

- 一组 toolbar actions
- segmented control
- 地图缩放/定位按钮组
- 媒体播放控制
- filter chip group

需要独立：

- 主操作与危险操作语义不同
- 控件距离较远或属于不同任务
- 系统/现有设计本身要求独立边界

若视觉出现“十几个胶囊漂在页面上”，默认判定为过度玻璃化。

## 6. 染色与品牌色

品牌色只用于：

- 选中状态
- 当前导航项
- 主要 CTA
- 小范围 accent
- 关键状态

不要给每个玻璃面板都染成不同颜色。正文颜色仍来自语义色系统；玻璃色不是数据可视化色板。

原则：

- tint 面积越大，饱和度越低；
- 小控件可以更鲜明；
- 信息/成功/警告/错误仍按语义色表达，不依赖玻璃色推断状态。

## 7. 深色模式

深色不能只把白玻璃改成黑色透明。

建议：

```css
--lg-dark-glass-regular: rgba(35,39,48,.82);
--lg-dark-edge: rgba(255,255,255,.12);
```

深色更依赖：

- 明度差
- 轻边界
- 局部高光
- 少量阴影

减少大面积发光，避免蓝紫霓虹科技屏。

## 8. Reduce Transparency / Increase Contrast / Show Borders

Agent 必须把材质看成**可降级表现**，不能把可读性绑定在透明度上。

当减少透明或浏览器不支持 backdrop-filter：

- 玻璃退到稳定 surface；
- 边界、选中、焦点仍然清楚；
- 信息层级不能消失。

当提高对比度：

- 提高文字和边界对比；
- 减少过淡的透明装饰；
- 不能只靠背景模糊区分层级。

当环境要求显示更明确边界时：

- 自定义控制补足 border/outline；
- 不把边界烘焙成永远很重的默认视觉；
- 原生实现优先响应系统环境值。

## 9. 性能预算

backdrop-filter 是昂贵效果。实现时：

- 不在长列表每行启用 backdrop-filter；
- 不在动画中的大面积元素持续变化 blur；
- 避免 3 层以上相互嵌套的透明模糊；
- 优先一个共享容器，而不是 N 个独立玻璃子项；
- 滚动卡顿时先降低 blur 区域和层数，而不是牺牲文字清晰度。

## 10. 失败模式

出现以下任一项时重新设计：

- 正文卡片全部半透明；
- 表格每一行都是玻璃；
- 图表 canvas 本身透明，网格线与背景混在一起；
- 玻璃后方没有任何可见内容；
- 为了看见玻璃而加入无业务意义的渐变球、彩色 blob；
- 重要按钮在不同背景下对比度不可预测；
- 多层 blur 导致边缘脏、文字发灰；
- Clear glass 被用于纯白/纯浅灰内容背景且无任何补偿。

## 11. Agent 决策顺序

每次使用玻璃前依次回答：

1. 这是内容层还是控制/导航层？
2. 后方是否真的有值得透出的内容？
3. regular 是否足够？为什么需要 clear？
4. 这一组控件是否应该共享一个 glass container？
5. 减少透明后是否仍然完整可用？
6. 深色、复杂背景、滚动状态下是否仍然清晰？
7. 这个效果是否值得它的性能成本？

答不出理由时，使用稳定 surface。

## 官方核对入口

实现原生 Apple 平台产品或需要确认最新行为时，核对：

- https://developer.apple.com/design/human-interface-guidelines/materials
- https://developer.apple.com/documentation/technologyoverviews/liquid-glass
- https://developer.apple.com/design/human-interface-guidelines/designing-for-macos/
