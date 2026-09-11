# macOS Liquid Glass Skills

让 AI Agent 为不同产品设计、实现和审查一致的 **macOS / Apple Liquid Glass 风格 UI 与 App Icon**。

本仓库包含两个独立 Skill：

- `macos-liquid-glass-ui`：页面、组件、布局、滚动、响应式、状态与 Web 玻璃材质规范；
- `macos-liquid-glass-icon`：App Icon / 产品图标的概念设计、ChatGPT 直接生图、迭代验收，以及 Icon Composer 分层交付说明。

两者可以共享品牌色与视觉语言，但职责分开：页面 glass panel 不应直接缩小后当 App Icon，App Icon 也不应该把完整 UI 截图塞进图标里。

这套仓库供 Agent 读取和执行，不依赖特定前端框架。Web 玻璃效果与 AI 图标生成参数属于本项目设计基线，并非 Apple 官方固定参数。本项目与 Apple 无隶属关系。

## 快速安装

安装了 Node.js 和 npm 后，先查看仓库中可用 Skill：

```bash
npx skills add Inupedia/macos-liquid-glass-ui-skill --list
```

安装 UI Skill：

```bash
npx skills add Inupedia/macos-liquid-glass-ui-skill --skill macos-liquid-glass-ui
```

安装 Icon Skill：

```bash
npx skills add Inupedia/macos-liquid-glass-ui-skill --skill macos-liquid-glass-icon
```

按提示选择 Agent。默认安装到当前项目；需要跨项目使用时，添加 `--global`。

**为 Codex 和 Cursor 全局安装 UI Skill：**

```bash
npx skills add Inupedia/macos-liquid-glass-ui-skill --skill macos-liquid-glass-ui --agent codex cursor --global
```

**为 Codex 和 Cursor 全局安装 Icon Skill：**

```bash
npx skills add Inupedia/macos-liquid-glass-ui-skill --skill macos-liquid-glass-icon --agent codex cursor --global
```

