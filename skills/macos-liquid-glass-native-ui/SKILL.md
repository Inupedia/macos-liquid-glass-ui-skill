---
name: macos-liquid-glass-native-ui
description: 为原生 macOS SwiftUI / AppKit 产品设计、实现或审查 Liquid Glass 界面。优先系统组件与系统材质，覆盖 macOS 26 Liquid Glass API（glassEffect / GlassEffectContainer / NSGlassEffectView）与版本合同、窗口、Toolbar、Sidebar、Inspector、Search、Menu/Command、Sheet/Popover、可访问性环境键与原生验证；不使用 Web backdrop-filter 近似替代系统行为。
---

# macOS Liquid Glass Native UI

用于 **原生 macOS** 产品。目标不是手工复刻玻璃，而是让系统提供的窗口、导航、控制和 Liquid Glass 行为发挥作用，再对真正需要的自定义区域做克制扩展。

## 适用

- SwiftUI macOS App
- AppKit App
- SwiftUI + AppKit 混合工程
- 原生 macOS UI 设计审查、迁移与现代化

不适用：

- 普通 Web / Electron / Tauri Web UI：使用 `macos-liquid-glass-ui`
- App Icon：使用 `macos-liquid-glass-icon`

## 原生优先原则

1. **优先标准组件。** Toolbar、Sidebar、List、Table、Search、Menu、Sheet、Popover、Button 等只要系统能力足够，就不要自己画一套玻璃皮肤。
2. **不要给系统已经处理的区域重复加 glass effect。** Toolbar / navigation controls 获得系统外观时，不再叠 raw glass。Apple 原文：`Reduce your use of custom backgrounds in controls and navigation elements.` 删除时用正确替代：按钮用 `.buttonStyle(.glass)`，滚动边缘可读性用 `scrollEdgeEffectStyle(_:for:)`，内容延伸到 sidebar/inspector 之下用 `backgroundExtensionEffect()` / `NSBackgroundExtensionView`。
3. **Liquid Glass 属于控制和导航层。** 内容区默认使用正常内容材质；自定义 glass 只给少量需要浮于内容上方的交互。Apple 原文：`Limit the use of Liquid Glass effects onscreen at the same time.`
4. **自定义 glass 必须用容器合并。** 同屏 ≥2 个 `glassEffect` 时包进一个 `GlassEffectContainer`，否则会掉性能且无法 morph。
5. **`.ultraThinMaterial` 不是 Liquid Glass。** Material 没有折射、边缘高光、指针响应与 morph；它只在为更低 deployment target 写降级分支时作兜底。
6. **窗口可缩放是默认前提。** 设计从最小可用尺寸到大窗口都成立，不把单一截图当完成状态。
7. **命令是桌面端的一等公民。** 重要能力考虑 Toolbar、Menu、Commands、Keyboard shortcut、Context menu 的一致入口。
8. **系统辅助设置优先。** Reduce Transparency / Increase Contrast / Reduce Motion / Show Borders 要通过环境键读取并改变行为，不强行覆盖。
9. **采用平台约定。** 不把 iPhone 底部导航、Web 管理后台操作习惯机械搬到 Mac。

## 版本合同

macOS 26.0+ 引入的 Liquid Glass API（签名与可用性详解见 `references/swiftui-appkit.md` `2）：

| 平台 | 符号 | 可用性 |
| --- | --- | --- |
| SwiftUI | `glassEffect(_:in:)`、`GlassEffectContainer`、`glassEffectID(_:in:)`、`glassEffectUnion(id:namespace:)`、`Glass`、`GlassEffectTransition` | macOS 26.0+ |
| SwiftUI | `PrimitiveButtonStyle.glass` / `.glassProminent` / `.glass(_:)`、`GlassButtonStyle`、`GlassProminentButtonStyle` | macOS 26.0+ |
| SwiftUI | `ToolbarSpacer` / `SpacerSizing`、`ConcentricRectangle`、`ScrollEdgeEffectStyle` + `scrollEdgeEffectStyle(_:for:)`、`safeAreaBar(edge:alignment:spacing:content:)`、`Shape.rect(corners:isUniform:)` | macOS 26.0+ |
| SwiftUI | `backgroundExtensionEffect()` | **macOS 可用性未确证**：文档元数据列 macOS 26.0，符号页 availability 未显示 macOS；用前在 SDK 核实 |
| AppKit | `NSGlassEffectView`（`contentView` / `cornerRadius` / `style` / `tintColor`；`Style` 仅 `.clear` / `.regular`）、`NSBackgroundExtensionView`、`NSButton.BezelStyle.glass` | macOS 26.0+ |
| AppKit | `NSGlassEffectView.effectIsInteractive` | **macOS 27.0+**（不是 26.0） |

`#available` 分支模式：把 glass 代码收进 `@available(macOS 26.0, *)` 类型，调用点只留一处 `if #available`；降级分支必须注释标明「legacy fallback，非 Liquid Glass」。26 与 27 的差异（如 `effectIsInteractive`）用单独的 `if #available(macOS 27.0, *)`。

逃生舱：`UIDesignRequiresCompatibility`（Info.plist）。用最新 SDK 构建但保持旧外观，用于争取迁移时间，不要作为长期方案。

