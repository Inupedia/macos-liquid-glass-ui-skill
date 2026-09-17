---
name: macos-liquid-glass-ui
description: 为选择 macOS / Apple Liquid Glass 风格的 Web 产品设计、实现或审查 UI，提供材质语义、色板、窗口与导航、页面范式、组件、固定操作、滚动、响应式、可访问性和验收规范。适用于跨项目复用该风格，不默认替换其他品牌设计；原生 SwiftUI/AppKit 请求转用同仓库 native skill。
---

# macOS Liquid Glass UI

跨业务、跨前端框架复用的 **Web / 跨端视觉近似** UI 规范。数值是 Web 设计基线，不是 Apple 官方固定参数；玻璃为 Web 视觉近似。用户指定品牌、已批准样式、现有组件库及修改范围优先。

## 先判断是否该使用本 Skill

使用本 Skill：

- Web 产品、桌面 Web App、Electron/Tauri Web UI；
- 需要 Liquid Glass 风格的页面、组件、布局、交互或审查；
- 需要把现有 Web 产品改得更接近 macOS / Apple 的信息架构和视觉语言。

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

先区分 `content-solid`、`glass-light`、`glass-regular`、`glass-clear`、`glass-thick`、`glass-tinted`。默认 regular，clear 只用于图片、视频、地图等视觉丰富背景上的少量控制。

### 3. 套组件与状态

按业务需要覆盖默认、hover、pressed、focus、selected、disabled、readonly、loading、empty、error、long-content、narrow/short viewport、reduced motion/transparency 等状态，不为“完整”制造业务不存在的状态。

### 4. 做负向检查

对照 anti-patterns，重点排查：

- 全页玻璃化；
- glass-on-glass；
- 三栏滥用；
- toolbar button soup；
- 嵌套滚动；
- 假 macOS chrome；
- 关键错误只用 Toast；
- 200% 仍强制原布局。

### 5. 验证

实现后验证真实行为，尤其：

- 长内容展开后的按钮位置；
- 窗口高度/宽度变化；
- 200% 缩放；
- 键盘与焦点；
- Reduce Motion / Transparency；
- 图表容器尺寸变化；
- 模态/菜单层级与焦点恢复。

使用环境允许的浏览器工具；不依赖特定插件。构建通过不等于视觉验收。

## 资源路由

按任务读取最少必要文件；完整规范再组合读取。

- **颜色、字体、间距、基础视觉**：`references/visual-system.md`
- **Liquid Glass 语义、regular/clear、光学、降级、性能**：`references/materials-and-optics.md`
- **布局、滚动、稳定底栏、短屏/窄屏**：`references/layout-and-scroll.md`
- **Toolbar、Sidebar、Inspector、Search、Menu、Selection**：`references/window-and-navigation.md`
- **组件、表单、图表、状态与动效**：`references/components-and-states.md`
- **键盘、对比度、缩放、系统辅助偏好**：`references/accessibility.md`
- **选择页面骨架**：`references/page-archetypes.md`
- **生成/审查前的负向约束**：`references/anti-patterns.md`
- **实现/审查验收**：`references/validation.md`
- **起步样式**：`assets/foundation.css`，按现有 Token 转换；不是全局 reset，不直接替换现有样式。

### 推荐组合

- **完整 UI 规范**：视觉系统 + 材质 + 页面范式 + 布局滚动 + 窗口导航 + 组件状态 + 可访问性 + 验收。
- **现有项目实施**：页面范式 + 布局滚动 + 材质 + 相关组件 + anti-patterns + 验收。
- **审查**：anti-patterns + 可访问性 + 布局滚动 + 验收，再按发现的问题读取具体模块。
- **Dashboard / 数据产品**：视觉系统 + 材质 + components-and-states + 布局滚动 + 可访问性。
- **地图/媒体/画布**：材质（重点 clear）+ window/navigation + page-archetypes + accessibility。

## 交付要求

完整规范须包含：

- 色值与字体层级；
- 材质选择理由；
- 页面范式与布局合同；
- 导航、Toolbar、Search、Sidebar/Inspector 规则；
- 滚动条、溢出、固定操作；
- 组件与关键状态；
- Accessibility；
- Anti-pattern 检查；
- 验收矩阵。

实现交付说明修改范围、实际验证和未验证限制。不自行发布、改变系统偏好或声称完成未执行的检查。

## 官方边界

本 Skill 的 Web 参数属于项目基线，不声称替代 Apple HIG。需要核实原生行为或最新系统变化时，以 Apple 官方为准：

- https://developer.apple.com/design/human-interface-guidelines/materials
- https://developer.apple.com/design/human-interface-guidelines/designing-for-macos/
- https://developer.apple.com/design/human-interface-guidelines/toolbars
- https://developer.apple.com/design/human-interface-guidelines/sidebars
- https://developer.apple.com/design/human-interface-guidelines/searching
- https://developer.apple.com/documentation/technologyoverviews/liquid-glass
