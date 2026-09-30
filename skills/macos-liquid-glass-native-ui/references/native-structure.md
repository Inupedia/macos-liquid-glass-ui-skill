# 原生 macOS 结构：Window、Toolbar、Sidebar、Search 与 Commands

本文件只覆盖「结构与系统 API 选择」。Liquid Glass 材质实现细节见 `swiftui-appkit.md`，验收见 `validation.md`。

## Window

macOS 产品默认允许窗口变化。对每个主要窗口明确：

- 最小可用尺寸；
- 默认尺寸；
- 是否支持多窗口；
- 是否支持全屏；
- 关闭/恢复行为；
- toolbar/sidebar/inspector 在窄窗口的降级。

不要用固定截图尺寸推导所有布局。

相关 API：`WindowGroup` / `Window` / `DocumentGroup`（SwiftUI），`NSWindow` / `NSWindowController`（AppKit）。窗口尺寸与恢复语义属于系统职责，不要自建。

## Toolbar

Toolbar 用于高频命令、标题、导航和 search。

- leading：返回/前进、sidebar toggle、标题；
- center：高频视图/编辑控制；
- trailing：搜索、分享、更多、关键动作；
- 通常控制在 1–3 个语义组；
- 允许系统处理窄窗口 overflow；
- 不给每个 item 自画 bezel；
- 重要命令同时存在于 Menu/Commands 或其他可靠入口。

### 分组 API

| 需求 | API | 可用性 |
| --- | --- | --- |
| 分隔共享同一背景的 item（固定 spacer） | `ToolbarSpacer(.fixed, placement:)` | macOS 26.0+ |
| 弹性 spacer | `ToolbarSpacer(.flexible)`（`init` 默认值即 `.flexible`） | macOS 26.0+ |
| AppKit 分组的固定间隔 | `NSToolbarItem.Identifier.space` | 长期存在 |
| 自定义 toolbar item 归属 | `ToolbarItem(placement:)` / `ToolbarItemGroup` | 稳定 |

```swift
.toolbar {
    ToolbarItem(placement: .primaryAction) { FavoriteButton() }
    ToolbarSpacer(.fixed, placement: .primaryAction)   // 同组内分隔，优于自己塞 padding
    ToolbarItem(placement: .primaryAction) { ShareButton() }
}
```

### 隐藏 item：隐藏整个 item

官方明确点名的错误姿势：隐藏 item **内部的视图** → 界面上留下一个空 toolbar item。

> Check how you hide toolbar items. If you see an empty toolbar item without any content, your app might be hiding the view in the toolbar item instead of the item itself.

| 平台 | 正确 API | 可用性 |
| --- | --- | --- |
| SwiftUI | `ToolbarContent.hidden(_ hidden: Bool = true)`，作用于 `ToolbarItem` 本身 | 文档列 macOS 15.0+（以 SDK 为准） |
| AppKit | `NSToolbarItem.isHidden = true`，作用于 item 本身 | macOS 15.0+ |

```swift
ToolbarItem(placement: .primaryAction) { ShareButton() }
    .hidden(!canShare)          // 对 item 调用，不是对 ShareButton 内部视图
```

不要用 `opacity(0)`、`frame(width: 0)`、把内容设为 empty 之类的方式「隐藏」，它们都会留下占位。

### 用户自定义 toolbar

如果 toolbar 支持用户自定义（`NSToolbar.allowsUserCustomization`），不假设某个可移除 item 永远存在：

- 每个 item 有稳定 `identifier`；
- 关键命令在 Menu / keyboard shortcut 有独立入口；
- 检测 item 是否被移除后再决定相关 UI 状态；
- 不要在运行期重建整个 toolbar 来响应自定义变化。

## Sidebar

Sidebar 用于稳定导航和集合，不用于当前对象属性编辑。

要求：选中项明确；支持折叠/恢复；窄窗口优先折叠；与 content 形成明确功能层/内容层关系；搜索框只有在搜索 sidebar 所代表集合时放在这里。

