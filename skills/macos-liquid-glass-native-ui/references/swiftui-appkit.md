# SwiftUI / AppKit 实现策略

## 1. 总原则

原生 macOS 实现优先让系统组件获得系统设计语言，而不是手工重做 Liquid Glass。

Apple 的核心口径（原文，作为本文件所有判断的上位依据）：

> Reduce your use of custom backgrounds in controls and navigation elements. Any custom backgrounds and appearances you use in these elements might overlay or interfere with Liquid Glass or other effects that the system provides, such as the scroll edge effect.

> Avoid overusing Liquid Glass effects. If you apply Liquid Glass effects to a custom control, do so sparingly. … Limit these effects to the most important functional elements in your app.

来源：https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass

优先顺序：

1. 标准 SwiftUI / AppKit 组件（自动获得 Liquid Glass）；
2. 系统提供的 style / material / toolbar API（`.buttonStyle(.glass)` 等）；
3. 项目已有原生封装；
4. 最后才是显式自定义 glass。

关键区分：**「系统自动获得」与「需要显式调用」不是一回事。**

| 区域 | 是否自动 | 需要做什么 |
| --- | --- | --- |
| Toolbar / 窗口控件 / Sheet / Popover / Menu | 自动 | 删掉自定义 background，别覆盖 |
| Sidebar / List / Table / Form 行 | 自动 | 不要逐行加 glass |
| Button / Slider / Toggle 等控件 | 自动 | 用系统 button style，不要自画 |
| 浮在内容上方的自定义控件组 | **需显式** | `glassEffect(_:in:)` + `GlassEffectContainer` |
| 内容延伸到 sidebar/inspector 之下 | **需显式** | `backgroundExtensionEffect()` / `NSBackgroundExtensionView` |

`.ultraThinMaterial` 等 Material **不是** Liquid Glass：它没有玻璃的折射、边缘高光、交互响应与 morph。在 macOS 26 上把 Material 当作 Liquid Glass 的等价物是错的；它只在为更低 deployment target 写降级分支时可用。

## 2. macOS 26 Liquid Glass API 与版本合同

以下签名与可用性均取自 Apple 官方文档符号页（2026-09-30 核对，`developer.apple.com/tutorials/data/documentation/…json` 元数据）。**写入代码前仍应在目标 SDK 中 ⌥-click 复核一次**——文档元数据与 Xcode SDK 偶有偏差（本文档已发现两处，见 §2.5）。

### 2.1 SwiftUI 符号表

| 符号 | 签名 / 取值 | 可用性 |
| --- | --- | --- |
| `glassEffect(_:in:)` | `nonisolated func glassEffect(_ glass: Glass = .regular, in shape: some Shape = DefaultGlassEffectShape()) -> some View` | macOS 26.0+ |
| `GlassEffectContainer` | `@MainActor @preconcurrency struct GlassEffectContainer<Content> where Content: View`；`init(spacing: CGFloat?, content: () -> Content)` | macOS 26.0+ |
| `glassEffectID(_:in:)` | `nonisolated func glassEffectID(_ id: (some Hashable & Sendable)?, in namespace: Namespace.ID) -> some View` | macOS 26.0+ |
| `glassEffectUnion(id:namespace:)` | `@MainActor @preconcurrency func glassEffectUnion(id: (some Hashable & Sendable)?, namespace: Namespace.ID) -> some View` | macOS 26.0+ |
| `Glass` | `struct Glass`；`.regular` / `.clear` / `.identity`；`func tint(_ color: Color?) -> Glass`；`func interactive(_ isEnabled: Bool = true) -> Glass` | macOS 26.0+ |
| `GlassEffectTransition` | `.matchedGeometry` / `.materialize` | macOS 26.0+ |
| `PrimitiveButtonStyle.glass` | `static var glass: GlassButtonStyle` | macOS 26.0+ |
| `PrimitiveButtonStyle.glassProminent` | `static var glassProminent: GlassProminentButtonStyle` | macOS 26.0+ |
| `PrimitiveButtonStyle.glass(_:)` | `nonisolated static func glass(_ glass: Glass) -> Self`（传变体，如 `.glass(.clear)`） | macOS 26.0+ |
| `backgroundExtensionEffect()` | `@MainActor @preconcurrency func backgroundExtensionEffect() -> some View` | 文档元数据列 macOS 26.0+；**符号页渲染的 availability 未显示 macOS，按未确证处理，见 §2.5** |
| `ToolbarSpacer` | `nonisolated init(_ sizing: SpacerSizing = .flexible, placement: ToolbarItemPlacement = .automatic)`；`SpacerSizing` 有 `.fixed` / `.flexible` | macOS 26.0+ |
| `ToolbarContent.hidden(_:)` | `nonisolated func hidden(_ hidden: Bool = true) -> some ToolbarContent` | 文档列 macOS 15.0+（非 26 专属；iOS 侧列 26.4 等反常值，以 SDK 为准） |
| `ConcentricRectangle` | `struct ConcentricRectangle: Shape`；`init()` 缺省跟随容器曲率，另有 `init(corners:isUniform:)` 等 | macOS 26.0+ |
| `ScrollEdgeEffectStyle` | `.automatic` / `.hard` / `.soft`；`scrollEdgeEffectStyle(_ style: ScrollEdgeEffectStyle?, for edges: Edge.Set)` | macOS 26.0+ |
| `safeAreaBar(edge:alignment:spacing:content:)` | `nonisolated func safeAreaBar(edge: HorizontalEdge, alignment: VerticalAlignment = .center, spacing: CGFloat? = nil, @ContentBuilder content: () -> some View) -> some View` | macOS 26.0+ |
| `Shape.rect(corners:isUniform:)` | `static func rect(corners: Edge.Corner.Style, isUniform: Bool = false) -> Self` | macOS 26.0+ |