**不要猜测 API 名、参数或版本号。** 写入代码前在目标 SDK 中 ⌥-click 复核；本文档已发现文档元数据与符号页 availability 冲突的案例，见 `references/swiftui-appkit.md` `2.5。

## 工作流程

### 1. 识别工程

实施前检查：SwiftUI / AppKit / hybrid；deployment target；WindowGroup / DocumentGroup / NSWindow 结构；已有 NavigationSplitView / NSSplitViewController；Toolbar / Commands / Menu 实现；是否存在自定义 VisualEffect / glass 封装；未提交修改和用户限定范围。

不要为了 Liquid Glass 迁移重写整个架构。

### 2. 建立窗口合同

记录：Window 类型和最小尺寸；Sidebar / content / inspector 关系；Toolbar 分组；Search 范围与 placement；当前对象选择模型；Sheet / Popover / Panel 归属；哪些命令必须在 Menu/Shortcut 仍可访问。

### 3. 优先系统表现

涉及弹窗、Sheet、Popover、Picker/Selector、Segmented、Table 或 Outline 时，**必须读取 `references/native-components.md`**。先决定系统组件与交互模型，再进入 visual polish；仅给出「系统自带组件即可」不构成完整的组件设计。明示选择状态、排序/过滤/多选、窗口归属、焦点恢复与失败恢复。

先尝试系统组件和平台 API；只有系统组件无法表达产品需求时才自定义。

自定义时先问：是否真的需要 glass？是否应该是 button/control style，而不是给容器 raw glass effect？是否包进了 `GlassEffectContainer`？是否能保持 content layer 稳定？系统辅助设置变化后是否仍然成立？

### 4. 验证

至少检查：小/中/大窗口；Light / Dark；Sidebar 展开/收起；Toolbar overflow / customization（若支持）；隐藏 item 后无空槽位；Keyboard-only；Menu/Command parity；A1 `accessibilityReduceTransparency`；A2 `colorSchemeContrast == .increased`；A3 `accessibilityReduceMotion`；A4 `accessibilityShowBorders`；Sheet/Popover focus 和恢复；多窗口（若产品支持）。

Liquid Glass 专项性能：同屏自定义 glass 数量与容器覆盖率，并用 Instruments 的 Animation Hitches 实测。数值上限自己定并写进交付说明，**不要声称是 Apple 官方数值**。清单见 `references/validation.md`。

## 资源路由

- 弹窗、Selector、Table、Outline 组件级选型、状态、键盘与验收：`references/native-components.md`
- SwiftUI 与 AppKit 实现策略、API 签名与版本合同：`references/swiftui-appkit.md`
- 窗口、Toolbar、Sidebar、Search、Commands 结构 API：`references/native-structure.md`
- 场景与文稿生命周期（`MenuBarExtra`、`Settings`、`DocumentGroup` / `NSDocument`、窗口还原、Stage Manager、多显示器、Dock、Quick Look）：`references/native-scenes-and-documents.md`
- 输入、文本系统与本地化（拖放 / `Transferable`、`NSPasteboard`、`TextEditor` / TextKit、IME、String Catalogs、RTL、启动性能）：`references/native-input-and-localization.md`
- 原生验收清单与交付模板：`references/validation.md`

若需要 Web 视觉 token、Web page archetype 或 CSS fallback，不要混进本 Skill；转到 `macos-liquid-glass-ui`。App Icon / 产品图标转到 `macos-liquid-glass-icon`。

## 交付要求

组件专项交付还要列出组件 Variant、结构、selection ownership、输入和错误状态、键盘路径，以及实际验证的窗口/系统偏好条件。

设计/实现结果应说明：哪些区域直接使用系统组件；哪些区域做了自定义及原因；自定义 glass 的具体用途、数量与容器归属；窗口和命令模型；实际验证过的系统设置与窗口尺寸；OS build、Xcode/SDK 版本、是否做了 26.x vs 27.x 双版本验证；未验证限制。

不要声称手工参数是 Apple 官方固定值。官方行为以当前 SDK 和 Apple 文档为准。

## 边界

本 Skill 覆盖三块：

1. **材质与实现**：`swiftui-appkit.md`（API 签名、版本合同、禁止→替代 API、辅助功能键）；
2. **结构与场景**：`native-structure.md`（窗口、Toolbar、Sidebar、Inspector、Search、Commands）、`native-scenes-and-documents.md`（`MenuBarExtra`、`Settings`、文稿生命周期、窗口还原、多显示器、Dock、Quick Look）；
3. **输入与本地化**：`native-input-and-localization.md`（拖放、剪贴板、文本编辑、IME、String Catalogs、格式化、RTL）。

仍不在本 Skill 范围内的：具体业务领域 UI（图表库、媒体编解码、网络层）、Web 前端实现、App Icon 绘制。需要时按 Apple 官方文档或对应 Skill 处理。

## 官方参考

- Liquid Glass 技术总览：https://developer.apple.com/documentation/technologyoverviews/liquid-glass
- Adopting Liquid Glass（迁移口径与「删除自定义背景」原文）：https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass
- `glassEffect(_:in:)`：https://developer.apple.com/documentation/swiftui/view/glasseffect(_:in:)
- Applying Liquid Glass to custom views（容器合并与性能警告原文）：https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views
- `GlassEffectContainer`：https://developer.apple.com/documentation/swiftui/glasseffectcontainer
- `NSGlassEffectView`：https://developer.apple.com/documentation/appkit/nsglasseffectview
- `NSBackgroundExtensionView`：https://developer.apple.com/documentation/appkit/nsbackgroundextensionview
- `accessibilityReduceTransparency`：https://developer.apple.com/documentation/swiftui/environmentvalues/accessibilityreducetransparency
- `accessibilityShowBorders`：https://developer.apple.com/documentation/swiftui/environmentvalues/accessibilityshowborders
- HIG — Designing for macOS：https://developer.apple.com/design/human-interface-guidelines/designing-for-macos/
- HIG — Materials：https://developer.apple.com/design/human-interface-guidelines/materials
- HIG — Toolbars：https://developer.apple.com/design/human-interface-guidelines/toolbars
- HIG — Sidebars：https://developer.apple.com/design/human-interface-guidelines/sidebars
- HIG — Searching：https://developer.apple.com/design/human-interface-guidelines/searching