相关 API：`NavigationSplitView` + `NavigationSplitViewVisibility`（`.automatic` / `.all` / `.doubleColumn` / `.detailOnly`，macOS 13.0+）；AppKit 用 `NSSplitViewController` 的 `NSSplitViewItem(sidebarWithViewController:)`。

### Column width

| 平台 / 场景 | API | 可用性 |
| --- | --- | --- |
| SwiftUI sidebar / content 列 | `navigationSplitViewColumnWidth(min:ideal:max:)`，或单值 `navigationSplitViewColumnWidth(_ width: CGFloat)` | macOS 13.0+ |
| SwiftUI inspector 列 | `inspectorColumnWidth(min:ideal:max:)` | macOS 14.0+ |
| AppKit | `NSSplitViewItem.minimumThickness` / `maximumThickness` / `NSSplitView` 的 holding priority | 稳定 |

给 `min` 与 `max`，让系统在连续 resize 中自己插值；只给 `ideal` 会在窄窗口留下压不动或跳变的布局。

## Inspector

Inspector 用于当前对象属性：selection 改变时同步；无选择有明确 empty/default state；窄窗口可转 overlay/panel；不承担一级导航。

相关 API：`.inspector(isPresented:content:)`（macOS 14.0+）配合 `.inspectorColumnWidth(min:ideal:max:)`（macOS 14.0+）；AppKit 用 `NSSplitViewItem(inspectorWithViewController:)`。

不要自建右侧浮动面板：系统的 inspector 已处理材质、宽度约束、折叠动画与 focus。

## Search

明确搜索范围：app-wide、current collection、current document、systemwide/Spotlight integration。

根据业务支持 suggestions、recent、scope、tokens。展示历史前考虑隐私并提供清除能力。

| 需求 | API | 可用性 |
| --- | --- | --- |
| 搜索字段 | `.searchable(text:placement:prompt:)` | macOS 13.0+ |
| 可编程显示/隐藏搜索字段 | `.searchable(text:isPresented:placement:prompt:)` | macOS 14.0+ |
| 放置位置 | `SearchFieldPlacement`：`.automatic` / `.sidebar` / `.toolbar` / `.toolbarPrincipal` 等 | macOS 12.0+ |
| 范围选择 | `.searchScopes(_:scopes:)` | 稳定 |

位置与 scope 是一对：`placement: .sidebar` 时 scope 应描述 sidebar 所代表的集合；document find 不要复用同一个 search state。

## Menus and Commands

桌面端命令模型至少考虑：Menu bar、Toolbar、Context menu、Keyboard shortcut、Command palette（专业工具可选）。

同一业务动作应共享 command/state，而不是四个入口四套逻辑。SwiftUI 用 `Commands` / `.commands { }`、`CommandGroup`、`CommandMenu`；AppKit 用 `NSMenu` / `NSMenuItem` 与 responder chain。

常见能力：New/Open/Close、Save（若产品存在显式保存）、Undo/Redo、Cut/Copy/Paste、Find、View / Sidebar / Inspector toggle、Window commands、Help、App Settings。

不要为了「简洁」移除用户预期的标准桌面能力。

## Selection

List/Table/Outline 明确：single / multi select；Cmd-click；Shift range；focus vs selection；keyboard movement；delete/rename behavior；inspector 和 command enablement。

## Sheets / Popovers / Panels

Sheet：需要集中完成且与当前 window 强关联的任务。

Popover：短、轻、上下文相关。

Panel：工具、检查器、辅助工作区；明确是否 floating/key/main。

Dialog：需要立即处理的重要决定。

不要用 modal 解决所有复杂度。

**审查动作：** 检查 popover 的 content view 是否加了 `NSVisualEffectView` / 自定义背景，官方要求删除，让系统统一材质。

## Multi-window

支持多窗口时：每个 window 的 selection、navigation、toolbar state 不意外互串；app-global state 与 window-local state 分开；菜单命令作用于 key window 时语义明确；恢复窗口时不恢复到已失效对象。

## Active / Inactive Window