非 Liquid Glass 专属、但结构改造常用的稳定符号：

| 符号 | 可用性 |
| --- | --- |
| `inspector(isPresented:content:)` | macOS 14.0+ |
| `inspectorColumnWidth(min:ideal:max:)` | macOS 14.0+ |
| `searchable(text:placement:prompt:)` | macOS 13.0+ |
| `searchable(text:isPresented:placement:prompt:)` | macOS 14.0+ |
| `navigationSplitViewColumnWidth(_:)` | macOS 13.0+ |
| `navigationSplitViewColumnWidth(min:ideal:max:)` | macOS 13.0+ |

### 2.2 AppKit 符号表

| 符号 | 签名 / 取值 | 可用性 |
| --- | --- | --- |
| `NSGlassEffectView` | `class NSGlassEffectView: NSView` | macOS 26.0+ |
| `NSGlassEffectView.contentView` | `var contentView: NSView?` | macOS 26.0+ |
| `NSGlassEffectView.cornerRadius` | `var cornerRadius: CGFloat` | macOS 26.0+ |
| `NSGlassEffectView.style` | `var style: NSGlassEffectView.Style`；`Style` 仅有 `.clear` / `.regular` | macOS 26.0+ |
| `NSGlassEffectView.tintColor` | `@NSCopying var tintColor: NSColor?` | macOS 26.0+ |
| `NSGlassEffectView.effectIsInteractive` | `var effectIsInteractive: Bool` | **macOS 27.0+**（文档元数据；若你按 26.0 目标构建就不要无条件使用） |
| `NSBackgroundExtensionView` | `class NSBackgroundExtensionView: NSView` | macOS 26.0+ |
| `NSButton.BezelStyle.glass` | `case glass` | macOS 26.0+ |
| `NSToolbarItem.isHidden` | `var isHidden: Bool` | macOS 15.0+ |
| `NSToolbarItem.Identifier.space` | `static let space` | 文档未给 macOS 引入版本（长期存在），可直接使用 |

### 2.3 `#available` 分支模式

把 glass 相关代码隔离在一个 `@available` 类型里，避免 `#available` 散落在每个 view body：

```swift
// 好：可用性边界只有一处
@available(macOS 26.0, *)
struct LiquidGlassSurface<Content: View>: View {
    var content: Content

    var body: some View {
        content
            .padding(12)
            .glassEffect(.regular.interactive(), in: .rect(cornerRadius: 12))
    }
}

// 调用点显式分支
if #available(macOS 26.0, *) {
    LiquidGlassSurface(content: PlaybackControls())
} else {
    // 降级：不是 Liquid Glass 等价物，只是「不崩且可读」
    PlaybackControls()
        .padding(12)
        .background(.ultraThinMaterial, in: RoundedRectangle(cornerRadius: 12))
}
```

