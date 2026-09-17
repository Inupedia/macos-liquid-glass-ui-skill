---
name: macos-liquid-glass-native-ui
description: 为原生 macOS SwiftUI / AppKit 产品设计、实现或审查 Liquid Glass 界面。优先系统组件与系统材质，覆盖窗口、Toolbar、Sidebar、Inspector、Search、Menu/Command、Sheet/Popover、可访问性与原生验证；不使用 Web backdrop-filter 近似替代系统行为。
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
2. **不要给系统已经处理的区域重复加 glass effect。** Toolbar / navigation controls 获得系统外观时，不再叠 raw glass。
3. **Liquid Glass 属于控制和导航层。** 内容区默认使用正常内容材质；自定义 glass 只给少量需要浮于内容上方的交互。
4. **窗口可缩放是默认前提。** 设计从最小可用尺寸到大窗口都成立，不把单一截图当完成状态。
5. **命令是桌面端的一等公民。** 重要能力考虑 Toolbar、Menu、Commands、Keyboard shortcut、Context menu 的一致入口。
6. **系统设置优先。** Reduce Transparency、Increase Contrast、Reduce Motion、Show Borders、Liquid Glass 外观偏好等由系统或环境驱动，不强行覆盖。
7. **采用平台约定。** 不把 iPhone 底部导航、Web 管理后台操作习惯机械搬到 Mac。

## 工作流程

### 1. 识别工程

实施前检查：

- SwiftUI / AppKit / hybrid
- Deployment target
- WindowGroup / DocumentGroup / NSWindow 结构
- 已有 NavigationSplitView / NSSplitViewController
- Toolbar / Commands / Menu 实现
- 是否存在自定义 VisualEffect / glass 封装
- 未提交修改和用户限定范围

不要为了 Liquid Glass 迁移重写整个架构。

### 2. 建立窗口合同

记录：

- Window 类型和最小尺寸
- Sidebar / content / inspector 关系
- Toolbar 分组
- Search 范围
- 当前对象选择模型
- Sheet / Popover / Panel 归属
- 哪些命令必须在 Menu/Shortcut 仍可访问

### 3. 优先系统表现

先尝试系统组件和平台 API；只有系统组件无法表达产品需求时才自定义。

自定义时先问：

- 是否真的需要 glass？
- 是否应该是 button/control style，而不是给容器 raw glass effect？
- 是否能保持 content layer 稳定？
- 系统辅助设置变化后是否仍然成立？

### 4. 验证

至少检查：

- 小/中/大窗口
- Light / Dark
- Sidebar 展开/收起
- Toolbar overflow / customization（若支持）
- Keyboard-only
- Menu/Command parity
- Reduce Motion / Transparency
- Increase Contrast / Show Borders
- Sheet/Popover focus 和恢复
- 多窗口（若产品支持）

## 资源路由

- SwiftUI 与 AppKit 实现策略：`references/swiftui-appkit.md`
- 窗口、Toolbar、Sidebar、Search、Commands：`references/native-structure.md`
- 原生验收：`references/validation.md`

若需要 Web 视觉 token、Web page archetype 或 CSS fallback，不要混进本 Skill；转到 `macos-liquid-glass-ui`。

## 交付要求

设计/实现结果应说明：

- 哪些区域直接使用系统组件；
- 哪些区域做了自定义，为什么；
- 自定义 glass 的具体用途；
- 窗口和命令模型；
- 实际验证过的系统设置与窗口尺寸；
- 未验证限制。

不要声称手工参数是 Apple 官方固定值。官方行为以当前 SDK 和 Apple 文档为准。

## 官方参考

- https://developer.apple.com/documentation/technologyoverviews/liquid-glass
- https://developer.apple.com/design/human-interface-guidelines/designing-for-macos/
- https://developer.apple.com/design/human-interface-guidelines/materials
- https://developer.apple.com/design/human-interface-guidelines/toolbars
- https://developer.apple.com/design/human-interface-guidelines/sidebars
- https://developer.apple.com/design/human-interface-guidelines/searching
