# Inspira UI × Liquid Glass 集成

> Last verified: 2026-09-17
>
> Inspira UI 是面向 Vue / Nuxt 的可拷贝、可定制组件集合，当前文档基于 shadcn-vue、motion-v 与 TailwindCSS，并包含 backgrounds、cards、interactions、text effects、visualizations 等大量表现型组件。本文件定义它如何作为本 Skill 的 **可选视觉增强层** 使用，而不是替代产品基础组件库或 Liquid Glass 设计规则。

官方入口：

- https://inspira-ui.com/
- https://docs.inspira-ui.com/docs/en
- https://github.com/unovue/inspira-ui
- https://docs.inspira-ui.com/docs/en/getting-started/installation

## 1. 角色边界

Liquid Glass Skill 决定：

- 页面信息架构；
- content / functional layer；
- glass material 语义；
- 颜色、圆角、间距、阴影；
- Toolbar / Sidebar / Inspector / Search；
- 滚动归属、固定操作区；
- 状态、可访问性与响应式；
- 动效预算和验收标准。

Inspira UI 可以提供：

- 有边界的背景效果；
- 卡片/容器强调；
- hover / reveal / pointer micro-interaction；
- 流程、连接关系和视觉化表达；
- onboarding、empty state、hero、产品介绍页的表现力；
- 少量 KPI / number / status 的视觉增强；
- 用户明确要求的特殊视觉组件。

Inspira UI **不负责**：

- 重写项目的 Store / API / Router；
- 替代成熟 Table、Tree、Dialog、Form 的业务行为；
- 决定整个产品的信息架构；
- 把所有 surface 都改成动态卡片；
- 为了“高级感”引入持续动画、WebGL 或指针特效；
- 伪造 macOS 系统 chrome。

一句话：**Liquid Glass 是 design system；Inspira UI 是可选的 presentation toolkit。**

## 2. 什么时候读取本文件

出现以下任一情况时读取：

- 用户明确要求使用 Inspira UI；
- 当前项目是 Vue / Nuxt，并要求更强的视觉表现；
- 用户要求动画背景、动态卡片、beam、spotlight、数字动效等效果；
- 需要把 Inspira UI 现有组件调整为 Liquid Glass 风格；
- 审查项目中是否滥用了 Inspira UI / Aceternity / Magic UI 类效果。

不要因为项目是 Vue 就默认安装 Inspira UI。普通后台、表单、数据表格如果现有组件已满足需求，保持现状。

## 3. 技术前提

当前官方安装方向以 Vue / Nuxt + Tailwind 为主，常见支持依赖包括：

```bash
pnpm add @vueuse/core motion-v tw-animate-css @inspira-ui/plugins
```

也可使用 npm / yarn / bun 的等价命令。项目若已使用 shadcn-vue，优先沿用其 tokens、alias 与 registry 机制，不建立第二套全局主题。

### 版本规则

- 先检查项目 Tailwind 版本；
- 当前官方主线安装说明面向较新的 Tailwind 方案；
- Tailwind CSS v3 项目不要机械套用当前主线配置，按 Inspira UI 对应版本文档处理；
- 不为了使用一个视觉组件强制升级 Tailwind、Nuxt 或现有 UI framework；
- 如果依赖升级影响范围明显大于组件价值，改用本地 CSS / 现有组件实现等价效果。

### 安装组件

Inspira UI 不是必须整体打包进项目的传统大组件库。优先：

1. 确定真实需要的组件；
2. 查看该组件当前官方文档；
3. 使用其当前 CLI / registry 安装方式，或手动复制源代码；
4. 将代码纳入项目现有 components 结构；
5. 立即映射到项目 tokens；
6. 删除 demo 专用文案、假数据和无用依赖；
7. 做 reduced-motion、键盘、触摸和响应式检查。

不要一次性把整个 Inspira UI 组件目录复制到业务项目。

## 4. Liquid Glass Token 映射

Inspira UI 示例中的颜色、渐变、边框和背景默认只是 demo 视觉，不应成为产品新的 token source。

统一映射：

