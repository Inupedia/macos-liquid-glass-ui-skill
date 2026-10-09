---
name: macos-liquid-glass-ui
description: 为选择 macOS / Apple Liquid Glass 风格的 Web、桌面 Web App 与 Electron/Tauri 产品设计、实现或审查 UI，提供材质语义与 clear 判定、色板、窗口与导航、页面范式、完整组件覆盖、固定操作、滚动、响应式、仅文字放大、可访问性与系统偏好降级、性能预算、框架与 Inspira UI 适配、桌面壳窗口原生材质、中文/RTL 排版和验收规范。适用于跨项目复用该风格，不默认替换其他品牌设计；原生 SwiftUI/AppKit 请求转用同仓库 native skill，App Icon 请求转用 icon skill。
---

# macOS Liquid Glass UI

跨业务、跨前端框架复用的 **Web / 跨端视觉近似** UI 规范。数值是 Web 设计基线，不是 Apple 官方固定参数；玻璃为 Web 视觉近似。用户指定品牌、已批准样式、现有组件库及修改范围优先。

## 先判断是否该使用本 Skill

使用本 Skill：

- Web 产品、桌面 Web App、Electron/Tauri Web UI；
- 需要 Liquid Glass 风格的页面、组件、布局、交互或审查；
- 需要把现有 Web 产品改得更接近 macOS / Apple 的信息架构和视觉语言；
- Vue / Nuxt 产品明确要求结合 Inspira UI 做视觉增强。

不要使用本 Skill：

- 原生 SwiftUI / AppKit 页面实现：改用 `macos-liquid-glass-native-ui`；
- App Icon / launcher icon / 产品图标：改用 `macos-liquid-glass-icon`；
- 16–24px 普通工具栏图标：优先系统符号或项目现有 icon system。

## 交付范围

- **规范/提示词**：输出独立完整规范，包含具体颜色、材质语义、布局行为、状态与验收，不自动修改项目。
- **设计/实现**：检查实际入口、技术栈、现有组件、Token、样式及未提交修改，复用既有能力，不强制换框架或组件库。
- **审查**：提供问题、触发条件、风险、建议和验证方式；审查不自动授权实施。
- **局部修改**：保留用户已认可区域，不因调用 Skill 擅自扩大改造范围。
- **跨项目复用**：移除水文、Archify 等业务依赖，不把单页、三栏或固定品牌色变成所有产品要求。
- **Inspira UI 集成**：把 Inspira UI 视为 Vue/Nuxt 的可选 presentation toolkit；Liquid Glass 规则仍负责信息架构、材质、动效预算、可访问性和验收。

可从上下文判断时直接继续。只有页面类型、用户群、目标设备或任务边界会实质改变结果时才补充说明。

## 核心原则

1. **先分内容层和功能层。** Liquid Glass 主要用于导航、控制和临时浮层；正文、图表、表格保持稳定内容材质。
2. **先选页面范式，再画布局。** Document、Finder-style、Settings、Dashboard、Workbench、Chat、Media/Map、Form、Table Admin 等使用不同骨架。
3. **主操作归属稳定。** 页面/面板级保存、提交等置于所属容器稳定底部；搜索、筛选、行内编辑、展开、关闭等局部操作留在对象旁。
4. **明确谁滚动。** 每个区域说明固定/弹性角色、滚动主体和溢出行为；锁高工作台与自然内容页使用不同骨架。
5. **结构随窗口变化，而不是整体缩小。** 短屏、窄屏、200% 缩放、软键盘优先保证内容和操作可达。
6. **尊重系统偏好。** 不全局隐藏滚动条；支持 Reduce Motion、Reduce Transparency、Increase Contrast 和更明确边界需求。
7. **状态真实。** 加载、空态、错误、部分成功和结果沿用稳定框架；不编造完成进度或数据。
8. **平台感来自行为，不来自装饰。** 不添加无功能红黄绿按钮、假 Dock、过度胶囊或满屏玻璃。
9. **第三方效果服从设计系统。** Inspira UI、Aceternity/Magic UI 类组件只能增强局部表达，不重新定义全局 tokens、交互模型或页面骨架。
10. **桌面壳里窗口材质优先。** Electron / Tauri 产品先考虑系统窗口材质（vibrancy / mica / Tauri window effects）；页面内 backdrop-filter 只能模糊 WebView 自己绘制的内容，窗口不透明时"半透明页面"是假的。两者不要叠加成 glass-on-glass。
11. **降级不能只靠媒体查询。** `prefers-reduced-transparency` 只有 Chromium 系支持（Safari / Firefox 未实现），所以默认状态本身必须可读，`prefers-contrast` / `forced-colors` 与实色基线要单独成立。

## 工作顺序

### 1. 建立布局合同

简短记录：

- 页面范式；
- 固定/弹性区域；
- 主要滚动主体；
- Sidebar / Inspector 是否存在及最小宽度；
- 主操作归属；
- 窄屏与短屏降级；
- 搜索范围与导航层级。

### 2. 选择材质

