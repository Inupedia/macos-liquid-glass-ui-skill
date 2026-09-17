# 原生 macOS 结构：Window、Toolbar、Sidebar、Search 与 Commands

## Window

macOS 产品默认允许窗口变化。对每个主要窗口明确：

- 最小可用尺寸；
- 默认尺寸；
- 是否支持多窗口；
- 是否支持全屏；
- 关闭/恢复行为；
- toolbar/sidebar/inspector 在窄窗口的降级。

不要用固定截图尺寸推导所有布局。

## Toolbar

Toolbar 用于高频命令、标题、导航和 search。

- leading：返回/前进、sidebar toggle、标题；
- center：高频视图/编辑控制；
- trailing：搜索、分享、更多、关键动作；
- 通常控制在 1–3 个语义组；
- 允许系统处理窄窗口 overflow；
- 不给每个 item 自画 bezel；
- 重要命令同时存在于 Menu/Commands 或其他可靠入口。

如果 toolbar 支持用户自定义，不假设某个可移除 item 永远存在。

## Sidebar

Sidebar 用于稳定导航和集合，不用于当前对象属性编辑。

要求：

- 选中项明确；
- 支持折叠/恢复；
- 窄窗口优先折叠；
- 与 content 形成明确功能层/内容层关系；
- 搜索框只有在搜索 sidebar 所代表集合时放在这里。

## Inspector

Inspector 用于当前对象属性：

- selection 改变时同步；
- 无选择有明确 empty/default state；
- 窄窗口可转 overlay/panel；
- 不承担一级导航。

## Search

明确搜索范围：

- app-wide
- current collection
- current document
- systemwide/Spotlight integration

根据业务支持 suggestions、recent、scope、tokens。展示历史前考虑隐私并提供清除能力。

## Menus and Commands

桌面端命令模型至少考虑：

- Menu bar
- Toolbar
- Context menu
- Keyboard shortcut
- Command palette（专业工具可选）

同一业务动作应共享 command/state，而不是四个入口四套逻辑。

常见能力：

- New/Open/Close
- Save（若产品存在显式保存）
- Undo/Redo
- Cut/Copy/Paste
- Find
- View / Sidebar / Inspector toggle
- Window commands
- Help
- App Settings

不要为了“简洁”移除用户预期的标准桌面能力。

## Selection

List/Table/Outline 明确：

- single / multi select；
- Cmd-click；
- Shift range；
- focus vs selection；
- keyboard movement；
- delete/rename behavior；
- inspector 和 command enablement。

## Sheets / Popovers / Panels

Sheet：需要集中完成且与当前 window 强关联的任务。

Popover：短、轻、上下文相关。

Panel：工具、检查器、辅助工作区；明确是否 floating/key/main。

Dialog：需要立即处理的重要决定。

不要用 modal 解决所有复杂度。

## Multi-window

支持多窗口时：

- 每个 window 的 selection、navigation、toolbar state 不意外互串；
- app-global state 与 window-local state 分开；
- 菜单命令作用于 key window 时语义明确；
- 恢复窗口时不恢复到已失效对象。

## Active / Inactive Window

玻璃、vibrancy、selection 和 toolbar 状态在非 key window 下应自然降级。不要用固定高亮让后台窗口看起来仍在主操作状态。

## Content Extension

视觉丰富内容（图片、地图、媒体）可以延伸到 sidebar/toolbar 后方以强化 Liquid Glass 层次；普通表格、表单和文档不为了效果强行延伸背景。

## 结构审查问题

1. Toolbar 是否只有高频命令？
2. 重要命令在 toolbar 隐藏/overflow 后是否仍能访问？
3. Sidebar 与 Inspector 是否职责混淆？
4. Search 范围是否清楚？
5. Window 缩小时是结构降级还是控件挤压？
6. Menu/shortcut 与按钮状态是否一致？
7. 多窗口时状态 ownership 是否正确？