```text
Inspira background       -> existing app background / --lg-bg
Inspira card background  -> --lg-surface 或允许时 --lg-glass-regular
Inspira border           -> --lg-separator / --lg-glass-edge
Inspira foreground       -> --lg-text
Inspira muted            -> --lg-muted
Inspira primary          -> existing brand accent / --lg-accent
Inspira radius           -> 本 Skill 的 radius scale
Inspira shadow/glow      -> 本 Skill shadow + effect budget
Inspira animation        -> 本 Skill motion duration / easing / reduced-motion
```

如果组件内硬编码大量 `neutral-*`、`slate-*`、任意 hex、neon gradient，优先改成 CSS variables / Tailwind semantic tokens。

禁止为了一个 Inspira 组件再引入一整套相互竞争的色板。

## 5. 组件采用分级

### A — 推荐：容易融入产品 UI

适合在保守调整后进入正式产品：

- subtle card emphasis；
- border / shine 类低强度强调；
- number / status transition；
- file / media presentation；
- timeline / step visualization；
- animated list（前提是更新本身有意义）；
- flow / connection visualization；
- 简单 reveal / entrance；
- 有明确业务含义的 visualization。

规则：默认静态可读，动画只是增强。

### B — 条件使用：适合局部展示

- Card Spotlight；
- Animated Beam / Tracing Beam；
- Aurora / Ripple / Wavy 等背景；
- Lens / glare / direction-aware hover；
- morphing / animated text；
- marquee；
- parallax；
- decorative particles / sparkles；
- 轻量 Canvas 动效。

适用位置：

- landing / hero；
- onboarding；
- empty state；
- demo / showcase；
- feature introduction；
- 小范围重要提示。

默认不用于：

- 表格主体；
- 长表单；
- Settings；
- 日志列表；
- 高频操作 toolbar；
- modal body；
- 大面积 dashboard 数据卡片。

### C — 高风险：只有用户明确要求才使用

- 全屏 WebGL scene；
- cursor trail / custom cursor；
- neon / extreme glow；
- 3D globe / heavy scene；
- scratch / game-like reveal；
- device mockup；
- 长时间持续循环的装饰动画；
- 大面积 HTML-in-canvas / shader-like effect。

使用前必须说明性能、可访问性和产品语境，并提供静态 / reduced-motion fallback。

## 6. 典型组件如何融入 Liquid Glass

### Card Spotlight

可以用于少量可探索卡片、产品入口或 feature card。

调整：

- 默认 surface 仍稳定；
- spotlight 强度降低，不改变文字对比度；
- hover 不移动主要布局；
- touch 设备没有 hover 时仍完整可用；
- 不应用到每个 KPI / table row。

### Border Beam / Shine 类效果

适合：

- 新功能提示；
- onboarding 当前步骤；
- 少量重点 CTA 周围；
- demo 环境突出活动对象。

避免：

- 每张卡片都跑 beam；
- 多个 beam 同屏竞争；
- 用 beam 替代 selected/focus/error 等真实状态。

### Animated Beam

只有连接关系本身有语义时使用，例如：

- Agent -> Tool -> Model；
- Data Source -> Processing -> Result；
- 服务依赖关系；
- 数据同步方向。

beam 必须服务于关系表达，而不是作为“AI 感”背景装饰。

### Timeline

适合版本、流程、事件故事和阶段历史。对于高密度系统日志，仍优先普通 list/table，不让滚动动画阻碍定位和复制。

### Number / KPI animation

- 数值首次进入或真实变化时可动画；
- 后台刷新不要每次从 0 重播；
- tabular-nums；
- reduced-motion 下直接显示最终值；
- 不用动画掩盖 loading / stale data。

### Dock

Inspira UI 提供 macOS-style Dock，但本 Skill 的默认 anti-pattern 仍然成立。

只有以下情况可以采用：

- 产品确实存在 launcher / app switcher / tool palette 语义；
- Dock 是真实交互控件而不是装饰；
- 不冒充操作系统 Dock；
- 键盘、tooltip、selected state、触摸均可操作。

普通管理后台、Dashboard、文档页不要为了“像 Mac”添加 Dock。

## 7. Vue + Element Plus

推荐组合：

```text
Element Plus / existing library
  -> Button, Input, Select, Table, Tree, Dialog, Form, Pagination

Inspira UI
  -> background, highlight, beam, decorative card, reveal, onboarding visualization

Liquid Glass Skill
  -> tokens, material, information architecture, layout, accessibility, motion budget
```