只使用其中一个 Agent 时，保留对应名称即可。安装流程与选项参考 [Skills CLI 文档](https://skills.sh/docs/cli)。安装后开启新会话；若客户端未刷新技能列表，可重启客户端。

## 直接让 Agent 安装

将下面这段话发给具备终端或 Skill 安装能力的 Agent：

```text
请从 https://github.com/Inupedia/macos-liquid-glass-ui-skill 安装需要的 Skill：
- UI：skills/macos-liquid-glass-ui/
- App Icon：skills/macos-liquid-glass-icon/

请使用可用的 Skill 安装器，或将完整 Skill 目录安装到当前 Agent 的用户级技能目录。
必须保留各 Skill 下的 SKILL.md、agents/、references/，以及 UI Skill 的 assets/。
如果已有同名且经过本地修改的 Skill，请先说明差异，避免覆盖本地定制。
安装后检查 SKILL.md 和资源文件是否完整，并说明如何调用。
```

Codex 内置 Skill Installer 可直接使用：

```text
https://github.com/Inupedia/macos-liquid-glass-ui-skill/tree/main/skills/macos-liquid-glass-ui
```

或：

```text
https://github.com/Inupedia/macos-liquid-glass-ui-skill/tree/main/skills/macos-liquid-glass-icon
```

## 手动安装

下载仓库后，将需要的完整 Skill 文件夹复制到目标目录，不要只复制 `SKILL.md`。

| Agent | UI Skill | Icon Skill |
| --- | --- | --- |
| Codex | `$CODEX_HOME/skills/macos-liquid-glass-ui/` | `$CODEX_HOME/skills/macos-liquid-glass-icon/` |
| Cursor | `~/.cursor/skills/macos-liquid-glass-ui/` | `~/.cursor/skills/macos-liquid-glass-icon/` |

Cursor 也支持放入项目的 `.cursor/skills/<skill-name>/`。其他 Agent 请使用其支持的 Skill 目录和安装方式。

# macOS Liquid Glass UI Skill

## 适合做什么

`macos-liquid-glass-ui` 将视觉风格与布局行为一起定义：从完整的明暗色板、玻璃材质、字体与圆角，到稳定的底部操作区、滚动条、响应式布局和组件状态。

适用于产品工作台、管理界面和演示页面，也可以只用来生成完整 UI 规范或提示词。

### 生成完整 UI 规范

```text
使用 $macos-liquid-glass-ui，为一个面向非专业用户的知识管理产品生成完整 UI 规范。
包含明暗色值、字体、间距、材质、布局、底部操作区、滚动条、响应式规则、
组件状态和验收标准。这次只输出规范，不修改代码。
```

### 在现有项目中实施

```text
使用 macos-liquid-glass-ui Skill 完善当前项目的界面。
先检查现有技术栈和组件，说明各区域的高度、滚动归属和按钮位置，再实施。
主操作稳定在所属面板底部，中间内容展开时不能把按钮顶走。
请验证窄屏、短屏、长文本和图表容器尺寸变化，并报告实际检查结果。
```

### 仅调整局部

```text
使用 macos-liquid-glass-ui Skill，只优化中间结果区域的图表与状态展示。
保留已经认可的导航、配色和外围布局，沿用现有组件和数据含义。
```

### 审查现有界面

```text
使用 macos-liquid-glass-ui Skill 审查当前界面，暂不修改代码。
重点检查底部操作被挤走、滚动嵌套、短屏裁切、弹窗溢出、文字对比度、
键盘操作，以及加载、空态、失败和完成状态，给出触发条件和验证方式。
```

## UI 规范覆盖范围

| 领域 | 包含内容 |
| --- | --- |
| 视觉系统 | 明暗主题色板、语义色、字体层级、间距、圆角、边框、阴影、玻璃材质与降级 |
| 布局 | 锁高工作台与自然内容页、区域伸缩、稳定底部操作、长文本与溢出策略 |
| 滚动与适配 | 滚动主体、系统滚动条偏好、窄屏与短屏、缩放、软键盘和安全区域 |
| 组件 | 按钮、表单、表格、菜单、弹窗、抽屉、提示和焦点行为 |
| 动态展示 | 加载、空态、错误、重试、结果、流程阶段、图表与动效 |
| 验收 | 操作可达性、对比度、键盘访问、布局稳定性及浏览器验证记录 |

页面或面板的主操作稳定在所属容器底部；搜索、筛选、行内编辑等局部操作仍放在操作对象旁。滚动条遵循系统与浏览器偏好，不全局隐藏。玻璃主要用于导航和控制层，正文与图表使用稳定底色。

# macOS Liquid Glass Icon Skill

## 设计目标

`macos-liquid-glass-icon` 用于生成 **App Icon / 产品图标**，参考 Apple 当前 Liquid Glass 图标思路，但不把生成流程绑到外部图像 API。

核心原则：

- 当前 ChatGPT / 宿主有内置 image generation 时，直接调用它生成或编辑图片；
- 不接第三方图像 provider，不索要 API Key；
- 先冻结产品隐喻、轮廓、层级、HEX palette 和材质，再生图；
- AI 生成的 PNG 是视觉成稿/方向稿，真正上架 Apple 平台时额外给出 Icon Composer layer map；
- 不把 16–24 px 工具栏小图标强行做成重材质 App Icon。

## Generated Example — Chinese Zodiac

下面这组十二生肖图标由 `macos-liquid-glass-icon` 的图标家族流程生成：先冻结统一的材质、视角、层级和视觉语言，再只替换生肖主体，用于验证 Skill 在一组图标中的风格一致性。

![Chinese Zodiac Liquid Glass icon set](assets/examples/chinese-zodiac-liquid-glass.jpg)

> 这是 AI 生成的视觉案例，用于展示 icon family 的统一风格与构图方向；真实 Apple App Icon 上线前仍应按照 Icon Composer / Xcode 的生产流程拆分并验证图层。

### 直接生成一个 App Icon

```text
使用 $macos-liquid-glass-icon，为当前产品设计并直接生成一个 Liquid Glass 风格 App Icon。
先根据产品功能和已有 UI/品牌色确定一个核心隐喻，再调用 ChatGPT 内置图像生成。
不要使用外部图像 API。最终图标要在 64px 和 32px 仍然能辨认，并给出简短的 Icon Composer 分层说明。
```

### 从现有 Logo / Icon 改造

```text
使用 macos-liquid-glass-icon Skill，把我提供的现有 App Icon 改成 Liquid Glass 风格。
必须保留原来的品牌轮廓和主色，只简化细节、调整前后层级和玻璃材质。
直接使用图像编辑能力，不重新猜一个完全不同的图标。
```

### 先出候选方向

```text
使用 macos-liquid-glass-icon Skill，为这个产品生成 2×2 四个 App Icon 方向。
四个方向必须锁定同一 palette、材质强度、视角和细节预算，只比较不同的核心隐喻与构图。
确定方向后再生成单独的 1024×1024 定稿。
```

### 做同风格图标家族

```text
使用 macos-liquid-glass-icon Skill，为这组产品入口图标建立统一 style spec。
先锁定共同 HEX palette、层级、材质、视角、圆角语言和细节预算，再逐个生成；
不要让每张图各自发明一种玻璃效果。
```

## Icon Skill 与 oil-icon 的差异

本 Skill 借鉴“先冻结 style spec、再生图、最后 QA”的方法，但刻意去掉外部图像 API、API Key 配置和 provider fallback。

它也不依赖固定的 4×4 切图工作流：单个 App Icon 默认直接生成单图；只有概念歧义高时才先做 2×2 候选方向。

针对 Apple 平台，还增加了 Icon Composer 分层思路：视觉稿可以模拟 Liquid Glass，但生产源层应保持干净可拆，动态镜面、高光、折射、透明度和阴影留给系统/Icon Composer 处理。

## 仓库结构

```text
skills/
├── macos-liquid-glass-ui/
│   ├── SKILL.md
│   ├── agents/openai.yaml
│   ├── assets/foundation.css
│   └── references/
│       ├── visual-system.md
│       ├── layout-and-scroll.md
│       ├── components-and-states.md
│       └── validation.md
└── macos-liquid-glass-icon/
    ├── SKILL.md
    ├── agents/openai.yaml
    └── references/
        ├── icon-system.md
        ├── prompt-template.md
        └── validation.md
```

### UI Skill

- [Skill 入口](skills/macos-liquid-glass-ui/SKILL.md)：触发范围、工作流程和资源路由。
- [视觉系统](skills/macos-liquid-glass-ui/references/visual-system.md)：颜色、材质、字体与尺寸。
- [布局与滚动](skills/macos-liquid-glass-ui/references/layout-and-scroll.md)：高度、固定操作、自适应与滚动行为。
- [组件与状态](skills/macos-liquid-glass-ui/references/components-and-states.md)：交互、图表与状态展示。
- [验收规范](skills/macos-liquid-glass-ui/references/validation.md)：行为测试与交付要求。
- [基础 CSS](skills/macos-liquid-glass-ui/assets/foundation.css)：可选 Token 和布局起点。

### Icon Skill

- [Skill 入口](skills/macos-liquid-glass-icon/SKILL.md)：触发范围、直接生图规则、工作流和生产交付。
- [图标设计系统](skills/macos-liquid-glass-icon/references/icon-system.md)：轮廓、层级、palette、材质与品牌适配。
- [ChatGPT Image Prompt 模板](skills/macos-liquid-glass-icon/references/prompt-template.md)：单图、候选稿、改图和图标家族提示词。
- [图标验收](skills/macos-liquid-glass-icon/references/validation.md)：小尺寸、AI 瑕疵、材质和 Icon Composer 生产检查。

## Apple 官方生产参考

真实 Apple App Icon 的最终生产与验证以官方资料为准：

- [Human Interface Guidelines — App icons](https://developer.apple.com/design/human-interface-guidelines/app-icons)
- [Icon Composer](https://developer.apple.com/icon-composer/)
- [Creating your app icon using Icon Composer](https://developer.apple.com/documentation/xcode/creating-your-app-icon-using-icon-composer)

## 更新与验证

通过 Skills CLI 安装后，可运行：

```bash
npx skills update macos-liquid-glass-ui
npx skills update macos-liquid-glass-icon
```

全局安装时添加 `--global`。手动安装时，请比较本地定制后更新完整目录。

检查仓库中的技能是否被发现：

```bash
npx skills add Inupedia/macos-liquid-glass-ui-skill --list
```

安装成功表示 Agent 能读取规范；具体产品的 UI 或图标质量仍需在真实页面、目标尺寸，以及适用时的 Icon Composer / Xcode 中验证。请要求 Agent 区分已生成、已验收、已生产交付和已实际运行验证的状态。
