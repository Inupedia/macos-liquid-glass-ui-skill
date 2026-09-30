# 场景与文稿生命周期：MenuBarExtra、Settings、DocumentGroup、窗口还原、Stage Manager、Dock、Quick Look

> 适用范围：原生 macOS SwiftUI / AppKit 的 **Scene 声明、文稿生命周期、窗口还原、屏幕与 Dock / Quick Look 集成**。材质与玻璃规则见 `swiftui-appkit.md`，窗口 / Toolbar / Sidebar 结构见 `native-structure.md`；**本文件只管场景与文稿生命周期**。

本文件补上 SKILL.md「边界」小节里「结构与场景」这一块，并与 `native-structure.md` 的「交给其他 reference 的主题」互为指向。

## 1. MenuBarExtra：菜单栏常驻项

| 符号 | 可用性 | 说明 |
| --- | --- | --- |
| `MenuBarExtra`（`init(_:content:)` / `init(_:systemImage:content:)` / `init(content:label:)` / `init(isInserted:content:label:)` 等） | macOS 13.0+ | Scene，渲染为系统菜单栏常驻控件 |
| `Scene.menuBarExtraStyle(_:)` | macOS 13.0+ | 设置该 Scene 的菜单栏样式 |
| `MenuBarExtraStyle`：`.automatic`（`AutomaticMenuBarExtraStyle`，默认）/ `.menu`（`PullDownMenuBarExtraStyle`）/ `.window`（`WindowMenuBarExtraStyle`） | macOS 13.0+ | 三种样式 |
| `LSUIElement`（Info.plist Bool）/ `NSApplication.setActivationPolicy(_:) -> Bool` | macOS 10.0+ / macOS 10.6+ | agent app：后台运行，不出现在 Dock / 运行期改激活策略 |
| `NSApplication.ActivationPolicy`：`.regular` / `.accessory` / `.prohibited` | 文档未给引入版本 | `.accessory` 官方描述：不出现在 Dock **且没有菜单栏**，仍可被程序或点击其窗口激活 |

- 样式取舍：纯命令列表 → `.menu`（默认 `.automatic` 也解析为下拉菜单）。出现任何非 Menu 控件（`Slider`、`ProgressView`、`ScrollView`、多列布局、图表）→ 必须 `.window`，否则控件被菜单渲染吞掉。`.window` 不自己给固定宽度（`.frame(width:)`）＝ 失败；`.window` 里放 > 7 个纯 `Button` 命令且无分组 ＝ 失败（那是菜单，不是面板）。
- **玻璃来源（本文件与 `swiftui-appkit.md` 的唯一交点）**：菜单栏与 `.window` 下拉面板的材质由**系统菜单栏 / 系统 popover 窗口**提供。**禁止**在 `MenuBarExtra` 的 content builder 内出现 `.glassEffect(...)`、`GlassEffectContainer`、`NSVisualEffectView`、`.background(.ultraThinMaterial)`、自绘圆角卡片——审查时在该闭包内检索这些符号，命中即失败。
- 无 Dock 图标：纯菜单栏工具用 `LSUIElement = true` 或运行期 `NSApp.setActivationPolicy(.accessory)`。需要标准 App 菜单（Settings ⌘,、Window、Help）时**不要**用 `.accessory`（官方明确它没有菜单栏），用 `.regular` + `MenuBarExtra` 并存（Apple 的 `AppWithMenuBarExtra` 示例即 `WindowGroup` + `MenuBarExtra`）。既要 ⌘, 又声明 `.accessory` 且无自建菜单栏入口 ＝ 失败。
- 状态：`MenuBarExtra` 是 Scene，content / `label` 闭包在展示时重建，`@Observable`（`@Observable` 宏 macOS 14.0+）模型必须由 `App` 级 `@State` 或单例持有；放进菜单内容的 `@State` ＝ 关菜单即丢状态 ＝ 失败。
- 退出与前置：官方行为是**只显示在菜单栏的 App 在用户移除 extra 后被自动终止**，因此 `.menu` 内容必须含 `Button("Quit") { NSApplication.shared.terminate(nil) }`，缺退出入口 ＝ 失败（`.accessory` 下没有 ⌘Q）。打开主窗口用 `@Environment(\.openWindow)`（macOS 13.0+；`OpenWindowAction` 有 `callAsFunction(id:)` / `(value:)` / `(id:value:)`）再 `NSApplication.activate()`（macOS 14.0+）前置 App，target < 14 用 `activate(ignoringOtherApps: true)`；只 `openWindow` 不 `activate`，窗口可能落在后台 ＝ 失败。