不要使用 Inspira UI 的视觉 demo 去重新包装所有 `el-*` 组件。

例如：表格页面可让 toolbar / filter popover 使用玻璃材质，empty state 使用轻量 Inspira 动效，但 `el-table` 仍保持稳定 content surface。

## 8. Vue / Nuxt + shadcn-vue

这是最自然的组合之一，因为 Inspira UI 自身与 shadcn-vue / Tailwind 生态接近。

规则：

- 复用 `components.json` alias；
- 保留 shadcn-vue primitives 的 keyboard / aria / portal 行为；
- Inspira 只扩展视觉或组合层；
- 全局 `--background` / `--foreground` / `--primary` 等变量映射到项目已有 Liquid Glass tokens；
- 不让 registry 安装覆盖经过项目修改的基础组件；
- 安装前查看将新增/覆盖的文件。

## 9. Nuxt / SSR

对于 browser-only、Canvas、WebGL、依赖窗口尺寸或 pointer API 的组件：

- 检查官方组件是否需要 client-only 行为；
- 避免 SSR hydration mismatch；
- 初始化前确认 DOM / container size；
- 路由离开时清理 animation frame、observer、listener、WebGL context；
- 不把整个页面粗暴包进 `ClientOnly` 只为使用一个效果；
- loading fallback 与最终布局尺寸尽量稳定。

## 10. Motion Budget

本 Skill 的基础动效时长仍优先于 demo 默认值：

```text
hover       120–160ms
press       100–140ms
selection   180–220ms
panel       200–280ms
content     240–320ms
```

### 持续动画预算

产品工作台中：

- 同一视口默认最多 1 个明显持续装饰效果；
- 次要持续效果必须很弱；
- 离屏时暂停能暂停的效果；
- 页面 hidden 时避免无意义持续渲染；
- 低端设备 / battery / reduced-motion 条件下应降级；
- 不在 Table、Form、Dialog、Toolbar 中放持续背景动画。

Landing / Showcase 可以放宽，但仍不能影响文字、滚动和输入。

## 11. Reduce Motion

所有引入的 Inspira 动效必须定义 reduced-motion 行为：

```css
@media (prefers-reduced-motion: reduce) {
  /* remove continuous travel / parallax / looping transforms */
  /* keep final state, hierarchy and feedback visible */
}
```

不能只是把 duration 从 2s 改成 20s。

推荐：

- entrance -> final state；
- beam -> static connection；
- number ticker -> final number；
- parallax -> fixed composition；
- cursor-follow -> normal hover/focus；
- animated background -> static gradient / solid background。

## 12. Reduce Transparency / Contrast

Inspira 效果位于玻璃 surface 上时仍遵守本 Skill：

- 文字可读性不能依赖背景刚好较暗；
- Reduce Transparency 时 glass -> solid fallback；
- Increase Contrast 时增强真实边界，而不是增强 glow；
- spotlight / gradient 不作为唯一 selected 或 error 信号；
- clear glass + animated background 组合必须额外检查每个动画帧的可读性。

## 13. Pointer / Touch / Keyboard

很多表现型组件天然以 pointer hover 为中心。进入产品 UI 前必须补齐：

- keyboard focus；
- touch fallback；
- visible focus ring；
- semantic button/link；
- tooltip 不只依赖 hover；
- pointer-follow 不阻断点击；
- card 可点击时不要嵌套冲突的 clickable children。

如果一个组件需要彻底重写可访问交互才能满足基本要求，评估是否值得使用。

## 14. Performance Budget

采用组件前判断它属于：

```text
CSS-only
DOM + Motion
SVG animation
Canvas
WebGL
```

成本逐级增加时，不应该只因为视觉更炫就采用。

检查：

- animation 是否触发布局；
- 是否创建大量 DOM nodes；
- resize / mousemove 是否节流；
- intersection observer 是否用于离屏暂停；
- canvas / WebGL DPR 是否有限制；
- 路由切换是否 cleanup；
- 多个相同特效能否合并；
- 是否拖慢首屏和 interaction readiness。

## 15. Agent 选型流程

当用户说“用 Inspira UI 做这个页面”时：

