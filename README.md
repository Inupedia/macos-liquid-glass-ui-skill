# macOS Liquid Glass UI Skill

让 AI Agent 为不同产品设计、实现和审查一致的 **macOS 26 Liquid Glass 风格 Web UI**。

这套 Skill 将视觉风格与布局行为一起定义：从完整的明暗色板、玻璃材质、字体与圆角，到稳定的底部操作区、滚动条、响应式布局和组件状态。适用于产品工作台、管理界面和演示页面，也可以只用来生成完整的 UI 规范或提示词。

它是供 Agent 读取的设计与实施指南，附带可选的基础 CSS；不依赖特定前端框架。Web 玻璃效果是视觉近似，参数属于本项目的设计基线，并非 Apple 官方固定参数。本项目与 Apple 无隶属关系。

## 快速安装

安装了 Node.js 和 npm 后，在需要使用 Skill 的项目目录运行：

```bash
npx skills add Inupedia/macos-liquid-glass-ui-skill --skill macos-liquid-glass-ui
```

按提示选择 Agent。默认安装到当前项目；需要跨项目使用时，添加 `--global`。

**为 Codex 和 Cursor 全局安装：**

```bash
npx skills add Inupedia/macos-liquid-glass-ui-skill --skill macos-liquid-glass-ui --agent codex cursor --global
```

只使用其中一个 Agent 时，保留对应名称即可。安装流程与选项参考 [Skills CLI 文档](https://skills.sh/docs/cli)。安装后开启新会话；若客户端未刷新技能列表，可重启客户端。

## 直接让 Agent 安装

将下面这段话发给具备终端或 Skill 安装能力的 Agent：

```text
请从 https://github.com/Inupedia/macos-liquid-glass-ui-skill 安装
macos-liquid-glass-ui Skill，供当前 Agent 跨项目使用。
Skill 位于 skills/macos-liquid-glass-ui/。
请使用可用的 Skill 安装器，或将完整目录安装到当前 Agent 的用户级技能目录。
必须保留 SKILL.md、agents/、references/ 和 assets/。
如果已有同名且经过本地修改的 Skill，请先说明差异，避免覆盖本地定制。
安装后检查 SKILL.md 和资源文件是否完整，并说明如何调用。
```

Codex 内置 Skill Installer 可使用这个仓库路径：

```text
https://github.com/Inupedia/macos-liquid-glass-ui-skill/tree/main/skills/macos-liquid-glass-ui
```

## 手动安装

下载仓库后，将整个 `skills/macos-liquid-glass-ui` 文件夹复制到目标目录，不要只复制 `SKILL.md`。

| Agent | 用户级目标目录 |
| --- | --- |
| Codex | `$CODEX_HOME/skills/macos-liquid-glass-ui/`，默认 `~/.codex/skills/macos-liquid-glass-ui/` |
| Cursor | `~/.cursor/skills/macos-liquid-glass-ui/` |

Cursor 也支持放入项目的 `.cursor/skills/macos-liquid-glass-ui/`，见 [Cursor Skills 文档](https://cursor.com/docs/skills)。其他 Agent 请使用其支持的 Skill 目录和安装方式。

## 如何使用

在 Codex 中可显式输入 `$macos-liquid-glass-ui`。其他 Agent 可以直接要求使用 `macos-liquid-glass-ui` Skill。

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

## 规范覆盖范围

| 领域 | 包含内容 |
| --- | --- |
| 视觉系统 | 明暗主题色板、语义色、字体层级、间距、圆角、边框、阴影、玻璃材质与降级 |
| 布局 | 锁高工作台与自然内容页、区域伸缩、稳定底部操作、长文本与溢出策略 |
| 滚动与适配 | 滚动主体、系统滚动条偏好、窄屏与短屏、缩放、软键盘和安全区域 |
| 组件 | 按钮、表单、表格、菜单、弹窗、抽屉、提示和焦点行为 |
| 动态展示 | 加载、空态、错误、重试、结果、流程阶段、图表与动效 |
| 验收 | 操作可达性、对比度、键盘访问、布局稳定性及浏览器验证记录 |

页面或面板的主操作稳定在所属容器底部；搜索、筛选、行内编辑等局部操作仍放在操作对象旁。滚动条遵循系统与浏览器偏好，不全局隐藏。玻璃主要用于导航和控制层，正文与图表使用稳定底色。

Skill 会根据产品选用布局，不将单页、三栏或某个业务流程强加给所有项目。已有品牌规范、已批准的设计和用户限定的修改范围优先。

## 仓库结构

```text
skills/macos-liquid-glass-ui/
├── SKILL.md
├── agents/openai.yaml
├── assets/foundation.css
└── references/
    ├── visual-system.md
    ├── layout-and-scroll.md
    ├── components-and-states.md
    └── validation.md
```

- [Skill 入口](skills/macos-liquid-glass-ui/SKILL.md)：触发范围、工作流程和资源路由。
- [视觉系统](skills/macos-liquid-glass-ui/references/visual-system.md)：颜色、材质、字体与尺寸。
- [布局与滚动](skills/macos-liquid-glass-ui/references/layout-and-scroll.md)：高度、固定操作、自适应与滚动行为。
- [组件与状态](skills/macos-liquid-glass-ui/references/components-and-states.md)：交互、图表与状态展示。
- [验收规范](skills/macos-liquid-glass-ui/references/validation.md)：行为测试与交付要求。
- [基础 CSS](skills/macos-liquid-glass-ui/assets/foundation.css)：可选的 Token 和布局起点，需适配现有项目，不是全局重置样式。

## 更新与验证

通过 Skills CLI 安装后，可运行：

```bash
npx skills update macos-liquid-glass-ui
```

全局安装时添加 `--global`。手动安装时，请比较本地定制后更新完整目录。

可以先检查仓库中的技能是否被发现：

```bash
npx skills add Inupedia/macos-liquid-glass-ui-skill --list
```

安装成功表示 Agent 能读取这套规范；具体产品的视觉质量仍需在真实页面中验证。请要求 Agent 区分已实施、已构建和已在浏览器中验证的内容。
