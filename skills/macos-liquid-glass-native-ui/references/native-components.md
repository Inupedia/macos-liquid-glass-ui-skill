# 原生 macOS 组件级规范：Dialog、Table 与 Selector

本文件补足 `native-structure.md` 中提到的 Sheet、Popover、Selection 的**具体组件设计合同**。只适用 SwiftUI / AppKit，优先使用系统提供的控制和材质，不把 Web 的 `--lg-*` 或 `backdrop-filter` 套进原生视图。

## 1. 组件决策表

| 任务 | SwiftUI 组件 | AppKit 组件 | 关键判断 |
|---|---|---|---|
| 编辑依附当前窗口的短任务 | `.sheet(isPresented:)` | `beginSheet` / window-attached sheet | Sheet 依附窗口，不用独立 floating panel 假装 |
| 关键确认/删除 | `.confirmationDialog` / `.alert` | `NSAlert`（适当时作为 sheet） | 危险操作明确、默认焦点不能误触危险 |
| 少量锚点设置 | `.popover` | `NSPopover` | 锚定触发器，超出空间合理关闭/退化 |
| 持续属性检查 | `.inspector` | `NSSplitViewItem(inspectorWithViewController:)` | 对应 selection，不应反复用 modal |
| 标准单选/下拉 | `Picker`（合适的 `.pickerStyle`） | `NSPopUpButton` 等 | 让系统决定菜单背景与 Glass，而非加自定义 NSVisualEffectView |
| 立即生效二元开关 | `Toggle` | `NSSwitch` | 仅二元设置，提交动作仍是 Button |
| 对象表格、排序/选中 | `Table` / `TableColumn` | `NSTableView` | 行 selection、排序、列宽与滚动均需实际检查 |
| 层级对象 | `OutlineGroup` / `List` 或系统 Outline 方案 | `NSOutlineView` | 展开与选择语义分离 |
| 输入校验 | `TextField` / `TextEditor` | `NSTextField` / `NSTextView` | 错误邻近字段、保持草稿，支持输入法与撤销 |

API 的具体 macOS availability 以用户工程目标 SDK 为准；不要依赖尚未在目标 SDK 校验的新签名。

## 2. Sheet / Alert / Popover

### Anatomy 与交互

- Sheet：清晰标题（必要时）、简短说明、独立的正文/操作区；较长正文滚动，操作和最后字段可达。重要按钮文案使用业务动词（「删除记录」而非无语义「确定」）。
- Alert：只承载需要立即决定的事；详细长内容改成任务界面，不把页面整个塞进 Alert。重要错误不能只使用自动消失 Banner/Toast。
- Popover：少量、上下文相关的字段/命令，触发器位置清晰，点击其他位置或 Esc 后不丢未保存的重要数据。
- Menu：使用标准 `Menu` / `NSMenu`；命令 enablement 与 Menu bar、Toolbar、keyboard shortcut 保持一致。
- 自定义玻璃只用于标准控件不能表达的少数功能层区域；`NSGlassEffectView` 不是 `NSPopover` 内容的默认自加背景。系统 Sheet/Popover 不二次覆玻璃。
- 检查前台 key window 与非活动 window 对控件/selection 的视觉区分。
- 多窗口时 Sheet 必须归属于触发它的窗口，不能共用一个错误的全局 isPresented 变量。

### 焦点/撤销

- 进入 Sheet 时把焦点放在首个合理字段或安全控制，打开失败不吞掉触发点。
- 取消/关闭后把焦点回到原来的对象；如果触发对象已经删除则回到有语义的替代对象。
- 未保存编辑遵守用户可预期的取消与撤销语义，不能 Esc 静默清空。
- 使用系统默认 keyboard/VoiceOver 行为，避免用不完整的自制 focus trap 干预。

## 3. Picker / Segmented / Selection

