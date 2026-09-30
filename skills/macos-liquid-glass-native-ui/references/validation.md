# 原生 macOS 验收

构建通过不等于原生体验通过。根据任务范围选择相关项验证，并在交付中区分「已验证」和「未验证」。

判定口径：每一项都要能回答「怎么做的、在什么条件下看、结果是什么」。答不出就是未验证。

## 窗口矩阵

至少覆盖：最小可用窗口；常规窗口；大窗口；全屏（产品支持时）；Sidebar 展开/收起；Inspector 展开/收起；多窗口（产品支持时）。

检查：

- toolbar 不挤压；
- column width 的 min/ideal/max 在连续 resize 中不跳变；
- content 不被 sidebar/inspector 压坏；
- sheet/popover 不超出可见范围；
- table/editor/scroll view 仍可用；
- 窄窗口有明确降级。

## 视觉环境

- Light
- Dark
- active key window
- inactive/background window
- 普通内容背景
- 图片/地图等 rich background（相关时）

Liquid Glass 必须保持层级而不是在某个背景下消失。

## Accessibility

**每条检查都从「读哪个键」出发，并给出该键为 true / 非默认时的 fallback 行为。** 只勾「我打开了 Reduce Transparency 看了一眼」不算通过。

| # | 系统设置 | 要读取的环境键 | 可用性 | 通过标准：键为非默认值时的 fallback 行为 |
| --- | --- | --- | --- | --- |
| A1 | Reduce Transparency | `@Environment(\.accessibilityReduceTransparency) private var reduceTransparency` | macOS 10.15+ | glass / 半透明背景退为不透明（官方：true 时 window 背景不应半透明），文字对比不下降，无内容被遮挡 |
| A2 | Increase Contrast | `@Environment(\.colorSchemeContrast) private var contrast`，判断 `== .increased` | macOS 10.15+ | 自定义控件出现/加强边缘，分隔与选中态对比提高；不出现「开了反而更糊」 |
| A3 | Reduce Motion | `@Environment(\.accessibilityReduceMotion) private var reduceMotion` | macOS 10.15+ | morph / 位移 / 弹性动画停用或退化为交叉淡入；完成状态仍可识别 |
| A4 | Show Borders | `@Environment(\.accessibilityShowBorders) private var showBorders` | macOS 11.0+，`@backDeployed(before: macOS 26.1)` | 自定义交互控件画出清晰可见边缘，在任何窗口尺寸下可区分 |
| A5 | Differentiate Without Color | `@Environment(\.accessibilityDifferentiateWithoutColor) private var differentiate` | macOS 10.15+ | 状态不只靠颜色：补 icon / 形状 / 文字 |

**A4 版本语义必须写对（官方原文）：**

> On macOS 27 and later, the system provides a dedicated Show Borders setting in System Settings. On earlier versions of macOS, this value is true when Increased Contrast is enabled.

即 macOS 26.x 及更早该值等于 Increase Contrast 开启，**不是独立开关**。验收记录里不要写成「在 macOS 26 单独测了 Show Borders」。

**不要写成系统偏好驱动的一项：** macOS 26 的 Clear / Tinted 属于 System Settings → Appearance 的图标/小组件外观变体，**不是窗口材质运行时开关**。窗口材质可读性只由 A1（Reduce Transparency）与 A2（Increase Contrast）驱动。不要把它列进本表。

其余检查：

- Keyboard-only 全流程可达；
- VoiceOver 语义（有条件时实测）；
- Focus order 合理，不跳入隐藏元素；
- 大字号 / 缩放；
- 自定义 glass/control 是最高优先级检查对象；系统组件通常优先沿用系统行为。

## Toolbar / Commands

- 重要 toolbar action 在窄窗口 overflow 后仍可访问；
- toolbar 可隐藏/自定义时，关键命令仍有 menu/shortcut 路径；
- **隐藏 item 时验证是否出现空 toolbar item**：隐藏的是整个 item（`ToolbarContent.hidden(_:)` / `NSToolbarItem.isHidden`）而非 item 内视图；
- 分组只使用 `ToolbarSpacer` / `NSToolbarItem.Identifier.space`，没有靠图片或 padding 伪装间隔；
- shortcut 与 menu/toolbar enablement 一致；
- key window 切换后命令作用对象正确；
- destructive command 有明确确认或撤销策略。

## Sidebar / Selection / Inspector

- Sidebar selection 和 content 一致；
- keyboard 移动 selection 正常；
- multi-select 范围正确；
- Inspector 始终对应当前 selection；
- 删除当前项后的 selection/focus 合理；
- 无 selection 有有效状态。

## Search

- scope 清楚；
- placement 与 scope 匹配（`.sidebar` 不用于 document find）；
- 空查询、无结果、错误状态合理；
- recent/suggestion 不泄露不该公开的信息；
- Escape/clear 行为合理；
- search focus 不破坏主要 command shortcuts。

## Sheets / Popovers

- 打开时 focus 合理；
- Escape 关闭最高层可关闭 UI；
- 关闭后 focus 回到触发点；
- 未保存内容不会静默丢失；
- popover 自动避让 window 边界；
- **popover content view 上没有自加的 `NSVisualEffectView` / 自定义背景**（官方要求删除）；
- 背景 window/content 不被意外滚动或操作。

## 滚动边缘可读性

