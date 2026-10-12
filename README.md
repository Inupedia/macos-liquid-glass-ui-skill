# macOS Liquid Glass Skills

面向 AI 编程助手的 macOS Liquid Glass 设计规范，覆盖 Web 界面、原生 macOS 应用和 App Icon。

这套 Skill 侧重实际开发中的布局、组件、交互与验收，可用于新项目设计、现有界面改造和代码审查。它不要求替换项目已有的技术栈或组件库。

## 安装

查看可用 Skill：

```bash
npx skills add Inupedia/macos-liquid-glass-ui-skill --list
```

为 Codex、Cursor 全局安装全部三个 Skill：

```bash
npx skills add Inupedia/macos-liquid-glass-ui-skill \
  --skill '*' --agent codex cursor --global --yes
```

也可以只安装需要的 Skill：

```bash
npx skills add Inupedia/macos-liquid-glass-ui-skill --skill macos-liquid-glass-ui
```

管理已安装的 Skill：

```bash
npx skills ls -g
npx skills update -g
```

## 包含的 Skill

| Skill | 适用场景 | 主要内容 |
| --- | --- | --- |
| [macos-liquid-glass-ui](skills/macos-liquid-glass-ui/SKILL.md) | Web、Vue、React、Electron、Tauri | 材质、页面布局、导航、组件和交互规范 |
| [macos-liquid-glass-native-ui](skills/macos-liquid-glass-native-ui/SKILL.md) | SwiftUI、AppKit | 系统组件、窗口、Toolbar、Sheet、菜单与 Liquid Glass API |
| [macos-liquid-glass-icon](skills/macos-liquid-glass-icon/SKILL.md) | macOS、iOS、iPadOS App Icon | 图标设计、风格一致性、分层交付与 Icon Composer |

三个 Skill 分开维护：Web 使用适合浏览器的材质实现；原生 macOS 优先使用系统组件；图标设计不混入页面和工具栏控件。

## 设计范围

Web Skill 不只定义配色和模糊效果，还包括：

- Toolbar、Sidebar、Inspector、Search 等桌面式信息架构
- Button、Dialog、Popover、Select、Combobox、Table 等组件的结构、状态和交互
- 滚动、窄窗口、短屏、200% 文字缩放与键盘操作
- 无障碍、系统偏好、深色模式及性能约束
- Vue / React、Element Plus、Tailwind、Electron / Tauri 等实现参考

**组件规范**

| 文档 | 内容 |
| --- | --- |
| [Component Design Contract](skills/macos-liquid-glass-ui/references/component-design-contract.md) | 组件选型、变体、结构、材质、状态和验收 |
| [Actions / Navigation / Feedback](skills/macos-liquid-glass-ui/references/actions-navigation-feedback-components.md) | 按钮、导航、反馈 |
| [Overlays & Dialogs](skills/macos-liquid-glass-ui/references/overlays-and-dialog-components.md) | Dialog、Sheet、Popover、Menu |
| [Selection & Input](skills/macos-liquid-glass-ui/references/selection-and-input-components.md) | Select、Combobox、Segmented、表单 |
| [Tables & Data](skills/macos-liquid-glass-ui/references/tables-and-data-components.md) | 排序、筛选、选择、批量操作 |

[组件交互示例](skills/macos-liquid-glass-ui/assets/component-showcase.html) · [CSS 配方](skills/macos-liquid-glass-ui/assets/component-recipes.css) · [基础 Tokens](skills/macos-liquid-glass-ui/assets/foundation.css)

克隆仓库后，在浏览器中打开 `skills/macos-liquid-glass-ui/assets/component-showcase.html`，可查看 Dialog、Select 和 Table 的交互示例。示例仅供设计与开发参考，不是完整的生产组件库。

## 使用示例

**Web 界面改造**

```text
使用 $macos-liquid-glass-ui 改造当前 Vue / React 项目。
保留现有组件库和业务逻辑，检查页面结构、Toolbar、Sidebar、
弹窗、Select、Table 的状态与交互，并验证响应式和无障碍体验。
```

**原生 macOS 应用**

```text
使用 $macos-liquid-glass-native-ui 检查并完善当前 SwiftUI 项目。
优先使用系统 Toolbar、Sidebar、Sheet 和 Menu，
检查窗口缩放、键盘操作以及系统辅助功能设置。
```

**App Icon**

```text
使用 $macos-liquid-glass-icon 为当前产品设计 App Icon。
从产品含义确定轮廓和图层，生成视觉稿，
检查小尺寸识别度，并提供 Icon Composer 分层建议。
```

图标示例：

![Chinese Zodiac Liquid Glass icon family](assets/examples/chinese-zodiac-liquid-glass.png)

*AI 生成的图标仅作为视觉参考。正式图标需在 Icon Composer / Xcode 中完成制作与验证。*

## 测试与维护

```bash
python3 -m unittest discover -s tests
python3 scripts/validate_skills.py --strict
python3 scripts/run_evals.py --list
```

`SKILL.md` 用于入口判断和工作流程，详细规则放在 `references/` 中按需引用。仓库包含结构校验、行为测试用例和 CI 检查。真实 Agent 的行为评分需要额外配置执行环境，参见 [Evals 文档](docs/evals.md)。

## 参考资料

[Apple Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/) · [Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/liquid-glass) · [Icon Composer](https://developer.apple.com/icon-composer/) · [skills.sh](https://skills.sh/)

本项目与 Apple 无隶属关系。Web 端采用视觉近似方案；原生 macOS 行为以 Apple SDK 和官方文档为准。