玻璃、vibrancy、selection 和 toolbar 状态在非 key window 下应自然降级。不要用固定高亮让后台窗口看起来仍在主操作状态。

## Content Extension

视觉丰富内容（图片、地图、媒体）可以延伸到 sidebar/toolbar/inspector 后方以强化 Liquid Glass 层次；普通表格、表单和文档不为了效果强行延伸背景。

原理（官方原文）：background extension effect 会**镜像相邻内容**让人以为它延伸到了 sidebar 之下，并**施加模糊**以保持 sidebar/inspector 的易读性。

| 平台 | API | 可用性 |
| --- | --- | --- |
| SwiftUI | `.backgroundExtensionEffect()` | `@MainActor @preconcurrency func backgroundExtensionEffect() -> some View`。**macOS 可用性未确证**：文档 JSON 元数据列 macOS 26.0，但符号页渲染的 availability 未显示 macOS；使用前在目标 SDK 中 ⌥-click 或 `swift-symbolgraph-extract` 核实，不要无条件依赖 |
| AppKit | `NSBackgroundExtensionView` | 已确证 macOS 26.0+（官方描述：可布局到 safe area 之外，如 titlebar / sidebar / inspector 之下；默认让内容留在 safe area 内，用边缘内容变体填充容器） |

三条硬约束：

1. **单实例。** 官方原文：`Apply this modifier with discretion. This should often be used with only a single instance of background content with consideration of visual clarity and performance.` 一个窗口内只对一处背景内容使用，不要给每个列表行或每张卡片都加。
2. **会被裁剪。** 该效果在容器边界内工作，不要指望它替代真实滚动内容或跨窗口；被裁剪的内容要检查是否有被切掉的关键视觉信息。
3. **注意清晰度与性能。** 镜像 + 模糊有渲染成本，且与上方 sidebar/inspector 的可读性互相牵制。rich content 上叠加后要实测滚动与 resize 帧率。

### 滚动边缘可读性

内容滚到 toolbar / 自定义 bar 下方时必须保证控件可读，**不要自己贴一层 blur**。

| 需求 | API | 可用性 |
| --- | --- | --- |
| 给滚动内容边缘加系统效果 | `scrollEdgeEffectStyle(_ style: ScrollEdgeEffectStyle?, for edges: Edge.Set)`；`ScrollEdgeEffectStyle` 取值 `.automatic` / `.hard` / `.soft` | macOS 26.0+ |
| 把自定义 bar 注册进 safe area | `safeAreaBar(edge: HorizontalEdge, alignment: VerticalAlignment = .center, spacing: CGFloat? = nil, content:)` | macOS 26.0+ |

系统 bars（toolbar 等）默认已具备该行为；只有自建 bar 才需要显式注册。官方口径：`Scroll views offer a scrollEdgeEffectStyle(_:for:) that helps maintain sufficient legibility and contrast for controls by obscuring content that scrolls beneath them.`

## 明确不覆盖

以下主题 **本 Skill 不给规则**，需要时按 Apple 官方文档处理，不要从本文件推断结论：

`MenuBarExtra`、`Settings` scene（⌘,）、`DocumentGroup` / `NSDocument` 与自动保存/版本浏览、窗口还原、Stage Manager、多显示器、Dock（`dockTile` / 最近文档）、drag & drop / `NSPasteboard`、Quick Look、`TextEditor` / TextKit、Unicode / IME / 本地化、启动性能。

## 结构审查问题

1. Toolbar 是否只有高频命令？
2. 重要命令在 toolbar 隐藏/overflow 后是否仍能访问？
3. 隐藏 item 时隐藏的是整个 item 还是 item 里的视图？
4. Sidebar 与 Inspector 是否职责混淆？
5. Search 范围与 placement 是否匹配？
6. Column width 是否给了 min/ideal/max 而不是只写 ideal？
7. Window 缩小时是结构降级还是控件挤压？
8. Menu/shortcut 与按钮状态是否一致？
9. 多窗口时状态 ownership 是否正确？
10. 是否误用了本 Skill 明确不覆盖的主题？