```swift
@main
struct StatusApp: App {
    @State private var model = StatusModel()   // @Observable 需 macOS 14.0+；App 级持有，避免关菜单丢状态
    var body: some Scene {
        MenuBarExtra("Sync Status", systemImage: model.statusSymbol) {
            StatusMenu(model: model)
        }
        .menuBarExtraStyle(.menu)              // 纯命令用 .menu；出现 Slider/ScrollView 就换 .window
        Window("Sync", id: "main") { ContentView() }   // 尺寸与可塑性见 §4
        #if os(macOS)
        Settings { SettingsView() }            // 声明后系统自动提供 App 菜单「设置…」与 ⌘,
        #endif
    }
}

struct StatusMenu: View {
    let model: StatusModel
    @Environment(\.openWindow) private var openWindow
    var body: some View {
        Button("Open Main Window") {
            openWindow(id: "main")
            if #available(macOS 14.0, *) { NSApplication.shared.activate() }
            else { NSApplication.shared.activate(ignoringOtherApps: true) }
        }
        Divider()
        Button("Quit") { NSApplication.shared.terminate(nil) }   // .accessory 无 App 菜单，必须显式给
    }
}
```

## 2. Settings 场景

| 符号 | 可用性 | 说明 |
| --- | --- | --- |
| `Settings`（`init(content:)`） | macOS 11.0+ | 只在 macOS 编译，用 `#if os(macOS)` 包住 |
| `SettingsLink`（`init()` / `init(label:)`） | macOS 14.0+ | 打开设置窗口；已打开则前置 |
| `OpenSettingsAction` / `@Environment(\.openSettings)` | macOS 14.0+ | 编程式打开，可指定 tab |
| `Tab(_:systemImage:)` | macOS 15.0+ | 旧系统写 `TabView { X().tabItem { Label(…) } }` |
| `.scenePadding(_:)` / `.formStyle(.grouped)`（`GroupedFormStyle`） | macOS 12.0+ / macOS 13.0+ | 系统内边距 / 分组行样式 |

- 声明 `Settings { }` 后 **SwiftUI 自动启用 App 菜单 Settings 项与对应快捷键**（⌘, 由系统给，不要在 `Commands` 里再造一个「偏好设置」）。
- 尺寸按 Apple 官方示例：`TabView` + `.scenePadding()` + `.frame(maxWidth: 350, minHeight: 100)`。偏好设置是固定内容窗口，不要套 `defaultSize` / `windowResizability` 的窗口玩法。
- **不要用自定义 Sheet / Window 冒充偏好设置。** 判定：存在 `Settings` scene 之外的另一套「偏好设置」入口，或 App 菜单 Settings 项打不开 ＝ 失败。
- 材质：Settings 是普通窗口，材质由系统给；不要加玻璃容器 / `NSVisualEffectView`，不要为「透明感」加透明标题栏。
- macOS 11–13 无公开的编程式打开 Settings API，**不要用 `showSettingsWindow:` / `showPreferencesWindow:` 这类 selector**（未确证，见 §8）；低版本只依赖 App 菜单入口。

设置视图骨架（Apple 官方示例形状，可直接复制）：`TabView { Tab("General", systemImage: "gear") { … } }.scenePadding().frame(maxWidth: 350, minHeight: 100)`；行分组用 `Form { Toggle("Show Previews", isOn: $showPreview) }.formStyle(.grouped)`，值用 `@AppStorage` 绑定。

## 3. 文稿类应用

### 3.1 版本合同（先读这条）

`FileDocument`、`ReferenceFileDocument`、`DocumentGroup.init(newDocument:editor:)`、`DocumentGroup.init(viewing:viewer:)` **已于 macOS 27.2 起弃用**，弃用说明分别为 `Conform your type to Document instead.` / `Use Document protocol instead.` / `Conform your type to ReadableDocument instead.`。macOS 27.0+ 的新路径：`Document`（= `ReadableDocument & WritableDocument`，`AnyObject`）、`ReadableDocument`、`WritableDocument`、`DocumentGroup.init(allowCreating:editor:makeDocument:)`、`DocumentGroup.init(viewer:makeReadableDocument:)`、`URLDocumentConfiguration`、`DocumentCreationContext`，全部 macOS 27.0+。