规则：

- deployment target ≥ macOS 26.0 时，不要写 `#available` 也不要留 Material 降级分支；
- deployment target < macOS 26.0 时，用 `@available(macOS 26.0, *)` 把 glass 收进独立类型，调用点只留一个 `if #available`；
- 降级分支必须用注释标明「legacy fallback，非 Liquid Glass」；
- 26 ↔ 27 的差异（如 `effectIsInteractive`）用单独的 `if #available(macOS 27.0, *)`，不要和 26.0 混在一个 guard 里。

### 2.4 显式自定义 glass 的正确写法

`glassEffect` 默认 `.regular` + Capsule（声明默认值为 `DefaultGlassEffectShape()`）。要圆角矩形就显式给 shape：

```swift
Text("Hello, World!")
    .font(.title)
    .padding()
    .glassEffect()                                   // .regular + Capsule

Text("Hello, World!")
    .font(.title)
    .padding()
    .glassEffect(in: .rect(cornerRadius: 16))        // 大控件用圆角矩形

Text("Hello, World!")
    .font(.title)
    .padding()
    .glassEffect(.regular.tint(.orange).interactive())  // 着色 + 交互响应
```

**顺序约束（官方原文）：** "Apply the `glassEffect(_:in:)` modifier after other modifiers that affect the appearance of the view." 即 `.padding()`、`.font()`、`.frame()` 放在 `glassEffect` **之前**。glass 锚定在 view 的 bounds 上，padding 会被算进材质范围。

### 2.5 两处必须自己复核的版本事实

1. **`backgroundExtensionEffect()` 的 macOS 可用性未确证。** 本文档从 `developer.apple.com/tutorials/data/documentation/swiftui/view/backgroundextensioneffect().json` 抓到的 `platforms` 元数据**列出 macOS 26.0**，但该符号页渲染出来的 availability 列表**没有显示 macOS**。两者矛盾，因此不要在代码里无条件依赖它。
   核实方式：在 Xcode 中 ⌥-click 该符号看 SDK 头部，或 `swift-symbolgraph-extract -module-name SwiftUI -target arm64-apple-macos26.0` 后检索 `backgroundExtensionEffect`；也可直接尝试编译含该调用的最小 target。
   若目标 SDK 不提供，改用 **已确证 macOS 26.0+** 的 AppKit 等价物 `NSBackgroundExtensionView`（见 §4.3）。

2. **`NSGlassEffectView.effectIsInteractive` 是 macOS 27.0+，不是 26.0+。** `NSGlassEffectView` 本体与其 `contentView` / `cornerRadius` / `style` / `tintColor` 均为 26.0+，只有 `effectIsInteractive` 的文档元数据是 27.0。

`scrollEdgeEffectStyle` / `safeAreaBar` / `ConcentricRectangle` 本次已逐页确证为 macOS 26.0+，可直接使用（见 §2.1 表）。

### 2.6 自定义 glass 必须用容器合并

**规则：同屏存在 ≥2 个自定义 `glassEffect` 时，必须包在同一个 `GlassEffectContainer` 内。**

Apple 原文：

> Creating too many Liquid Glass effect containers and applying too many effects to views outside of containers can degrade performance. Limit the use of Liquid Glass effects onscreen at the same time.

容器的作用：`Each view with a Liquid Glass effect contributes a shape rendered with the effect to a set of shapes. SwiftUI renders the effects together, improving rendering performance and allowing the effects to interact with and morph into one another.`

```swift
@Namespace private var namespace
@State private var isExpanded = false

var body: some View {
    GlassEffectContainer(spacing: 40.0) {
        HStack(spacing: 40.0) {
            Image(systemName: "scribble.variable")
                .frame(width: 80, height: 80)
                .glassEffect()
                .glassEffectID("pencil", in: namespace)

            if isExpanded {
                Image(systemName: "eraser.fill")
                    .frame(width: 80, height: 80)
                    .glassEffect()
                    .glassEffectID("eraser", in: namespace)
            }
        }
    }
}
```