- 内容滚到 toolbar / 自定义 bar 下方时，控件与文字仍可读；
- 使用的是 `scrollEdgeEffectStyle(_:for:)` 或 `safeAreaBar(edge:…)`，而不是自己贴一层 blur；
- `.hard` / `.soft` / `.automatic` 的选择与产品视觉一致，且不遮挡内容语义。

## Content Extension

- 单实例：同一窗口只有一处 background extension，不是每行/每卡都加；
- 被裁剪的边缘没有切掉关键视觉信息；
- 镜像 + 模糊后，上方 sidebar/inspector 文字仍可读；
- rich content 滚动与 resize 时不掉帧；
- SwiftUI `backgroundExtensionEffect()` 若使用，已确认目标 SDK 的 macOS 可用性（见 `swiftui-appkit.md` §2.5）；否则使用 `NSBackgroundExtensionView`。

## Liquid Glass 自定义检查

对每一个手工 glass effect 逐项问：

1. 系统组件是否本来就能完成？
2. 它是否属于 controls/navigation functional layer？
3. 是否包在 `GlassEffectContainer` 内（同屏 ≥2 个时）？
4. `glassEffect(_:in:)` 是否放在会影响外观的 modifier（`padding` / `font` / `frame`）**之后**？
5. `accessibilityReduceTransparency == true` 时是否仍可用？
6. `accessibilityShowBorders == true` 或 `colorSchemeContrast == .increased` 时结构是否更清楚？
7. 背景变化时文字和 icon 是否仍可读？
8. 是否与系统 toolbar/sidebar 形成重复材质？
9. 是否在 inactive window 下表现合理？

任何一项答不出时，优先删除或简化自定义 glass。

## Liquid Glass 专项性能验收

Apple 只给了定性约束，原文：

> Creating too many Liquid Glass effect containers and applying too many effects to views outside of containers can degrade performance. Limit the use of Liquid Glass effects onscreen at the same time.

因此验收必须自己定量。**上限数值由你（实现者）自己定义并写进交付说明，不要声称是 Apple 官方数值。**

要落地的四项：

1. **同屏自定义 glass effect 数量上限** — 数出最坏状态下同时可见的 `glassEffect` 调用数与 `NSGlassEffectView` 实例数，给出你定的上限（例：「≤ 6 个自定义 glass effect，超出即视为需要重设计」），并说明为什么这个数字对本产品成立。记录实测峰值。
2. **容器覆盖率** — 同屏 ≥2 个自定义 glass 时，是否 100% 包在同一个 `GlassEffectContainer` 内；**容器外的散装 effect 数量必须为 0**。容器数量本身也要计数并设上限。
3. **Instruments 实测** — 用 Instruments 的 **Animation Hitches** 模板（必要时叠加 Core Animation / Time Profiler）覆盖这些场景：
   - 大列表/表格滚动；
   - 连续 resize window（拖动边缘，含最小尺寸边界）；
   - 打开/关闭 sidebar 与 inspector；
   - rich content（图片/地图）上有 glass controls；
   - glass 出现/消失触发的 morph 过渡；
   - 多窗口（相关时）。

   记录：hitch ratio / hitch time、以及是否集中在 glass morph 或背景延伸区域。
4. **对照与回归** — 分别测「自定义 glass 开启」与「退化为 content surface」，确认前者没有引入可见卡顿；resize 与滚动不得出现明显掉帧。

自定义 blur/material 不应导致明显滚动或 resize 卡顿。若只是为了视觉而无法通过本节，删掉自定义 glass 是正解。

## 回归

现代化 UI 时特别检查：

- 原有菜单命令没有丢；
- keyboard shortcuts 没有冲突；
- undo/redo 仍正确；
- document dirty/save 状态正确；
- window restoration 没被破坏；
- accessibility label 没因 custom view 丢失；
- selection/focus 没因 bridge 重构发生漂移；
- 自定义 background 被删除后，原本依赖它的对比度没有崩。

## 交付格式

```text
环境
- macOS target / deployment target: ...
- OS build: ...                      # 例如 26.1 (25B78)，实测所用具体 build
- Xcode / SDK 版本: ...              # 例如 Xcode 26.1 (17B55) / macOS 26.1 SDK
- 26.x vs 27.x 双版本验证: 已做 / 未做（未做时说明原因与风险）

已验证
- Window: min / normal / large
- Light / Dark
- Keyboard navigation
- A1 Reduce Transparency -> 读取 accessibilityReduceTransparency，glass 退为不透明
- A2 Increase Contrast -> 读取 colorSchemeContrast == .increased，补描边
- A4 Show Borders -> 读取 accessibilityShowBorders（macOS 26.x 该值等于 Increase Contrast）
- Toolbar overflow / 隐藏 item 无空槽位
- 滚动边缘：scrollEdgeEffectStyle(.soft, for: .all)

性能（数值为自定义上限，非 Apple 官方数值）
- 同屏自定义 glass effect 峰值: n / 自定上限 m
- 容器外散装 effect: 0
- Instruments Animation Hitches: 场景 -> hitch ratio
- 对照（glass 开 vs 关）: 结论

未验证
- VoiceOver 实机
- macOS 27.x 上的 NSGlassEffectView.effectIsInteractive
- backgroundExtensionEffect() 的 macOS 可用性
- 多显示器

自定义 Liquid Glass
- Map floating controls：保留，系统无等价产品结构；已包入 GlassEffectContainer
- Main content cards：移除 glass，退回 content surface
```

不要把「应该没问题」写成「已验证」。