判定：target ≥ macOS 27 仍用旧 `FileDocument` 写新代码 ＝ 失败（拾取弃用警告，错过新文稿基础设施的 autosave / undo 约定）。target < 27 时保留旧协议，但把新路径收进独立的 `@available(macOS 27.0, *)` 类型，不要和旧路径混在同一个 guard 里。

### 3.2 SwiftUI 文稿声明

```swift
// macOS 27.0+ 路径。协议成员（reader/writer、snapshot/apply）按 Apple 的 Document
// 协议页给出的形状实现，不要凭记忆写成员名
@available(macOS 27.0, *)
@Observable
final class TextDocument: Document {
    static let readableContentTypes: [UTType] = [.plainText]
    static let writableContentTypes: [UTType] = [.plainText]
    var text: String = ""
}

@main
struct NotesApp: App {
    var body: some Scene {
        DocumentGroup { document in
            TextEditorView(document: document)   // 新建文稿时 configuration.fileURL 为 nil
        } makeDocument: { configuration, context in
            TextDocument()
        }
    }
}
```

只读查看器用 `DocumentGroup(viewer:makeReadableDocument:)`，并按官方要求把 Info.plist 的 `CFBundleTypeRole` 设为 `Viewer`（只读路径下系统不加 File > New、不允许写入）。只读产品用可写初始化器 ＝ 失败。

### 3.3 与 AppKit `NSDocument` 的对应

SwiftUI 的 `DocumentGroup` 在 macOS 上提供文稿类菜单支持（官方原文：`In macOS this includes document-based menu support, including the ability to open multiple documents.`）。AppKit 侧按下表配置，**不要自己实现自动保存与版本管理**。

| 需求 | API | 可用性 |
| --- | --- | --- |
| 就地自动保存 | `NSDocument.autosavesInPlace`（class var `Bool`）：**默认 false，需 override 返回 true** | macOS 10.7+ |
| 草稿自动保存 / 版本管理 | `NSDocument.autosavesDrafts` / `NSDocument.preservesVersions` | macOS 10.8+ / 10.7+ |
| 打开 Versions 浏览器 | `NSDocument.browseVersions(_:)` | macOS 10.8+ |
| 查询 / 关闭浏览器 | `NSDocument.isBrowsingVersions` / `stopBrowsingVersions(completionHandler:)`（另有 async 变体） | macOS 10.12+ |
| 未保存更改计数 / 窗口红点 | `NSDocument.updateChangeCount(_:)` + `NSDocument.ChangeType`；`NSWindow.isDocumentEdited` | 文档未给引入版本 |

`updateChangeCount(_:)` 官方语义（原文摘要）：change count 为 0 表示无未保存更改，> 0 表示已编辑未保存；`ChangeType` 取值 `.changeDone`（increment）/ `.changeUndone`（decrement）/ `.changeCleared` / `.changeReadOtherContents` / `.changeAutosaved` / `.changeRedone` / `.changeDiscardable`。**用 `NSDocument` 默认 undo/redo 时该计数自动维护，只有自己实现 undo 时才手动调用**；既用默认 undo 又手动调用 ＝ 失败（计数漂移，红点与保存提示错位）。

文稿窗口标题与路径：`NSWindow.titleVisibility`（macOS 10.10+，`.visible` / `.hidden`；`.hidden` 官方只描述「隐藏标题并把 toolbar 上移到原标题区」，**不承诺隐藏交通灯**）；`NSWindow.representedURL`（macOS 10.5+）、`NSWindow.setTitleWithRepresentedFilename(_:)` 让标题栏显示文件名并保留系统路径下探入口。SwiftUI 侧从 editor 闭包的 configuration 读 `fileURL`（新建文稿为 nil）；官方明确警告**不要用该 URL 自己读写文稿内容或元数据**，读写走协议方法。

## 4. 窗口与场景管理