先区分 `content-solid`、`glass-light`、`glass-regular`、`glass-clear`、`glass-thick`、`glass-tinted`。默认 regular；clear 只用于图片、视频、地图等视觉丰富背景上的少量控制，并且必须通过判定线：按最坏背景帧计算合成色，正文对比 ≥4.5:1、必要图形 ≥3:1，不满足就加 scrim（不透明度 ≥.25）或退回 regular。实现时用 `[data-material]` 切换 `--lg-surface-material` / `--lg-blur-material`，材质值只来自 `assets/foundation.css`。

是 Electron / Tauri 产品时，先判断能否用窗口原生材质承载；能承载就不要在页面里再画一层玻璃。

### 3. 套组件与状态

**组件级任务必须先读 `references/component-design-contract.md`，再按类型精读：**
- Actions / Tabs / Breadcrumb / Navigation / Feedback / Lists → `references/actions-navigation-feedback-components.md`；
- 弹窗 / Sheet / Popover / Menu → `references/overlays-and-dialog-components.md`；
- Select / Selector / Segmented / Combobox / Filter → `references/selection-and-input-components.md`；
- Table / Data Grid / 排序 / 多选 / 批操作 → `references/tables-and-data-components.md`。

不能只输出「有 Dialog、Table、Select」或一张视觉截图；对实际使用的组件必须包含 Variant 决策、Anatomy、Token/Material、关键状态、键盘与焦点、数据模型、失败恢复和可执行验收。具体组件优先保留现有无障碍 primitive；`assets/component-recipes.css` + `assets/component-showcase.html` 是可打开的示例，不是新的框架依赖。

按业务需要覆盖默认、hover、pressed、focus、selected、disabled、readonly、loading、empty、error、long-content、narrow/short viewport、reduced motion/transparency 等状态，不为“完整”制造业务不存在的状态。

如果用户要求“完整设计系统”或“组件要足够充足”，读取完整组件矩阵，再只展开目标产品实际会用到的类别。

### 4. 适配现有技术栈

优先映射已有 tokens 和组件库。Vue、Element Plus、React、Tailwind、Headless 组件库、ECharts、Electron/Tauri 等实现策略读取实现适配参考，不为视觉迁移重写业务架构。

如果用户明确要求 Inspira UI，或 Vue/Nuxt 页面需要 animation background、beam、spotlight、number effect、visualization 等表现型组件：

1. 读取 `references/inspira-ui.md`；
2. 先完成 Liquid Glass 页面范式和布局合同；
3. 找出最多 1–3 个真正值得增强的区域；
4. 优先保留 Element Plus / shadcn-vue / Nuxt UI 等成熟基础组件；
5. 按 Inspira UI 当前官方文档安装具体组件，不整库复制；
6. 将 demo tokens、motion 和状态映射回本 Skill；
7. 验证 reduced motion、keyboard/touch、SSR 和性能。

### 5. 做负向检查

对照 anti-patterns，重点排查：

- 全页玻璃化；
- glass-on-glass（包含"窗口原生材质之上再叠页面玻璃"）；
- 三栏滥用；
- toolbar button soup；
- 嵌套滚动；
- 假 macOS chrome；
- 关键错误只用 Toast；
- 200% 仍强制原布局；
- 只测页面缩放、不测仅文字放大；
- 只在 Chromium 验证 reduce transparency，就当降级已完成；
- 把装饰性 `--lg-border` / `--lg-separator` 当必要边界用（深色下尤其）；
- 白字按钮压 `--lg-accent`；
- 图表只用颜色区分系列，或深色主题没换系列色；
- Inspira UI 多种特效同屏堆叠；
- 为了"像 Mac"添加装饰性 Dock；
- 动画替代真实 selected/focus/error 状态。

### 6. 验证

实现后验证真实行为，尤其：

- 长内容展开后的按钮位置；
- 窗口高度/宽度变化；
- 200% 页面缩放与**仅文字放大**；
- 键盘与焦点（焦点环两侧对比度实测）；
- Reduce Motion / Transparency（含 Safari 等不支持该媒体查询时的降级路径）；
- `prefers-contrast: more` 与 `forced-colors`；
- `color-scheme` 是否让原生控件跟随主题；
- 图表容器尺寸变化、深色主题系列色；
- 玻璃层数与帧率是否在性能预算内；
- 模态/菜单层级与焦点恢复；
- 中文/多语言/RTL 下的换行、按钮位置与 `dir` 行为；
- 第三方动效在 offscreen、touch、SSR/hydration 和 cleanup 场景的行为。

使用环境允许的浏览器工具；不依赖特定插件。构建通过不等于视觉验收，浏览器预览也不等于桌面壳验收。

## 资源路由

按任务读取最少必要文件；完整规范再组合读取。

