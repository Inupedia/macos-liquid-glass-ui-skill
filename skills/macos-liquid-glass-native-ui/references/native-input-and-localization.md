# 原生输入、文本系统与本地化

> 适用范围：原生 macOS SwiftUI / AppKit 应用中的**拖放与剪贴板、文本编辑、输入法（IME）与键盘、本地化、书写方向（RTL）、可访问性输入路径**，以及只与这些主题相关的启动/响应性能。窗口、材质、Toolbar/Sidebar、`glassEffect` 规则见 `swiftui-appkit.md`；验收记录格式见 `validation.md`。
本文件是「原生 vs Web」判别面最集中的地方：拖放语义、IME 标记文本（composed / marked text）、String Catalog 复数与方向镜像在 Web 里没有等价物，凭常识实现必然出错。每条规则都要能判定「什么情况用哪个 API」「什么情况算失败」。
版本口径：符号与可用性取自 Apple 官方文档元数据（2026-09-30 核对）。API 后的版本号即最低引入版本；无版本号表示该符号页未列出 macOS 引入版本（长期存在的 AppKit 符号），**不代表 macOS 26 专属**。写入代码前仍需在目标 SDK 中 ⌥-click 复核。

## 1. 拖放与剪贴板

### 1.1 选型判定
| 场景 | 用什么 | 判定 |
| --- | --- | --- |
| SwiftUI 视图拖出一个模型对象 | `.draggable(_:)`（macOS 13.0+） | payload 类型需 conform `Transferable` |
| SwiftUI 视图接收模型对象 | `.dropDestination(for:action:isTargeted:)`（macOS 13.0+） | 该重载**在 macOS 27.2 被弃用**，替代为 `dropDestination(for:isEnabled:action:)`（macOS 26.0+，action 收 `DropSession`） |
| 需要判断 `isTargeted` 做落点高亮 | 上述两者的 `isTargeted` 闭包 | 见 §1.3 可访问性要求 |
| 与**任意外部 App** 交换文件/富文本 | `.onDrag`（macOS 10.15+）/ `.onDrop(of:isTargeted:perform:)`（macOS 11.0+），走 `NSItemProvider` | 未被弃用；只在 `Transferable` 表达不了的场景用 |
| `.onDrop(of:delegate:)`（macOS 10.15+，收 `[String]`） | **不要新写** | 文档已标弃用（`deprecationSummary: "Use  instead."`，替代符号未渲染） |
| AppKit 自定义 `NSView` 作拖源/落点 | `NSDraggingSource` / `NSDraggingDestination` + `registerForDraggedTypes(_:)` | 见 §1.2 |
| 写系统剪贴板 | `NSPasteboard` | 顺序约束见 §1.2 |
`Transferable`（macOS 13.0+）的表示按**优先级从高到低**排列。Apple 原文：
> The order of the representations in the transfer representation matters; place the representation that most accurately represents your type first, followed by a sequence of more compatible but less preferable representations.
`ProxyRepresentation`（macOS 13.0+）让接收方退到通用格式（如纯文本）。Apple 明确警告：
> `ProxyRepresentation` is a convenience, and its evaluation isn't supposed to be calculation-heavy. Don't perform long-running work in `exporting` and `importing` closures. They shouldn't contain network requests, file operations, or other potentially time-consuming tasks.
`FileRepresentation`（macOS 13.0+）走 `SentTransferredFile` / `ReceivedTransferredFile`，适合大文件；`DataRepresentation`、`CodableRepresentation` 同为 macOS 13.0+。`UTType` 为 macOS 11.0+；自有类型用 `UTType(exportedAs:)` 并在 Info.plist 登记。`.draggable(_:)` 硬约束（原文）：`Don't perform work on the main actor while exporting the item. Doing so isn't supported and might cause a hang.`

### 1.2 可复制代码：Transferable 拖放（含 SwiftUI + AppKit 剪贴板）