| 需求 | API | 可用性 |
| --- | --- | --- |
| 可复制窗口组 / 唯一窗口 | `WindowGroup` / `Window("标题", id:)` | macOS 11.0+ / macOS 13.0+ |
| 按值 / 按 id 开窗 | `WindowGroup(for:)` + `@Environment(\.openWindow)` | macOS 13.0+ |
| 关窗 | `@Environment(\.dismissWindow)`（`callAsFunction(id:)` / `(value:)` / `(id:value:)`） | macOS 14.0+ |
| 默认尺寸 / 位置 | `Scene.defaultSize(width:height:)`、`defaultSize(_:)`、`Scene.defaultPosition(_:)` | macOS 13.0+（`defaultPosition` 仅 macOS） |
| 尺寸可塑性 / 窗口样式 | `Scene.windowResizability(_:)`：`.automatic` / `.contentMinSize` / `.contentSize`；`Scene.windowStyle(_:)` + `.hiddenTitleBar`（`HiddenTitleBarWindowStyle`） | macOS 13.0+ / macOS 11.0+ |
| 外部事件归属 / 按 Scene 持久化 UI 状态 | `Scene.handlesExternalEvents(matching:)`（`Set<String>`）/ `@SceneStorage` | macOS 11.0+ |
| Scene 还原开关 | `Scene.restorationBehavior(_:)`：`.automatic` / `.disabled` | macOS 15.0+ |

- `WindowGroup(for:)`：**传同一个值时系统前置已有窗口而不是新开**（官方原文）。不要自建「某 id 是否已打开」的注册表；新建入口要处理 nil（给 `defaultValue:` 或显式分支）。
- `.hiddenTitleBar` 只承诺隐藏标题与标题栏背景，**交通灯是否隐藏属未确证**（见 §8）。要在代码里操作交通灯用 `NSWindow.standardWindowButton(_:)`（文档未给引入版本），不要猜 API 名。AppKit 等价做法是 `NSWindow.titlebarAppearsTransparent`（macOS 10.10+）+ `NSWindow.StyleMask.fullSizeContentView`（macOS 10.10+）。
- `@SceneStorage` 官方三个硬约束：**每 Scene 独立、不共享**；**不保证持久化时机与频率**；**Scene 被显式销毁（macOS 上窗口关闭）时数据一并销毁**。因此只放轻量 UI 状态（selection、tab、scroll position），不放文稿模型、图片或敏感数据。
- 还原链路：SwiftUI 交给 `restorationBehavior(.automatic)`（官方原文：`On macOS, this behavior is governed by a system setting which can be toggled on and off by the user.`）；AppKit 用 `NSWindow.isRestorable`（macOS 10.7+）、`NSWindow.restorationClass`（macOS 10.7+）、`NSWindowRestoration` 协议、`NSApplication.restoreWindow(withIdentifier:state:completionHandler:)`（macOS 10.7+）、`applicationSupportsSecureRestorableState(_:)`（macOS 12.0+）。自己写 UserDefaults + frame 存档 ＝ 失败（与系统还原打架，且不响应用户关闭还原的设置）。

```swift
struct WorkspaceWindow: View {
    @SceneStorage("sidebarSelection") private var selection: String?   // 每 Scene 独立，窗口关闭即销毁
    @Environment(\.openWindow) private var openWindow
    @Environment(\.dismissWindow) private var dismissWindow
    var body: some View {
        NavigationSplitView { Sidebar(selection: $selection) } detail: { Detail() }
            .toolbar {
                Button("New Inspector") { openWindow(id: "inspector", value: UUID()) }
                Button("Close Inspector") { dismissWindow(id: "inspector") }
            }
    }
}

@main
struct WorkspaceApp: App {
    var body: some Scene {
        WindowGroup("Workspace", id: "workspace") { WorkspaceWindow() }
            .defaultSize(width: 1100, height: 720)
            .defaultPosition(.topLeading)
            .windowResizability(.contentMinSize)   // 不要用 .contentSize 锁死窗口
        WindowGroup("Inspector", id: "inspector", for: UUID.self) { $id in
            InspectorView(id: id)
        }
    }
}
```

## 5. Stage Manager 与多显示器