- **颜色、字体、间距、基础视觉**：`references/visual-system.md`
- **Liquid Glass 语义、regular/clear、光学、降级、性能**：`references/materials-and-optics.md`
- **布局、滚动、稳定底栏、短屏/窄屏**：`references/layout-and-scroll.md`
- **Toolbar、Sidebar、Inspector、Search、Menu、Selection**：`references/window-and-navigation.md`
- **组件设计入口（选型 → 解剖 → 状态 → 行为 → 验收）**：`references/component-design-contract.md`
- **Button、Tabs、Navigation、Feedback、List、Empty State**：`references/actions-navigation-feedback-components.md`
- **弹窗、Sheet、Popover、Menu 的组件规格**：`references/overlays-and-dialog-components.md`
- **Selector、Select、Combobox、Segmented、Filter**：`references/selection-and-input-components.md`
- **Table、Data Grid、批量选择与排序**：`references/tables-and-data-components.md`
- **组件行为、表单、图表、状态与动效**：`references/components-and-states.md`
- **完整组件覆盖范围**：`references/component-matrix.md`
- **键盘、对比度、缩放、系统辅助偏好**：`references/accessibility.md`
- **选择页面骨架**：`references/page-archetypes.md`
- **生成/审查前的负向约束**：`references/anti-patterns.md`
- **Vanilla/Vue/Element Plus/React/Tailwind/图表/Electron 实施**：`references/implementation-adapters.md`
- **Inspira UI × Liquid Glass 选型、安装、适配、动效与性能约束**：`references/inspira-ui.md`
- **Electron / Tauri 窗口原生材质、权限、降级链**：`references/desktop-shell-integration.md`
- **中西文混排、CJK 断行、逻辑属性与 RTL、文字缩放**：`references/i18n-and-typography.md`
- **实现/审查验收**：`references/validation.md`
- **可运行的组件演示**：`assets/component-showcase.html` 与 `assets/component-recipes.css`（先加载 foundation.css；演示不替代生产级 a11y primitives）。
- **起步样式**：`assets/foundation.css`，按现有 Token 转换；不是全局 reset，不直接替换现有样式。它是全部 `--lg-*` token 的唯一定义源。

### 推荐组合

- **完整 UI 规范**：视觉系统 + 材质 + 页面范式 + 布局滚动 + 窗口导航 + 完整组件矩阵 + 组件状态 + 可访问性 + 验收。
- **现有项目实施**：页面范式 + 布局滚动 + 材质 + 相关组件 + 实现适配 + anti-patterns + 验收。
- **Vue/Nuxt + Inspira UI**：页面范式 + 材质 + 实现适配 + Inspira UI + accessibility + anti-patterns + 验收。
- **审查**：anti-patterns + 可访问性 + 布局滚动 + 验收，再按发现的问题读取具体模块。
- **Dialog / Selector / Table 组件专项**：component-design-contract + 对应详细组件规格 + foundation.css / component-recipes.css + accessibility + validation。
- **Dashboard / 数据产品**：视觉系统 + 材质 + components-and-states + component-matrix + 布局滚动 + 可访问性。
- **地图/媒体/画布**：材质（重点 clear）+ window/navigation + page-archetypes + accessibility。
- **Electron / Tauri 桌面产品**：desktop-shell-integration + 材质 + 布局滚动 + window/navigation + 实现适配 + 验收。
- **中文 / 多语言 / RTL 产品**：i18n-and-typography + 视觉系统 + 布局滚动 + 可访问性。

## 交付要求

完整规范须包含：

- 色值与字体层级（引用 `--lg-*` token，不重复十六进制）；
- 材质选择理由（含 clear 判定计算）；
- 页面范式与布局合同；
- 导航、Toolbar、Search、Sidebar/Inspector 规则；
- 滚动条、溢出、固定操作、层级；
- 组件级合同（Variant、Anatomy、材质/Token、键盘/焦点、受控状态、异步/错误、验收）；
- Accessibility（含仅文字放大、Safari 降级路径、对比度实测值）；
- 性能预算（层数、帧率、测量方法）；
- Anti-pattern 检查；
- 验收矩阵（含视口 → 断点命中关系）。

如果使用 Inspira UI，额外说明：

- 选用了哪些组件以及业务理由；
- 哪些现有基础组件被保留；
- token / motion 如何映射；
- reduced-motion、touch/keyboard、SSR 与性能处理；
- 哪些候选效果因过度装饰或成本过高被舍弃。

实现交付说明修改范围、实际验证和未验证限制。不自行发布、改变系统偏好或声称完成未执行的检查。

## 官方边界

本 Skill 的 Web 参数属于项目基线，不声称替代 Apple HIG。需要核实原生行为或最新系统变化时，以 Apple 官方为准：

- https://developer.apple.com/design/human-interface-guidelines/materials
- https://developer.apple.com/design/human-interface-guidelines/designing-for-macos/
- https://developer.apple.com/design/human-interface-guidelines/toolbars
- https://developer.apple.com/design/human-interface-guidelines/sidebars
- https://developer.apple.com/design/human-interface-guidelines/searching
- https://developer.apple.com/documentation/technologyoverviews/liquid-glass

Inspira UI 集成以其当前官方文档和仓库为准：

- https://docs.inspira-ui.com/docs/en
- https://docs.inspira-ui.com/docs/en/getting-started/installation
- https://github.com/unovue/inspira-ui