```swift
import SwiftUI
import UniformTypeIdentifiers
struct Landmark: Transferable, Codable {
    var title: String
    var note: String
    static var transferRepresentation: some TransferRepresentation {
        CodableRepresentation(contentType: .landmark)   // 高保真：自有类型优先
        ProxyRepresentation(\.title)                     // 退让：不认识 .landmark 时给纯文本
    }
}
extension UTType {
    static let landmark = UTType(exportedAs: "com.example.landmark")   // Info.plist 需登记
}
struct LandmarkRow: View {
    let landmark: Landmark
    @State private var isTargeted = false
    var body: some View {
        Text(landmark.title)
            .padding(8)
            .draggable(landmark)                                  // macOS 13.0+
            .dropDestination(for: Landmark.self) { items, _ in   // macOS 13.0+（27.2 起弃用）
                !items.isEmpty                                  // false = 让系统给出失败反馈
            } isTargeted: { isTargeted = $0 }
            .overlay {   // 落点反馈不能只靠颜色
                if isTargeted {
                    RoundedRectangle(cornerRadius: 6).strokeBorder(.tint, lineWidth: 2)
                }
            }
            .accessibilityLabel(isTargeted ? "落点：\(landmark.title)" : landmark.title)
    }
}
// AppKit 写剪贴板：clearContents() 必须先于 setString(_:forType:)
func copyToPasteboard(_ text: String) {
    let pb = NSPasteboard.general
    pb.clearContents()                        // 官方：往剪贴板放数据的第一步
    pb.setString(text, forType: .string)      // 返回 Bool，必须检查
}
```
AppKit 落点（`NSView` 本身 conform `NSDraggingDestination`）：
```swift
final class DropWell: NSView {
    override init(frame frameRect: NSRect) {
        super.init(frame: frameRect)
        registerForDraggedTypes([.fileURL, .string])   // 不注册则收不到任何拖放回调
    }
    required init?(coder: NSCoder) { fatalError() }
    override func draggingEntered(_ sender: any NSDraggingInfo) -> NSDragOperation {
        sender.draggingPasteboard.canReadObject(forClasses: [NSURL.self]) ? .copy : []
    }
    override func performDragOperation(_ sender: any NSDraggingInfo) -> Bool {
        !(sender.draggingPasteboard.readObjects(forClasses: [NSURL.self]) as? [URL] ?? []).isEmpty
    }
}
```
`NSPasteboard.PasteboardType` 是 `struct`：`.string`（10.6+）、`.fileURL`（10.13+）。惰性/多类型数据用 `NSPasteboardItem.setDataProvider(_:forTypes:)`（10.6+）。

### 1.3 落点高亮必须多重编码

**失败判定：拖放目标高亮只改变背景色/透明度。** 必须同时给出非颜色信号：边框（`strokeBorder`）、`circle.slash` 之类禁止图标、或文字状态（"释放以导入"）。HIG — Drag and drop 要求展示可否接收、给出无效落点反馈，并**提供拖放的替代路径**（菜单命令），因为拖放对部分用户不可行（macOS 上可用键盘或 VoiceOver 完成拖放）。键盘路径见 §6。

## 2. 文本编辑

### 2.1 选型判定（从轻到重）
| 需求 | 用什么 | 可用性 / 边界 |
| --- | --- | --- |
| 单行/多行纯文本输入 | `TextField(_:text:axis:)`，`axis: .vertical` | macOS 13.0+；配合 `.lineLimit(_:reservesSpace:)`（macOS 13.0+）固定高度 |
| 多行纯文本编辑 | `TextEditor(text:)` | macOS 11.0+；入参是 `Binding<String>`，**无富文本能力** |
| 去掉编辑区自带背景 | `.scrollContentBackground(.hidden)` | macOS 13.0+ |
| 去掉编辑区边框/样式 | `.textEditorStyle(.plain)` | macOS 14.0+（`TextEditorStyle` 与 `.automatic` 同为 macOS 14.0+） |
| 富文本、自定义属性、精确排版 | `NSTextView` + TextKit 2 | `NSTextLayoutManager` / `NSTextContentStorage` 均 macOS 12.0+ |
| 代码编辑器（高亮、折叠、多光标） | TextKit 2 或成熟第三方 | 见 §2.2 |
**失败判定：为了语法高亮/富文本去改 `TextEditor` 的 `String` 再做正则拼装。** 这条路必然丢失 IME 组合态与选区语义；应换 `NSTextView` 或第三方。

### 2.2 TextKit 2 的适用边界