- `spacing` 控制形状何时开始融合：**值越大越早融合**。容器 `spacing` 大于内部 `HStack` 间距时，静止状态就会融合——通常不是想要的。
- `glassEffectID(_:in:)` + `@Namespace`：让出现在/消失的形状正确 morph。只在 view 层级过渡/动画期间生效。
- `GlassEffectTransition`：容器 spacing 内增删用默认 `.matchedGeometry`；比 spacing 更远的用 `.materialize`。
- 视图在布局容器之外（动态生成、游离）时，用 `glassEffectUnion(id:namespace:)` 让多个几何共同贡献同一个 capsule。
- 多个互不相关的玻璃组（例如两组相距很远的浮动控件）才拆成多个容器；容器数量本身也是成本项。

## 3. 不重复给系统已处理区域叠玻璃

这是「禁止」升级为「禁止 + 正确替代 API」：

| 想做的事（错误） | 正确替代 |
| --- | --- |
| 给 toolbar 加自定义半透明背景 | 删掉；系统 toolbar 已有 Liquid Glass |
| 给每个 toolbar button 加 `.glassEffect()` | `.buttonStyle(.glass)` 或 `.buttonStyle(.glassProminent)` |
| 自己画圆角玻璃按钮 | `.buttonStyle(.glass)` / `.glassProminent` / `.glass(.clear)` |
| 给 popover `contentView` 加 `NSVisualEffectView` | 删掉（官方明确要求 audit popover 的 visual effect view） |
| 给 split view 分区加背景 | 删掉；改用 `NSBackgroundExtensionView` / `backgroundExtensionEffect()` |
| 内容滚到 toolbar 下方看不清 | `scrollEdgeEffectStyle(_:for:)` 或 `safeAreaBar(edge:…)`，不要贴一层 blur |
| 隐藏 toolbar item 时把 item 里的视图设为透明 | 隐藏整个 item：`ToolbarContent.hidden(_:)` / `NSToolbarItem.isHidden` |
| 自己写圆角数值 | `ConcentricRectangle` / `Shape.rect(corners:isUniform:)` |

**官方易错点（原文）**，务必检查：

> Check how you hide toolbar items. If you see an empty toolbar item without any content, your app might be hiding the view in the toolbar item instead of the item itself.

「空 toolbar item」是隐藏姿势错误的确诊症状：隐藏 item 内的 view 会留下一个空槽位。

## 4. SwiftUI

### 4.1 Window

根据任务选择 `WindowGroup`、`DocumentGroup` 或已有窗口架构。不要只按截图固定窗口尺寸。明确 default size、minimum size、resizability、multi-window behavior、restoration。

### 4.2 Navigation / Toolbar / Search

- 优先 `NavigationSplitView`，不要手工 HStack 模拟 sidebar/content/inspector。
- 列宽约束用 `.navigationSplitViewColumnWidth(_:)`（macOS 13.0+）。
- Inspector 用 `.inspector(isPresented:content:)`（macOS 14.0+），不要自建右侧面板。
- Search 用 `.searchable(text:placement:prompt:)`（macOS 13.0+），明确 scope；全局 search、sidebar 集合 search、document find 不混。
- Toolbar 分组用 `ToolbarSpacer`（macOS 26.0+）：共享同一背景的 item 用 `ToolbarSpacer(.fixed)` 分隔，而不是自己塞图片或 padding。
- 系统已给 glass 外观时：不给每个 toolbar button 再加 `.glassEffect()`；需要突出按钮时用系统 button style；重要命令同时在 Commands/Menu 可访问。

```swift
.toolbar {
    ToolbarItem(placement: .primaryAction) { FavoriteButton() }
    ToolbarSpacer(.fixed, placement: .primaryAction)   // 同组内分隔
    ToolbarItem(placement: .primaryAction) { ShareButton() }
        .hidden(!canShare)                              // 隐藏整个 item，不是 item 里的视图
}
```

### 4.3 Content Extension

```swift
// SwiftUI：可用性未确证，见 §2.5，先确认再依赖
detailContent.backgroundExtensionEffect()
```

```swift
// AppKit：已确证 macOS 26.0+
if #available(macOS 26.0, *) {
    let ext = NSBackgroundExtensionView()
    ext.autoresizingMask = [.width, .height]
    containerView.addSubview(ext)
}
```

硬约束：单实例、会被裁剪、注意清晰度与性能。详见 `native-structure.md`。

### 4.4 Custom Glass

只有浮于内容层上方的少量自定义控制需要显式 glass。