| 需求 | API | 可用性 |
| --- | --- | --- |
| 主 / 辅助窗口（Stage Manager 与全屏共用） | `NSWindow.CollectionBehavior.primary` / `.auxiliary` | macOS 13.0+ |
| 经典全屏参与 | `.fullScreenPrimary` / `.fullScreenAuxiliary` / `.fullScreenNone` | macOS 10.7+ |
| Spaces / Mission Control / 全屏 | `.managed` / `.canJoinAllSpaces` / `.moveToActiveSpace` / `.stationary`；`NSWindow.toggleFullScreen(_:)` | macOS 10.6+ / macOS 10.7+ |
| 屏幕列表 / 可见区域 / 参数变化 / 跨屏 | `NSScreen.screens` / `NSScreen.visibleFrame` / `NSApplication.didChangeScreenParametersNotification` / `NSWindow.didChangeScreenNotification` | 文档未给引入版本 |
| 缩放因子与变化回调 | `NSScreen.backingScaleFactor`、`NSWindow.backingScaleFactor`、`NSView.viewDidChangeBackingProperties()`、`NSWindow.didChangeBackingPropertiesNotification` | macOS 10.7+ |

- **不假设固定屏幕**：启动时缓存 `NSScreen.screens` 或写死分辨率 ＝ 失败。默认位置用 `defaultPosition` 或按 `NSScreen.main?.visibleFrame` 计算，不用绝对坐标。
- 监听 `didChangeScreenParametersNotification`（插拔显示器、Stage Manager 改变可见区域）后重新计算布局约束，不要重建窗口。
- 跨屏拖动或拖到不同 `backingScaleFactor` 的屏幕时，自绘层必须响应 `viewDidChangeBackingProperties()` / `didChangeBackingPropertiesNotification` 重绘（位图尺寸、`CALayer.contentsScale`）；系统 AppKit 控件自动处理，自绘 `NSView.draw(_:)` 与自定义 layer 不处理就是模糊 ＝ 失败。
- 全屏与 Stage Manager：用 `.primary`（macOS 13.0+）声明主窗口，浮在它之上的工具面板用 `.auxiliary` + `.fullScreenAuxiliary`。全屏入口一律走 `NSWindow.toggleFullScreen(_:)` 或系统绿色按钮，不要改 `styleMask` 模拟全屏。
- 材质：切屏、进出全屏、Stage Manager 层叠变化时的材质 active/inactive 由系统决定；不要用固定高亮让后台或副窗口看起来仍是主操作状态。

## 6. Dock 集成

| 需求 | API | 可用性 |
| --- | --- | --- |
| Dock 磁贴 / Badge / 重绘 / 角标开关 / 自定义绘制 | `NSApplication.dockTile` → `NSDockTile`；`NSDockTile.badgeLabel`（`String?`）、`NSDockTile.display()`、`NSDockTile.showsApplicationBadge`（官方注明 10.5 起 App 磁贴不支持 application badge，与属性名矛盾，见 §8）、`NSDockTile.contentView` | macOS 10.5+ |
| 最近文稿 / Dock 菜单 | `NSDocumentController.recentDocumentURLs` / `noteNewRecentDocumentURL(_:)` / `noteNewRecentDocument(_:)` / `clearRecentDocuments(_:)` / `maximumRecentDocumentCount`（`0` 表示不加 Open Recent 菜单）；`NSApplicationDelegate.applicationDockMenu(_ sender: NSApplication) -> NSMenu?` | 文档未给引入版本 |

- Badge 用 `badgeLabel` 字符串，**不要**自绘图片伪造角标；改完断言磁贴已更新。
- 最近文稿走 `NSDocumentController`；SwiftUI `DocumentGroup` 已提供文稿类菜单支持，**不要手写第二套 Open Recent**。只有非文稿 App 才用 `noteNewRecentDocumentURL(_:)`，并让 File 菜单与文件列表同源。
- Dock 菜单只放与当前窗口选择无关的全局动作（New Window、Recents、Quit）；与 key window selection 相关的动作放菜单栏或 context menu。
- **不要伪造 Dock 视觉**：不用 `NSDockTile.contentView` 画假 app 图标或假 badge，也不覆盖图标本身。Dock 图标与角标是系统资产。

## 7. Quick Look

| 需求 | API | 可用性 |
| --- | --- | --- |
| AppKit 预览面板 | `QLPreviewPanel`；`shared()`（不存在则创建）/ `sharedPreviewPanelExists()`；`dataSource`（`QLPreviewPanelDataSource`）、`delegate`（`QLPreviewPanelDelegate`）、`currentPreviewItem`、`currentPreviewItemIndex`、`refreshCurrentPreviewItem()` | macOS 10.6+ |
| 控制权接管 | 走 responder chain 的 `acceptsPreviewPanelControl(_:)` / `beginPreviewPanelControl(_:)` / `endPreviewPanelControl(_:)`（方法名出自 QLPreviewPanel 官方正文） | 文档未给引入版本 |
| SwiftUI 单个 URL / 集合内选择 | `quickLookPreview(_ item: Binding<URL?>)` / `quickLookPreview(_ selection:in items:)` | macOS 11.0+ |