`NSTextView` 用 `convenience init(usingTextLayoutManager: Bool)` 显式选择 TextKit 2；`textLayoutManager`、`textContentStorage` 均 macOS 12.0+。规则：
- **能留在 TextKit 1 就留下**：`NSTextView(frame:textContainer:)` 与 `NSTextContainer`（macOS 10.0+）是稳定面；TextKit 2 的 layout 与自定义 drawing 在边界场景仍需实测。
- 需要**视口化布局**（超长文档只布局可见区）才上 TextKit 2：`NSTextViewportLayoutController`（macOS 12.0+）。
- 需要自绘字形/自定义断行/复杂附件时，先确认 TextKit 2 能表达；不能则显式留在 TextKit 1，**不要混用两套 layout manager**。
- 代码编辑器需求（增量高亮、括号匹配、多光标）没有系统级现成解：用 TextKit 2 自建或采用第三方，**不要**用 `TextEditor` + overlay 伪造。

### 2.3 滚动归属

**失败判定：编辑区（内部滚动）与窗口/父级（外部滚动）同时响应同一滚动手势。** 规则：编辑区自身可滚动时，`TextEditor` / `NSTextView` 必须吃掉滚轮事件，父级 `ScrollView` 不要包住自带滚动的编辑器；需要"内容随窗口长高"时用 `TextField(axis: .vertical)` + `lineLimit` 或让 `NSTextView` 高度跟随内容，滚动交给外层单一容器；拖放自动滚动只由**当前落点容器**实现，不要内外两层都滚。

## 3. 输入法（IME）与键盘

### 3.1 marked text 不能被打断

中文/日文输入法的候选态是 **marked text**。`NSTextInputClient` 的 topic section 即 "Handling marked text"，成员：`hasMarkedText()`、`markedRange()`、`selectedRange()`、`setMarkedText(_:selectedRange:replacementRange:)`、`unmarkText()`、`validAttributesForMarkedText()`；必需方法还有 `insertText(_:replacementRange:)`、`doCommand(by:)`、`firstRect(forCharacterRange:actualRange:)`、`attributedSubstring(forProposedRange:actualRange:)`。该协议无 macOS 引入版本标注（长期存在）。
**失败判定（组合态期间任一条成立即失败）**：① 文本被 trim / normalize / 大小写转换；② 每次键入假名就触发校验、搜索、自动保存或 UI 重排；③ `onChange` 里整体替换内容（等价于丢弃 marked range）；④ 候选窗位置漂移（`firstRect(forCharacterRange:actualRange:)` 返回错误矩形）。正确做法：**只在 `insertText(_:replacementRange:)` / `unmarkText()` 之后才跑业务逻辑。**

### 3.2 AppKit 键盘路径

`NSResponder.keyDown(with:)`（无版本标注）中必须先调 `interpretKeyEvents(_:)` 把事件交给文本输入系统，再处理自定义逻辑：
```swift
override func keyDown(with event: NSEvent) {
    // 官方路径：先让输入法消费（组合、候选、deleteBackward: 等）
    interpretKeyEvents([event])
    // 到这里仍未处理的动作，才是应用级快捷键
}
override func doCommand(by selector: Selector) {
    switch selector {
    case #selector(NSResponder.insertNewline(_:)): submit()
    default: super.doCommand(by: selector)          // 必须回落到 super
    }
}
```
`NSEvent` 侧判定：`characters`、`charactersIgnoringModifiers`、`modifierFlags`、`isARepeat` 均为长期存在的属性（`modifierFlags` 路径含 Swift 属性后缀，见来源）。
**失败判定：在 `keyDown` 里按 `charactersIgnoringModifiers` 或裸键码匹配无修饰键（字母、空格、Return）来当快捷键。** 中文/日文输入态下这些键属于输入法，抢占它等于毁掉输入。快捷键一律优先 `⌘`/`⌃`/`⌥` 组合。

### 3.3 SwiftUI 侧
命令与快捷键用 `Commands`（macOS 11.0+）、`.keyboardShortcut(_:)`（macOS 11.0+）、`KeyboardShortcut`（macOS 11.0+）；要读回当前生效快捷键（菜单/提示保持一致）用 `@Environment(\.keyboardShortcut)`（macOS 12.0+，`KeyboardShortcut?`）；焦点用 `@FocusState`（macOS 12.0+，`projectedValue: FocusState<Value>.Binding`）与 `.focusable(_:)`（macOS 12.0+）。
**失败判定**：① 自绘 glass 输入控件用 `@FocusState` 记录"我聚焦了"，却没有把第一响应者交给真实文本系统——结果是输入法候选窗不出现、`hasMarkedText()` 永远为 false；自绘文本 UI 必须让宿主 `NSView` 成为 first responder 并由系统 `NSTextInputContext`（macOS 10.6+）驱动。② 输入法切换（拼音↔英文）导致布局重排或内容跳动——语言/输入源切换不是内容变更事件，不得触发 `body` 结构性重建。