| 需求 | 推荐 | 不该做 |
|---|---|---|
| 2–5 个快速切换同级模式 | `Picker` + `.pickerStyle(.segmented)`，或标准 `NSSegmentedControl` | 把十几个长文字段强压一行 |
| 选一个固定值 | `Picker` / `NSPopUpButton` | 为了玻璃视觉写一套菜单 |
| 很多可搜索选项 | 搜索字段 + 系统 List/Popover 或成熟 AppKit 组合 | 把 Picker 强改成不完整 combobox |
| 多个独立选项 | `Toggle`/Checkbox 模式 | 把 segmented 当多选 |
| 不可选 / 只读 | 系统 enabled/disabled 与真实只读状态 | 隐去全部信息，只留灰色空位 |

- `Picker` 的 selection 用稳定标识和类型匹配的 `.tag`；选项 label 可翻译，存储值不能依赖翻译文字。
- `Table`、`List` 的选择类型事先确定：single/multiple、Cmd-click、Shift-range、方向键。`focus` 与 `selection` 并非同一状态。
- 切换选择后 Inspector 显示当前 selection；删除最后一行后 Inspector 转合适空态。
- 键盘与菜单快捷键调用**同一个 action 状态**，不能一份 UI 一份业务逻辑。
- 异步加载的候选项取消/忽略过期结果；搜索无匹配要明确显示，而不是留下过时选择结果。

## 4. Table / Outline

对每列定义：ID、标题、数据类型、min/ideal/max width、是否排序、是否隐藏/固定、长内容处理、数字单位、行操作入口。按需要定义：

- 表格宽度跟随窗口连续缩放，不把所有列永久锁成像素宽度；
- Table 与 Inspector / Sidebar 组合时给最小内容区足够空间，必要时 Inspector 可折叠；
- 行选择模型与 cmd/shift 范围符合系统使用习惯；选中和 focus 都明显；
- 排序指示与真实数据顺序一致，远程分页/筛选操作必须由稳定 row ID 保持语义；
- 批操作是可撤销还是需确认，当前页和全结果范围不得混淆；
- 加载、空数据、筛选无结果、网络失败、权限不足状态不同；
- 数字右对齐、等宽数字，长路径有访问原文方式；不为了 Liquid Glass 把 `NSTableView` 行画成玻璃卡片；
- `NSOutlineView` 的展开与当前选择需要不同交互目标。

## 5. 视觉与系统辅助

原生系统控件不硬写 Web 控件 44px 等参数或固定圆角；使用当前 SDK 构建后检查实际尺寸与排版。对真正自定义的控件检查：

- `accessibilityReduceTransparency` 为 true：内容改实色，文字/操作可读；
- `colorSchemeContrast == .increased`：必要轮廓清楚；
- `accessibilityReduceMotion`：自定义位移/morph 停止，反馈仍可见；
- `accessibilityShowBorders`：自定义互动控件边界足够明显，注意其版本语义；
- `accessibilityDifferentiateWithoutColor`：错误/成功/选中用文字或形状，不仅靠色彩；
- 动态字号、VoiceOver 名称、中文输入法、RTL、长标签、激活/非激活窗口。

## 6. 逐组件验收

1. 创建/取消/出错/保存 Sheet；切换窗口后 Sheet 仍归属正确，焦点恢复。
2. 键盘和 VoiceOver 打开 Popover/Picker；Esc 回到触发点，选项不丢。
3. Segmented 切换真实视图，长标题或缩小窗口时仍能使用。
4. Table 选择/扩展选择/排序/过滤/批操作后，Inspector 的对象同步正确。
5. 复杂表格在最小窗口宽度和 200% 字体放大时没有丢列操作入口。
6. Light/Dark、非 key window、Reduce Transparency/Contrast/Motion/Show Borders 的降级路径。
7. 报告实测 macOS build + Xcode SDK + 窗口尺寸；没做的验证不能写成「已通过」。

## 官方参考

- https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass
- https://developer.apple.com/design/human-interface-guidelines/pickers
- https://developer.apple.com/design/human-interface-guidelines/popovers
- https://developer.apple.com/design/human-interface-guidelines/designing-for-macos/