- 文档、图片、媒体、附件预览**优先用系统 Quick Look**：它提供系统外观、Share、Markup 与全屏，面板材质由系统维护——这是 Mac 上「空格预览」的正式接入点。
- SwiftUI：`quickLookPreview(_:)` 由 binding 驱动，设为非 nil 时展示，用户关闭时系统把 binding 置回 nil。展示状态只有 binding 一个来源；再造一份 `@State` 副本 ＝ 失败。
- AppKit：控制权必须先经 responder chain（`acceptsPreviewPanelControl(_:)` 返回 true 才拿到 `beginPreviewPanelControl(_:)`）。直接 `QLPreviewPanel.shared()` 后绕过控制权流程设置 dataSource ＝ 失败。
- **取舍**：只有预览需要「限制在应用窗口内、与自定义检查器/画布联动的浮层」时才自建面板，且不得命名为 Quick Look、不得复制其外观（Share / Markup / 全屏不会跟着来）。仅为「比系统好看」自建 ＝ 失败，改用 `quickLookPreview(_:)`。
- 空格键触发：SwiftUI `quickLookPreview` 文档未定义空格键绑定，**属未确证**（见 §8）。需要精确空格语义时自己在 `NSResponder` / `keyDown` 或 Commands 层实现，并保证与菜单里的「快速查看」命令同源。

## 8. 未确证 / 需在 SDK 核实

1. **`NSQuitAlwaysKeepsWindows`（用户默认键）**：Apple 现行文档站点无该键的符号页或说明页；`SceneRestorationBehavior.automatic` 的官方说明确认 macOS 上由系统设置控制开关。**键名按未确证处理**，不要写进代码逻辑。核实：测试机 `defaults read -g NSQuitAlwaysKeepsWindows`，对比 System Settings 切换前后。
2. **`NSWindow.titleVisibility = .hidden` 与 `.hiddenTitleBar` 下的交通灯可见性**：官方只描述隐藏标题 / 标题栏背景。核实：最小 target 各跑一次，用 `NSWindow.standardWindowButton(_:)` 检查按钮存在性并截图核对。
3. **macOS 11–13 编程式打开 Settings**：`SettingsLink` / `OpenSettingsAction` 均为 macOS 14.0+，更早无公开 API；`showSettingsWindow:` / `showPreferencesWindow:` 属私有 selector，不要使用。核实：在 macOS 13 SDK 用 `swift-symbolgraph-extract -module-name SwiftUI` 检索 `Settings` 相关符号。
4. **`QLPreviewPanelController` 协议名与 `quickLookPreview` 的空格键绑定**：QLPreviewPanel 正文引用的 controller protocol 在当前站点解析不到独立页面（404），三个方法名出自该正文而**协议类型名未确证**；`quickLookPreview` 只定义 binding 驱动的展示，空格键语义未定义。核实：SDK 的 `QuickLookUI.h` 检索 `QLPreviewPanelController`，并在示例 App 中按空格实测。
5. **`NSDocument.hasUnautosavedChanges`**：符号出现在 NSDocument 的「Autosaving the Document」分组索引，但符号页 404，路径与签名未确证。核实：Xcode ⌥-click `NSDocument` 成员列表。
6. **`NSDockTile.showsApplicationBadge` 与一批「文档未给引入版本」符号**（`NSWindowRestoration`、`NSScreen.screens`、`didChangeScreenParametersNotification`、`applicationDockMenu(_:)`、`NSDocumentController` 最近文稿系列、`NSApplication.ActivationPolicy`、`NSWindow.standardWindowButton(_:)`）：文档元数据无 macOS `introducedAt`（`showsApplicationBadge` 另有与属性名矛盾的说明）。核实：Xcode 头文件中的 `API_AVAILABLE` 标注；`badgeLabel` 在目标系统上实测。

## 9. 来源