## 4. 本地化

### 4.1 String Catalog 是默认路径

Xcode 15 起 `Localizable.xcstrings`（String Catalog）是首选，Apple 原文：
> In Xcode 15 and later, string catalogs are the recommended way to localize strings that contain plurals. In earlier versions of Xcode, use strings and `stringsdict` files.
加一个 catalog 文件后 `Product > Build`，Xcode 自动抽取可本地化字符串（多数 SwiftUI 视图内字符串自动可本地化）。**复数**：对含变量的 key 选 **Vary by Plural**，Xcode 补齐该语言全部复数形式并**自动决定 specifier**（64 位整数为 `%lld`）；**手写 `if count == 1 { ... } else { ... }` 即失败**——复数类别不止 two-form（Apple 例子中俄语为 One/Few/Many/Other）。空间不足用 **Vary by Device** 做设备变体，而不是在代码里判断机型拼字符串。API：`String(localized:table:bundle:locale:comment:)`（macOS 12.0+，`keyAndValue: String.LocalizationValue`）、`NSLocalizedString(_:tableName:bundle:value:comment:)`（macOS 10.10+）、SwiftUI `Text(_:tableName:bundle:comment:)`（macOS 10.15+，走 `LocalizedStringKey`）。

### 4.2 格式化一律用 FormatStyle

**失败判定：手写日期/数字/单位拼接（`"\(year)年\(month)月"`、"$" + price、`"\(n) MB"`）。** 一律用 `FormatStyle`（以下均 macOS 12.0+）：`Int.formatted()` / `.formatted(.number)`（`FormatStyle.number`）；`.formatted(.percent)` / `.formatted(.currency(code:))`（`IntegerFormatStyle.Percent` / `.Currency`）；`Date.formatted(date:time:)`；`Measurement.formatted(_:)` + `Measurement.FormatStyle.init(width:locale:usage:numberFormatStyle:)`（locale 默认 `.autoupdatingCurrent`）。`Locale.current` / `Locale.autoupdatingCurrent` 为 macOS 10.10+，SwiftUI 用 `@Environment(\.locale)`（macOS 10.15+）；**`Locale.current` 会缓存，跨区域变更要看 `autoupdatingCurrent` 或环境值。**

### 4.3 可复制代码：String Catalog 复数用法

```swift
// 1) SwiftUI 文本：插值 + 变体交给 String Catalog（对该 key 选 "Vary by Plural"）
Text("\(fileCount) 个文件")                                // 不要写 if fileCount == 1
Text("Last updated \(lastUpdated, format: .dateTime)")    // 让系统决定日期格式
// 2) 非视图上下文：String(localized:)（macOS 12.0+）；变量拼进 key，不要在外面拼
let status = String(localized: "\(done) of \(total) tasks complete", table: "Progress",
                    comment: "Status line under the task list; two integers.")
// 3) 数字/度量：FormatStyle 而不是字符串拼接
let sizeText = Measurement(value: Double(size), unit: UnitInformationStorage.bytes)
    .formatted(.measurement(width: .abbreviated, usage: .asProvided))
let percentText = Double(ratio).formatted(.percent.precision(.fractionLength(0)))
```

### 4.4 伪本地化与超长文案

Apple 官方在 Interface Builder 预览与 scheme 语言选择处提供 pseudolanguage；**精确的伪语言名称列表本文件未从 Apple 文档确证**（见 §9）。可用的确证路径：Xcode 的 `Product > Scheme > Edit Scheme > Run > Options` 里选 **App Language / App Region**，或用 SwiftUI Preview 直接注入环境：
```swift
#Preview("de") { ContentView().environment(\.locale, .init(identifier: "de")) }
#Preview("ar (RTL)") {
    ContentView().environment(\.locale, .init(identifier: "ar")).environment(\.layoutDirection, .rightToLeft)
}
```
**失败判定（超长德语文案）**：按钮文字被截断成 `…`、关键动词消失、或为了塞进去而把 label 改短。正确做法：让按钮随内容变宽、允许换行或使用图标+tooltip，**绝不隐藏含义**。这条必须用德语（而不是英语加长空格）实测。

## 5. RTL 与书写方向