适合：地图浮动控制、媒体播放控制、少量 floating action group、自定义工具 palette。

不适合：文章正文、数据 table body、所有 list row、图表背景、每个 setting section。

对 Button，不要把「button sitting on a raw glass panel」误当系统 glass button；优先用 `.buttonStyle(.glass)`，再按需要设置边界形状。

## 5. AppKit

### 5.1 Window / Split View

优先 `NSWindow`、`NSSplitViewController`、`NSToolbar`、系统 sidebar/list/table。不要为现代视觉重写现有稳定 AppKit 信息架构。

### 5.2 Material 路径：先删，再加

**第一步永远是审查并删除不必要的自定义 background / vibrancy。** 官方要求 audit split views、tab bars、toolbars、popover 的 custom background，优先删除并让系统决定背景外观。

只有删除后仍缺一个「浮在内容上方的功能层」时，才考虑 `NSGlassEffectView`。

```swift
// 删除这类代码（popover contentView 上的 vibrancy 是官方点名的反例）
// let v = NSVisualEffectView(); v.material = .popover; popover.contentViewController?.view.addSubview(v)

@available(macOS 26.0, *)
func makeFloatingControlPanel() -> NSGlassEffectView {
    let glass = NSGlassEffectView()
    glass.style = .regular                 // 只有 .clear / .regular
    glass.cornerRadius = 16                // pt，与容器曲率协调
    glass.tintColor = nil                  // 需要强调时才给 NSColor

    let stack = NSStackView(views: [playButton, scrubber])
    stack.orientation = .horizontal
    glass.contentView = stack              // 内容走 contentView，不要 addSubview 到 glass 本身

    if #available(macOS 27.0, *) {         // effectIsInteractive 是 27.0+
        glass.effectIsInteractive = true
    }
    return glass
}
```

规则：

- `NSGlassEffectView` 只承载浮动控制、工具 palette 这类功能层；不要拿它当列表或内容容器背景。
- 内容一律走 `contentView`，保持 glass 层与内容层的职责分离。
- `NSVisualEffectView` 不是被废弃，但**不要用它去近似 Liquid Glass**。它继续适用于确实需要传统 vibrancy 语义的少数场景，且必须先确认 blending mode、material 语义、active/inactive window 表现、辅助设置下的可读性。
- 按钮用系统 bezel style，不要自画：

```swift
let button = NSButton(title: "Play", target: self, action: #selector(play))
if #available(macOS 26.0, *) {
    button.bezelStyle = .glass
}
```

### 5.3 Toolbar

- 支持系统 overflow 行为；
- 高价值命令保持可发现；
- 可隐藏/可自定义时，菜单中仍有对应命令；
- 隐藏 item 用 `NSToolbarItem.isHidden`（macOS 15.0+），不要隐藏 item 内部的 view——否则出现空 toolbar item；
- 分两组共享背景用 `NSToolbarItem.Identifier.space`；
- 不把所有 menu item 都复制成 toolbar item。

## 6. Hybrid

- 不为统一视觉而同时保留两套互相冲突的 command / selection state；
- selection、undo、focus、window state 需要单一来源；
- bridge 组件要明确生命周期和 ownership；
- 原生 material 的 active/inactive state 不能被 SwiftUI overlay 锁死。

## 7. 辅助功能：键名 + 读取代码

每个系统设置名后面直接给出对应环境键与最小片段。**不要靠固定透明度硬扛，要读键并改变行为。**

| 系统设置 | 环境键 | 可用性 | 为 true 时应做什么 |
| --- | --- | --- | --- |
| Reduce Transparency | `@Environment(\.accessibilityReduceTransparency) var reduceTransparency: Bool` | macOS 10.15+ | 窗口/自定义背景改为不透明 |
| Increase Contrast | `@Environment(\.colorSchemeContrast) var contrast: ColorSchemeContrast`（`.increased`） | macOS 10.15+ | 加边框、加深分隔、提高文字对比 |
| Reduce Motion | `@Environment(\.accessibilityReduceMotion) var reduceMotion: Bool` | macOS 10.15+ | 去掉非必要 morph / 位移动画 |
| Show Borders | `@Environment(\.accessibilityShowBorders) var showBorders: Bool` | macOS 11.0+，`@backDeployed(before: macOS 26.1)` | 给自定义交互控件画清晰可见的边缘 |
| Differentiate Without Color | `@Environment(\.accessibilityDifferentiateWithoutColor) var differentiate: Bool` | macOS 10.15+ | 状态不只靠颜色区分 |

