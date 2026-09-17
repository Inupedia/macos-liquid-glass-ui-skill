# SwiftUI / AppKit 实现策略

## 1. 总原则

原生 macOS 实现优先让系统组件获得系统设计语言，而不是手工重做 Liquid Glass。

优先顺序：

1. 标准 SwiftUI / AppKit 组件；
2. 系统提供的 style / material / toolbar API；
3. 项目已有原生封装；
4. 最后才是自定义 glass view。

如果标准 Toolbar、Sidebar、Button 已经自动获得 Liquid Glass 外观，不重复叠加 raw glass effect。

## 2. SwiftUI

### Window

根据任务选择 `WindowGroup`、`DocumentGroup` 或已有窗口架构。不要只按截图固定窗口尺寸。

明确：

- default size
- minimum size
- resizability
- multi-window behavior
- restoration（若产品需要）

### Navigation

优先使用符合信息架构的系统容器，例如 `NavigationSplitView`，而不是手工 HStack 模拟 sidebar/content/inspector。

只有在系统容器无法表达产品行为时才自定义 split layout，并完整处理最小宽度、折叠和焦点。

### Toolbar

优先 `.toolbar` 与系统 placement。按语义分组，避免十几个同权重 item。

系统已经提供 glass 外观时：

- 不给每个 toolbar button 再加 `.glassEffect()`；
- 需要突出按钮时优先使用合适的系统 button style；
- 自定义形状时保持与容器的 concentric 关系；
- 重要命令同时在 Commands/Menu 中可访问。

### Custom Glass

只有浮于内容层上方的少量自定义控制需要显式 glass。

适合：

- 地图浮动控制
- 媒体播放控制
- 少量 floating action group
- 自定义工具 palette

不适合：

- 文章正文
- 数据 table body
- 所有 list row
- 图表背景
- 每个 setting section

对 Button，不要把“button sitting on a raw glass panel”误当系统 glass button；优先使用系统 button style，再按需要设置边界形状。

### Search

使用系统 search 能力时明确 scope。全局 search、sidebar collection search、document find 不混在一起。

## 3. AppKit

### Window / Split View

优先 `NSWindow`、`NSSplitViewController`、`NSToolbar`、系统 sidebar/list/table 等成熟能力。

不要为现代视觉重写现有稳定 AppKit 信息架构。

### Material

AppKit 的背景 blending / visual effect 只在需要时使用。内容区域仍然保持稳定可读。

自定义 `NSVisualEffectView` 前先确认：

- blending mode 是否正确；
- material 是否符合区域语义；
- active/inactive window 下是否合理；
- accessibility 设置变化时是否仍可读。

### Toolbar

使用 `NSToolbar` 时：

- 支持系统 overflow 行为；
- 高价值命令保持可发现；
- 可隐藏/可自定义 toolbar 时，菜单中仍有对应命令；
- 不把所有 menu item 都复制成 toolbar item。

## 4. Hybrid

SwiftUI + AppKit 混合时：

- 不为统一视觉而同时保留两套互相冲突的 command / selection state；
- selection、undo、focus、window state 需要单一来源；
- bridge 组件要明确生命周期和 ownership；
- 原生 material 的 active/inactive state 不能被 SwiftUI overlay 锁死。

## 5. 系统偏好

自定义控件至少考虑：

- Light / Dark
- Reduce Transparency
- Increase Contrast
- Reduce Motion
- Show Borders（目标系统支持时）
- 用户对 Liquid Glass 清晰/着色程度的系统偏好

不要固定一套透明度后覆盖这些环境变化。

## 6. Concentric Geometry

靠近 window、toolbar、panel 边缘的自定义 rounded rect 应与外层轮廓协调，而不是随意用 12/16/24px。

规则：

- 离容器边缘越近，内层圆角越应跟随外层曲率；
- 内边距越小，内外半径差越小；
- 系统提供 concentric corner 能力时优先使用；
- 不为所有控件强制 pill。

## 7. Interaction Feedback

默认依赖系统 hover、press、focus、selection 行为。

自定义反馈：

- 少量 interactive glass 可有克制的 bounce/press；
- 不给所有玻璃容器加弹性；
- Reduce Motion 下移除非必要弹性和位移；
- 完成状态不能只靠动效。

## 8. 不要做

- 给整个 `NavigationSplitView` 叠一层自定义 blur；
- 给每个 `List` row 画半透明圆角卡片；
- 在 Toolbar 里二次模拟一套 Web 玻璃按钮；
- 为了截图好看关掉真实窗口 resize；
- 用固定 RGB 覆盖 system semantic colors；
- 把 AppKit 原有菜单/快捷键删掉只保留 toolbar；
- 把 iOS Tab Bar 当 macOS 主导航默认方案。

## 9. 实现报告

完成后列出：

- 使用的系统组件；
- 自定义组件；
- 自定义原因；
- 自定义 glass 的位置；
- 测试过的窗口与辅助设置；
- 尚未验证内容。