读方向用 `@Environment(\.layoutDirection)`（`LayoutDirection`，macOS 10.15+）；AppKit 用 `NSView.userInterfaceLayoutDirection`（macOS 10.8+，类型 `NSUserInterfaceLayoutDirection`）。**语义化边**：用 `Edge.leading` / `.trailing` 与 `alignment: .leading`，**禁止** `left`/`right` 与 `.left`/`.right` 对齐（不会镜像）；`NSTextAlignment.natural`（macOS 10.0+）让段落按语言自动对齐；`NSWritingDirection`（macOS 10.0+）表达文本方向。图标镜像用 `Image.layoutDirectionBehavior(_:)`（macOS 14.0+，`.mirrors`），旧路径 `.flipsForRightToLeftLayoutDirection(_:)`（macOS 10.15+）；SF Symbols 自带 RTL 变体。
**必须镜像**：返回/前进箭头、缩进、表示阅读方向的条形图标、表示前进/后退运动的图标（HIG：forward/backward motion 的图标要翻转）。
**绝不镜像**：时钟、媒体播放控制、方向性品牌 logo、勾选等通用符号、表示真实世界物体的图标（HIG 原文：`Don't flip logos or universal signs and marks.`；`clocks work the same everywhere`）。
**不镜像但需处理**：照片与插图（翻转会改变含义，必要时另做一版）；数字位数顺序永不反转，但**表示进度/计数方向的数字序列要反转**（HIG：`Reverse the order of numerals that show progress or a counting direction; never flip the numerals themselves.`）。
```swift
// RTL 安全布局：语义化边 + natural 对齐 + 选择性镜像
HStack(spacing: 8) {
    Image(systemName: "chevron.backward").layoutDirectionBehavior(.mirrors)   // macOS 14.0+
    Text(title).multilineTextAlignment(.leading)                              // 语义化对齐
    Spacer(minLength: 0)
}
.padding(.leading, 12).padding(.trailing, 8)                                  // 不用 .left/.right
```

## 6. 可访问性输入路径

**全键盘可达**：所有交互（含自绘控件）必须能纯键盘操作；AppKit 读系统状态 `NSApplication.shared.isFullKeyboardAccessEnabled`（macOS 10.6+），HIG 原文要求 `Support Full Keyboard Access when possible.` **VoiceOver 顺序与标签**：`Text` 自动成为元素，自绘组合视图要显式收口——`.accessibilityElement(children: .ignore)`（macOS 10.15+）、`.accessibilityLabel(_:)`（macOS 13.0+，`LocalizedStringResource`）、`.accessibilityHint(_:)`（macOS 13.0+）。**角色必须真实**：`.accessibilityAddTraits(.isButton)`（`AccessibilityTraits.isButton`，macOS 10.15+）；AppKit 用 `NSAccessibilityProtocol.setAccessibilityRole(_:)`（macOS 10.10+）。
**失败判定：自定义 glass 控件是一堆可点的 `ZStack`/`Rectangle`，暴露给 VoiceOver 时没有 button 角色、没有 label、Tab 键也进不去。** 判定方法：开启 Full Keyboard Access，只用键盘走完全流程；再用 Accessibility Inspector 逐个确认 role/label。**"按钮就是按钮"** ——如果它是一个按钮，就应该让 VoiceOver 读出按钮、按下、禁用状态。

## 7. 启动与响应性能（仅本主题相关）

**禁止在 `init`、`body`、`@State` 初值表达式里做磁盘/网络/解码工作**：`body` 内出现 `FileManager`、`Data(contentsOf:)`、`URLSession`、大数组排序即失败；读文件放 `.task { }` 或后台 actor。**大文档惰性加载**：文本/列表按需取，TextKit 2 用 `NSTextViewportLayoutController`（macOS 12.0+）只布局视口。**`MenuBarExtra` 与 `Settings` 场景不应在启动时构造重对象**：把重依赖改成 `@State` 惰性初始化或 `task`，并确认启动时长与内存峰值下降。**可测手段**：Instruments 的 **App Launch** 模板测启动阶段（含 dylib 加载、`applicationDidFinishLaunching`），文本/拖放交互叠加 **Time Profiler** 与 **Animation Hitches**（动画卡顿口径见 `validation.md`）；`XCTApplicationLaunchMetric` 元数据**只列 iOS/iPadOS/Mac Catalyst，未列原生 macOS**，故 macOS 启动回归**必须靠 Instruments App Launch 实测记录**，不要把 XCTest 启动指标当作 macOS 证据（见 §9）。