本次核对的 Apple 官方文档（`developer.apple.com/tutorials/data/documentation/…json` 元数据 + 符号页正文）：

- 菜单栏：`MenuBarExtra` https://developer.apple.com/documentation/swiftui/menubarextra ；`MenuBarExtraStyle` https://developer.apple.com/documentation/swiftui/menubarextrastyle ；`Scene.menuBarExtraStyle(_:)` https://developer.apple.com/documentation/swiftui/scene/menubarextrastyle(_:) ；`LSUIElement` https://developer.apple.com/documentation/bundleresources/information-property-list/lsuielement ；`setActivationPolicy(_:)` https://developer.apple.com/documentation/appkit/nsapplication/setactivationpolicy(_:) ；`ActivationPolicy.accessory` https://developer.apple.com/documentation/appkit/nsapplication/activationpolicy-swift.enum/accessory ；`activate()` https://developer.apple.com/documentation/appkit/nsapplication/activate() ；`activate(ignoringOtherApps:)` https://developer.apple.com/documentation/appkit/nsapplication/activate(ignoringotherapps:) ；`@Observable` https://developer.apple.com/documentation/observation/observable()
- Settings：`Settings` https://developer.apple.com/documentation/swiftui/settings ；`SettingsLink` https://developer.apple.com/documentation/swiftui/settingslink ；`OpenSettingsAction` / `openSettings` https://developer.apple.com/documentation/swiftui/opensettingsaction ；`Tab` https://developer.apple.com/documentation/swiftui/tab ；`formStyle(_:)` https://developer.apple.com/documentation/swiftui/view/formstyle(_:) ；`scenePadding(_:)` https://developer.apple.com/documentation/swiftui/view/scenepadding(_:)
- 文稿：`DocumentGroup` https://developer.apple.com/documentation/swiftui/documentgroup ；`init(allowCreating:editor:makeDocument:)` https://developer.apple.com/documentation/swiftui/documentgroup/init(allowcreating:editor:makedocument:) ；`init(viewer:makeReadableDocument:)` https://developer.apple.com/documentation/swiftui/documentgroup/init(viewer:makereadabledocument:) ；`Document` https://developer.apple.com/documentation/swiftui/document ；`ReadableDocument` https://developer.apple.com/documentation/swiftui/readabledocument ；`WritableDocument` https://developer.apple.com/documentation/swiftui/writabledocument ；`FileDocument`（27.2 起弃用）https://developer.apple.com/documentation/swiftui/filedocument ；`ReferenceFileDocument`（27.2 起弃用）https://developer.apple.com/documentation/swiftui/referencefiledocument ；`URLDocumentConfiguration` https://developer.apple.com/documentation/swiftui/urldocumentconfiguration
- `NSDocument`：`autosavesInPlace` https://developer.apple.com/documentation/appkit/nsdocument/autosavesinplace ；`autosavesDrafts` https://developer.apple.com/documentation/appkit/nsdocument/autosavesdrafts ；`preservesVersions` https://developer.apple.com/documentation/appkit/nsdocument/preservesversions ；`browseVersions(_:)` https://developer.apple.com/documentation/appkit/nsdocument/browseversions(_:) ；`stopBrowsingVersions(completionHandler:)` https://developer.apple.com/documentation/appkit/nsdocument/stopbrowsingversions(completionhandler:) ；`updateChangeCount(_:)` https://developer.apple.com/documentation/appkit/nsdocument/updatechangecount(_:) ；`ChangeType` https://developer.apple.com/documentation/appkit/nsdocument/changetype
- 文稿窗口标题：`titleVisibility` https://developer.apple.com/documentation/appkit/nswindow/titlevisibility-swift.property ；`representedURL` https://developer.apple.com/documentation/appkit/nswindow/representedurl ；`setTitleWithRepresentedFilename(_:)` https://developer.apple.com/documentation/appkit/nswindow/settitlewithrepresentedfilename(_:) ；`isDocumentEdited` https://developer.apple.com/documentation/appkit/nswindow/isdocumentedited
- 窗口与还原：`WindowGroup` https://developer.apple.com/documentation/swiftui/windowgroup ；`Window` https://developer.apple.com/documentation/swiftui/window ；`openWindow` https://developer.apple.com/documentation/swiftui/environmentvalues/openwindow ；`dismissWindow` https://developer.apple.com/documentation/swiftui/environmentvalues/dismisswindow ；`defaultSize(width:height:)` https://developer.apple.com/documentation/swiftui/scene/defaultsize(width:height:) ；`defaultPosition(_:)` https://developer.apple.com/documentation/swiftui/scene/defaultposition(_:) ；`windowResizability(_:)` https://developer.apple.com/documentation/swiftui/scene/windowresizability(_:) ；`windowStyle(_:)` https://developer.apple.com/documentation/swiftui/scene/windowstyle(_:) ；`HiddenTitleBarWindowStyle` https://developer.apple.com/documentation/swiftui/hiddentitlebarwindowstyle ；`handlesExternalEvents(matching:)` https://developer.apple.com/documentation/swiftui/scene/handlesexternalevents(matching:) ；`SceneStorage` https://developer.apple.com/documentation/swiftui/scenestorage ；`restorationBehavior(_:)` https://developer.apple.com/documentation/swiftui/scene/restorationbehavior(_:) ；`SceneRestorationBehavior.automatic` https://developer.apple.com/documentation/swiftui/scenerestorationbehavior/automatic ；`NSWindow.isRestorable` https://developer.apple.com/documentation/appkit/nswindow/isrestorable ；`restorationClass` https://developer.apple.com/documentation/appkit/nswindow/restorationclass ；`NSWindowRestoration` https://developer.apple.com/documentation/appkit/nswindowrestoration ；`restoreWindow(withIdentifier:state:completionHandler:)` https://developer.apple.com/documentation/appkit/nsapplication/restorewindow(withidentifier:state:completionhandler:) ；`applicationSupportsSecureRestorableState(_:)` https://developer.apple.com/documentation/appkit/nsapplicationdelegate/applicationsupportssecurerestorablestate(_:) ；`standardWindowButton(_:)` https://developer.apple.com/documentation/appkit/nswindow/standardwindowbutton(_:) ；`titlebarAppearsTransparent` https://developer.apple.com/documentation/appkit/nswindow/titlebarappearstransparent
- Stage Manager / 多显示器：`NSWindow.CollectionBehavior` https://developer.apple.com/documentation/appkit/nswindow/collectionbehavior-swift.struct ；`.primary` https://developer.apple.com/documentation/appkit/nswindow/collectionbehavior-swift.struct/primary ；`toggleFullScreen(_:)` https://developer.apple.com/documentation/appkit/nswindow/togglefullscreen(_:) ；`NSScreen.screens` https://developer.apple.com/documentation/appkit/nsscreen/screens ；`NSScreen.backingScaleFactor` https://developer.apple.com/documentation/appkit/nsscreen/backingscalefactor ；`didChangeScreenParametersNotification` https://developer.apple.com/documentation/appkit/nsapplication/didchangescreenparametersnotification ；`viewDidChangeBackingProperties()` https://developer.apple.com/documentation/appkit/nsview/viewdidchangebackingproperties() ；`didChangeBackingPropertiesNotification` https://developer.apple.com/documentation/appkit/nswindow/didchangebackingpropertiesnotification
- Dock / Quick Look：`NSApplication.dockTile` https://developer.apple.com/documentation/appkit/nsapplication/docktile ；`NSDockTile` https://developer.apple.com/documentation/appkit/nsdocktile ；`badgeLabel` https://developer.apple.com/documentation/appkit/nsdocktile/badgelabel ；`display()` https://developer.apple.com/documentation/appkit/nsdocktile/display() ；`applicationDockMenu(_:)` https://developer.apple.com/documentation/appkit/nsapplicationdelegate/applicationdockmenu(_:) ；`recentDocumentURLs` https://developer.apple.com/documentation/appkit/nsdocumentcontroller/recentdocumenturls ；`noteNewRecentDocumentURL(_:)` https://developer.apple.com/documentation/appkit/nsdocumentcontroller/notenewrecentdocumenturl(_:) ；`QLPreviewPanel` https://developer.apple.com/documentation/quicklookui/qlpreviewpanel ；`shared()` https://developer.apple.com/documentation/quicklookui/qlpreviewpanel/shared() ；`quickLookPreview(_:)` https://developer.apple.com/documentation/swiftui/view/quicklookpreview(_:) ；`quickLookPreview(_:in:)` https://developer.apple.com/documentation/swiftui/view/quicklookpreview(_:in:)