1. 先判断页面 archetype；
2. 完成 Liquid Glass layout contract；
3. 列出页面现有基础组件；
4. 找出 **最多 1–3 个**真正值得用 Inspira 增强的区域；
5. 从官方当前组件目录选择候选；
6. 检查组件依赖、SSR、pointer、motion、性能；
7. 映射 Liquid Glass tokens；
8. 保留/补齐 reduced-motion 与 accessibility；
9. 实施；
10. 真实浏览器验证。

不要先浏览几十个炫酷组件，再拼成页面。

## 16. 推荐模式

### AI / Agent 工作台

推荐：

- Animated Beam：只用于 Tool / Agent 关系视图；
- subtle number/status animation：运行指标；
- lightweight animated empty state：未运行任务；
- Border Beam：当前执行节点，可选。

避免：

- 每条 message 发光；
- composer 持续动画；
- 背景 particles；
- cursor trail。

### Dashboard

推荐：

- KPI 数字变化；
- 少量 highlight border；
- onboarding / empty state；
- 有业务意义的 visualization。

避免：

- 每个 KPI card spotlight；
- chart 本身玻璃化；
- animated gradient 全屏背景。

### Finder / Asset Browser

推荐：

- media hover preview；
- image Lens（只有确实帮助查看素材时）；
- file transition / empty state。

避免：

- 用动画 tree 替代成熟文件树；
- hover 导致项目位置移动；
- 用 Dock 代替 sidebar。

### Landing / Product Showcase

这里可以最充分使用 Inspira：

- background；
- text effect；
- card interaction；
- beam；
- showcase visualization；
- media reveal。

但导航、CTA、文本对比度、reduced-motion 和移动端仍按本 Skill 验收。

## 17. Anti-patterns

禁止默认产生：

- `Aurora + particles + spotlight + border beam + parallax` 同屏叠加；
- 每一张 card 使用不同 Inspira 效果；
- 全产品统一使用 cursor-follow；
- 为 macOS 风格添加假 Dock；
- 把真实选中状态换成 hover glow；
- 把普通按钮全部改成 animated CTA；
- data table row cardification；
- skeleton、loading、success 都持续发光；
- reduced-motion 仍执行长距离移动；
- 在移动端照搬 desktop hover；
- 为一个组件升级整个技术栈；
- 复制 demo 后留下品牌冲突颜色和无意义英文文案。

## 18. Review checklist

### 架构

- [ ] Inspira UI 是增强层，不是新的业务架构。
- [ ] 没有为了一个组件替换成熟基础组件库。
- [ ] 没有不必要的框架/版本升级。

### 视觉

- [ ] 使用项目 Liquid Glass tokens。
- [ ] 没有新增相互竞争的色板。
- [ ] 没有 glass + glow + beam 多层堆叠。
- [ ] content layer 仍稳定。

### 交互

- [ ] hover 有 keyboard/touch fallback。
- [ ] focus 可见。
- [ ] 动画不改变核心布局。
- [ ] 动画不是唯一状态提示。

### Accessibility

- [ ] prefers-reduced-motion 有真正降级。
- [ ] Reduce Transparency / contrast 下仍可读。
- [ ] screen reader / semantic control 没被视觉 wrapper 破坏。

### Performance

- [ ] 持续动画数量受控。
- [ ] observer/listener/RAF 可 cleanup。
- [ ] Canvas/WebGL 有明确价值。
- [ ] 离屏/隐藏状态不会持续无意义渲染。

### 验收

- [ ] 1440×900 / 1280×720 等目标桌面尺寸验证。
- [ ] 窄屏 / 短屏验证。
- [ ] 200% zoom 验证。
- [ ] reduced motion 验证。
- [ ] touch / keyboard 至少完成目标产品需要的验证。

## 19. 外部依赖边界

Inspira UI 为独立开源项目，本 Skill 与其没有官方隶属关系。引用组件时：

- 以 Inspira UI 当前官方文档和仓库为准；
- 尊重组件自身 credits / license / attribution 信息；
- 不把第三方组件代码复制进本 Skill 仓库作为固定快照，除非明确需要且许可允许；
- 本 Skill 主要保存 **选择、适配、约束和验收知识**，避免随着上游组件快速变化而过期。