## 8. 交付时必须记录

除 `validation.md` 要求的 OS build / Xcode / SDK 版本外，本主题追加：**IME**——至少一种中文输入法 + 一种日文输入法的组合、候选、上屏路径，以及组合态是否触发过业务逻辑；**拖放**——应用内（同容器/跨容器）、跨应用（Finder / 文本编辑器）、Option 变换行为、取消与失败反馈；**本地化**——至少一种语言使用 String Catalog 复数变体，德语（长文案）与一种 RTL 语言（阿拉伯语或希伯来语）走完关键界面；**输入路径**——Full Keyboard Access 全流程、VoiceOver 关键流程、自定义控件 role/label；**启动**——Instruments App Launch 数值与基线对比。

## 9. 未确证 / 需在 SDK 核实

以下项**没有**从 Apple 官方文档确证，不要当事实使用：
1. **`^[%lld 个文件](inflect: true)` 这一自动语法一致（automatic grammar agreement）标记语法本身未确证。** 已确证的相关事实：`AttributeScopes.FoundationAttributes.inflect`（macOS 12.0+）、`AttributedString.LocalizationOptions.inflect`（macOS 15.0+）、`AttributeScopes.FoundationAttributes.AgreementArgumentAttribute`（macOS 14.0+）、`AttributedString.inflected()`（见来源）。**核实方式**：在 Xcode 里对含 `^[...](inflect: true)` 的 SwiftUI 字面量执行 `Product > Build`，看 String Catalog 是否生成该 key 与变体；或查 `swift-foundation` 源码中的 Markdown 属性解析。**在确证前，复数一律走 String Catalog 的 Vary by Plural。**
2. **伪本地化（pseudolanguage）的官方名称与启用入口未确证。** Apple 文档提到在图 1 中"choose a localization or pseudolanguage"，但未列出名称（如 Double-Length / Accented 之类）。**核实方式**：在 Xcode Scheme → Options → App Language 的下拉里读取实际条目名；不要在文档里写未验证的名称。
3. **AppKit 拖放/剪贴板符号的 macOS 引入版本未确证。** `NSPasteboard`、`NSPasteboard.PasteboardType`、`NSDraggingSource`、`NSDraggingDestination`、`NSDraggingInfo`、`NSDragOperation`、`NSView.registerForDraggedTypes(_:)`、`NSResponder.interpretKeyEvents(_:)`、`NSEvent.characters` 等符号页 `platforms` 只写 `macOS`、无 `introducedAt`。可安全视作长期存在，但**不要写具体版本号**。
4. **`TextEditor` "不支持富文本"是推证而非文档原文。** 已确证的是 `init(text: Binding<String>)`（macOS 11.0+），文档未正面声明富文本限制。**核实方式**：查 `TextEditor` 符号页的完整 initializer 列表与 SDK 头文件。
5. **`XCTApplicationLaunchMetric` 在原生 macOS 的可用性未确证（元数据未列 macOS）。** 核实方式：在 macOS 单元测试 target 中写 `measure(metrics: [XCTApplicationLaunchMetric()])` 编译并运行。在此之前 macOS 启动回归以 Instruments App Launch 为准。
6. **`.onDrop(of:delegate:)` 的替代符号未确证**：其 `deprecationSummary` 渲染为 `"Use  instead."`，引用未解析出标题。

## 来源