```swift
struct GlassControl: View {
    @Environment(\.accessibilityReduceTransparency) private var reduceTransparency
    @Environment(\.accessibilityShowBorders) private var showBorders
    @Environment(\.colorSchemeContrast) private var contrast
    @Environment(\.accessibilityReduceMotion) private var reduceMotion

    @State private var isOn = false

    var body: some View {
        content
            .padding(12)
            .background {
                if reduceTransparency {
                    // 官方：true 时 window 背景不应半透明，应为不透明
                    RoundedRectangle(cornerRadius: 12).fill(.background)
                } else if #available(macOS 26.0, *) {
                    Color.clear.glassEffect(.regular, in: .rect(cornerRadius: 12))
                }
            }
            .overlay {
                if showBorders || contrast == .increased {
                    RoundedRectangle(cornerRadius: 12).strokeBorder(.separator)
                }
            }
            .animation(reduceMotion ? nil : .default, value: isOn)
    }
}
```

`accessibilityShowBorders` 的版本语义（官方原文）：

> On macOS 27 and later, the system provides a dedicated Show Borders setting in System Settings. On earlier versions of macOS, this value is true when Increased Contrast is enabled.

含义：**macOS 27 起才是独立开关；macOS 26.x 及更早，这个值等于 Increase Contrast 打开。** 所以不要断言「Show Borders 在 macOS 26 是独立设置」，也不要据此把 Increase Contrast 分支写成不可达代码——两者在旧系统上是同一路径。

不要写入未经核实的事实：macOS 26 的 **Clear / Tinted 属于 System Settings → Appearance 的图标/小组件外观变体，不是窗口材质的运行时开关**。窗口材质可读性只由 Reduce Transparency 与 Increase Contrast 驱动。

## 8. Concentric Geometry

靠近 window、toolbar、panel 边缘的自定义圆角应与外层轮廓协调，而不是随手写 12/16/24。**单位一律用 pt**（SwiftUI 与 AppKit 的长度语义都是 point，不是 CSS px）。

规则：

- 离容器边缘越近，内层圆角越应跟随外层曲率；
- 内边距越小，内外半径差越小；
- 优先用系统同心圆角能力：`ConcentricRectangle()`（macOS 26.0+，`init()` 自动跟随容器），需要同款圆角风格时用 `Shape.rect(corners:isUniform:)`（macOS 26.0+）；
- 低版本降级时手算「外半径 − 内边距」并保持一致，不要为所有控件强制 pill。

```swift
content
    .padding(12)
    .glassEffect(.regular, in: ConcentricRectangle())   // macOS 26.0+
```

## 9. Interaction Feedback

默认依赖系统 hover、press、focus、selection 行为。

自定义反馈：

- 少量 interactive glass 可用 `.interactive()` 获得系统的指针响应，而不是自己写动画；
- 不给所有玻璃容器加弹性；
- Reduce Motion 下移除非必要弹性和位移；
- 完成状态不能只靠动效。

## 10. 不要做

- 给整个 `NavigationSplitView` 叠一层自定义 blur；
- 给每个 `List` row 画半透明圆角卡片；
- 在 Toolbar 里二次模拟一套 Web 玻璃按钮；
- 用 `.ultraThinMaterial` 冒充 macOS 26 的 Liquid Glass；
- 不用 `GlassEffectContainer` 就散布多个 `glassEffect`；
- 靠隐藏 toolbar item 内部的视图来隐藏 item；
- 为了截图好看关掉真实窗口 resize；
- 用固定 RGB 覆盖 system semantic colors；
- 把 AppKit 原有菜单/快捷键删掉只保留 toolbar；
- 把 iOS Tab Bar 当 macOS 主导航默认方案。

## 11. 实现报告

完成后列出：

- 使用的系统组件；
- 自定义组件与原因；
- 自定义 glass 的位置、数量、是否都在 `GlassEffectContainer` 内；
- 读取了哪些辅助功能环境键、对应行为；
- 测试过的窗口尺寸与辅助设置；
- 全部 `#available` 分支及其降级行为；
- 尚未验证内容（尤其 §2.5 两处版本事实）。