拖放：`draggable(_:)` https://developer.apple.com/documentation/swiftui/view/draggable(_:) · `dropDestination(for:action:isTargeted:)`（27.2 起弃用）https://developer.apple.com/documentation/swiftui/view/dropdestination(for:action:istargeted:) · `dropDestination(for:isEnabled:action:)`（macOS 26.0+）https://developer.apple.com/documentation/swiftui/view/dropdestination(for:isenabled:action:) · `DropSession` https://developer.apple.com/documentation/swiftui/dropsession · `onDrag(_:)` https://developer.apple.com/documentation/swiftui/view/ondrag(_:) · `onDrop(of:isTargeted:perform:)` https://developer.apple.com/documentation/swiftui/view/ondrop(of:istargeted:perform:) · `onDrop(of:delegate:)`（弃用）https://developer.apple.com/documentation/swiftui/view/ondrop(of:delegate:)-2vr9o
Transferable：`Transferable` https://developer.apple.com/documentation/coretransferable/transferable · `ProxyRepresentation` https://developer.apple.com/documentation/coretransferable/proxyrepresentation · `FileRepresentation` https://developer.apple.com/documentation/coretransferable/filerepresentation · `DataRepresentation` https://developer.apple.com/documentation/coretransferable/datarepresentation · `CodableRepresentation` https://developer.apple.com/documentation/coretransferable/codablerepresentation · `UTType` https://developer.apple.com/documentation/uniformtypeidentifiers/uttype-swift.struct · 自定义类型登记 https://developer.apple.com/documentation/uniformtypeidentifiers/defining-file-and-data-types-for-your-app
剪贴板与 AppKit 拖放：`clearContents()` https://developer.apple.com/documentation/appkit/nspasteboard/clearcontents() · `setString(_:forType:)` https://developer.apple.com/documentation/appkit/nspasteboard/setstring(_:fortype:) · `PasteboardType` https://developer.apple.com/documentation/appkit/nspasteboard/pasteboardtype · `.fileURL` https://developer.apple.com/documentation/appkit/nspasteboard/pasteboardtype/fileurl · `NSPasteboardItem` https://developer.apple.com/documentation/appkit/nspasteboarditem · `setDataProvider(_:forTypes:)` https://developer.apple.com/documentation/appkit/nspasteboarditem/setdataprovider(_:fortypes:) · `NSDraggingSource` https://developer.apple.com/documentation/appkit/nsdraggingsource · `NSDraggingDestination` https://developer.apple.com/documentation/appkit/nsdraggingdestination · `NSDraggingInfo` https://developer.apple.com/documentation/appkit/nsdragginginfo · `registerForDraggedTypes(_:)` https://developer.apple.com/documentation/appkit/nsview/registerforDraggedTypes(_:) · HIG Drag and drop https://developer.apple.com/design/human-interface-guidelines/drag-and-drop
文本编辑：`TextEditor` https://developer.apple.com/documentation/swiftui/texteditor · `textEditorStyle(_:)` https://developer.apple.com/documentation/swiftui/view/texteditorstyle(_:) · `.plain` https://developer.apple.com/documentation/swiftui/texteditorstyle/plain · `scrollContentBackground(_:)` https://developer.apple.com/documentation/swiftui/view/scrollcontentbackground(_:) · `TextField(_:text:axis:)` https://developer.apple.com/documentation/swiftui/textfield/init(_:text:axis:) · `lineLimit(_:reservesSpace:)` https://developer.apple.com/documentation/swiftui/view/linelimit(_:reservesspace:) · `NSTextLayoutManager` https://developer.apple.com/documentation/appkit/nstextlayoutmanager · `NSTextContentStorage` https://developer.apple.com/documentation/appkit/nstextcontentstorage · `NSTextViewportLayoutController` https://developer.apple.com/documentation/appkit/nstextviewportlayoutcontroller · `NSTextView.textLayoutManager` https://developer.apple.com/documentation/appkit/nstextview/textlayoutmanager · `init(usingTextLayoutManager:)` https://developer.apple.com/documentation/appkit/nstextview/init(usingtextlayoutmanager:)
IME 与键盘：`NSTextInputClient` https://developer.apple.com/documentation/appkit/nstextinputclient · `NSTextInputContext` https://developer.apple.com/documentation/appkit/nstextinputcontext · `interpretKeyEvents(_:)` https://developer.apple.com/documentation/appkit/nsresponder/interpretkeyevents(_:) · `NSEvent.modifierFlags` https://developer.apple.com/documentation/appkit/nsevent/modifierflags-swift.property · `Commands` https://developer.apple.com/documentation/swiftui/commands · `keyboardShortcut(_:)` https://developer.apple.com/documentation/swiftui/view/keyboardshortcut(_:)-8liec · `KeyboardShortcut` https://developer.apple.com/documentation/swiftui/keyboardshortcut · `FocusState` https://developer.apple.com/documentation/swiftui/focusstate · `focusable(_:)` https://developer.apple.com/documentation/swiftui/view/focusable(_:) · HIG Keyboards https://developer.apple.com/design/human-interface-guidelines/keyboards · `isFullKeyboardAccessEnabled` https://developer.apple.com/documentation/appkit/nsapplication/isfullkeyboardaccessenabled
本地化：String Catalog https://developer.apple.com/documentation/xcode/localizing-and-varying-text-with-a-string-catalog · 复数（stringsdict 旧路径）https://developer.apple.com/documentation/xcode/localizing-strings-that-contain-plurals · 格式化准备 https://developer.apple.com/documentation/xcode/preparing-dates-numbers-with-formatters · 测试本地化 https://developer.apple.com/documentation/xcode/testing-localizations-when-running-your-app · 预览本地化 https://developer.apple.com/documentation/xcode/previewing-localizations · `String(localized:table:bundle:locale:comment:)` https://developer.apple.com/documentation/swift/string/init(localized:table:bundle:locale:comment:) · `String.LocalizationValue` https://developer.apple.com/documentation/swift/string/localizationvalue · `NSLocalizedString(_:tableName:bundle:value:comment:)` https://developer.apple.com/documentation/foundation/nslocalizedstring(_:tablename:bundle:value:comment:) · `LocalizedStringResource` https://developer.apple.com/documentation/foundation/localizedstringresource
格式化与 Locale：`FormatStyle` https://developer.apple.com/documentation/foundation/formatstyle · `.number` https://developer.apple.com/documentation/foundation/formatstyle/number-7fxvo · `IntegerFormatStyle.Currency` https://developer.apple.com/documentation/foundation/integerformatstyle/currency · `IntegerFormatStyle.Percent` https://developer.apple.com/documentation/foundation/integerformatstyle/percent · `Date.FormatStyle` https://developer.apple.com/documentation/foundation/date/formatstyle · `Date.formatted(date:time:)` https://developer.apple.com/documentation/foundation/date/formatted(date:time:) · `Measurement.FormatStyle.init(width:locale:usage:numberFormatStyle:)` https://developer.apple.com/documentation/foundation/measurement/formatstyle/init(width:locale:usage:numberformatstyle:) · `BinaryInteger.formatted()` https://developer.apple.com/documentation/swift/binaryinteger/formatted() · `Locale.autoupdatingCurrent` https://developer.apple.com/documentation/foundation/locale/autoupdatingcurrent · SwiftUI `locale` https://developer.apple.com/documentation/swiftui/environmentvalues/locale
语法一致（`inflect` 属性确证、标记语法未确证）：`AttributeScopes.FoundationAttributes.inflect` https://developer.apple.com/documentation/foundation/attributescopes/foundationattributes/inflect · `AttributedString.LocalizationOptions.inflect` https://developer.apple.com/documentation/foundation/attributedstring/localizationoptions/inflect · `AgreementArgumentAttribute` https://developer.apple.com/documentation/foundation/attributescopes/foundationattributes/agreementargumentattribute
RTL：HIG Right to left https://developer.apple.com/design/human-interface-guidelines/right-to-left · `layoutDirection` https://developer.apple.com/documentation/swiftui/environmentvalues/layoutdirection · `layoutDirectionBehavior(_:)` https://developer.apple.com/documentation/swiftui/view/layoutdirectionbehavior(_:) · `flipsForRightToLeftLayoutDirection(_:)` https://developer.apple.com/documentation/swiftui/view/flipsforrighttoleftlayoutdirection(_:) · `NSView.userInterfaceLayoutDirection` https://developer.apple.com/documentation/appkit/nsview/userinterfacelayoutdirection · `NSTextAlignment.natural` https://developer.apple.com/documentation/appkit/nstextalignment/natural · `NSWritingDirection` https://developer.apple.com/documentation/appkit/nswritingdirection
可访问性与性能：HIG Accessibility https://developer.apple.com/design/human-interface-guidelines/accessibility · `accessibilityElement(children:)` https://developer.apple.com/documentation/swiftui/view/accessibilityelement(children:) · `accessibilityLabel(_:)` https://developer.apple.com/documentation/swiftui/view/accessibilitylabel(_:) · `accessibilityHint(_:)` https://developer.apple.com/documentation/swiftui/view/accessibilityhint(_:) · `AccessibilityTraits.isButton` https://developer.apple.com/documentation/swiftui/accessibilitytraits/isbutton · `setAccessibilityRole(_:)` https://developer.apple.com/documentation/appkit/nsaccessibilityprotocol/setaccessibilityrole(_:) · `XCTApplicationLaunchMetric`（元数据未列原生 macOS）https://developer.apple.com/documentation/xctest/xctapplicationlaunchmetric
