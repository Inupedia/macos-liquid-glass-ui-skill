# 选择器、输入与筛选组件设计

选择器（Selector）不是一种组件。**先区分：单选/多选、是否可搜索、是否允许自由输入、选项总量、是否即时生效**，再选 Select、Picker、Combobox、Listbox、Radio、Segmented 或 Switch。

## 选型矩阵

| 情景 | 推荐 | 典型交互 | 不应做 |
|---|---|---|---|
| 2–5 个互斥同级视图 | Segmented | 点击/方向键切换当前视图 | 充当多选；长标签被裁 |
| 数个互斥表单选项，需全部可见 | Radio group | 明确组标签、单一已选 | 用 Switch 表示互斥 |
| 单一固定值，节省空间 | Native `<select>` | 平台原生菜单、键盘可选 | 自制 listbox 只为画玻璃 |
| 数量大、需要搜索、允许自由输入 | Combobox | 输入过滤、活跃选项、选中提交 | 把原生 select 改成假输入 |
| 数量大、只允许既定值 | Searchable listbox | 搜索后按选项选择；活跃项不同于选中项 | 混淆 free-text 与 selected value |
| 多个独立状态 | Checkboxes | 多个选中；部分选中时 indeterminate | 把 segmented 做成多选 |
| 立即生效二元设置 | Switch | 变化立即生效，清楚说明其对象 | 触发「删除/保存」命令 |
| 结构化过滤 | Filter panel/popover | 应用/清除条件；可见 active filters | 把所有筛选永久堆满 Toolbar |
| 日期/时间 | Native date/time input 或成熟 picker | 使用 locale、时区/范围明确 | 靠字符串猜解析 |
| 人员、标签多值 | Token field | 搜索、添加、键盘移除、完整值可读 | 一行隐藏所有 token |

这些是选型启发式，不是 Apple 官方数值。原生 SwiftUI `Picker` / AppKit `NSPopUpButton` 用 native skill 的组件规则。

## Anatomy & visual tokens

- 所有字段有**持久可见**的 label；placeholder 只是提示，不代替 label。
- 输入主体优先 `--lg-surface` / `--lg-surface-secondary`，控件高 `--lg-input-h`（44px）；紧凑场景可按 `component-matrix.md` 的 density 合同调整。
- 输入边界如承担识别功能必须用 `--lg-border-strong`，不能拿浅 `--lg-border` 充数。
- 非透明选项列表使用稳定 surface；如锚定于玻璃 Popover，外层可以 thick，**列表项自身不 blur**。
- 状态：default、hover、focus-visible、expanded、active-option、selected-value、disabled、readonly、loading、empty、invalid。
- Checkbox / Radio 维持系统语义和命中区；Segmented 在 200% 字体放大时能换行或退化为 Radio/Select。
- 字段错误紧邻字段，并用 `aria-describedby` 连接；表单失败不丢失既有输入。

## 选择模型与键盘合同

| 控件 | 重要语义 | 键盘路径 |
|---|---|---|
| `<select>` | 真实选择值，受系统实现约束 | 交给原生浏览器处理；不要用 JS 强行劫持 |
| Radio group | `fieldset` + `legend` 或成熟 primitive | Tab 进入组；箭头在组选项切换 |
| Checkbox group | 组名、每项 label；tri-state 清楚 | Space 切换勾选；indeterminate 要用真实状态 |
| Segmented | 若切换**同层视图**可按 Tabs 模式设计；若只是**提交值**更像 Radio group | 模式一旦选定要一致；自动激活仅用于切换无明显等待的视图 |
| Combobox | 明确是否 editable；`aria-expanded` / `aria-controls` / active descendant 由成熟实现维护 | Arrow 浏览、Enter 确认、Esc 关闭、打字过滤；焦点行为按 chosen pattern |
| Searchable listbox | focus 与 selected 分离；aria-selected 对齐实际选择 | Arrow、Home/End、typeahead 等由 Listbox primitive 实现 |
| Filter popover | label、已应用状态、清空入口 | Esc 恢复 Trigger；关闭前是否应用取决于 Instant/Apply 模式 |

**特别注意：** ARIA role 并不会自动实现键盘行为。采用 WAI-ARIA APG 模式或成熟无障碍组件库，不得只往 div 上写 `role="combobox"` 就宣布完成。

## 数据与异步

- 单选模型：`value: string | null`；区分「未选择」和「用户选择了字符串空值」。
- 多选模型：`values: stable-id[]`；通过 ID 保存选择，不用可翻译的 label 当主键。
- 候选项模型：`{ id, label, disabled?, description? }`；label 本地化，ID 稳定。
- Remote search：输入延迟可选、请求带 query version/AbortController；新查询覆盖旧查询，绝不能让慢请求倒写。
- 搜索为空、无结果、断网、权限不足分别说明；不可捏造「正在加载 60%」。
- 根据业务决定关闭后搜索文本是否保留；不可默认把输入的搜索词当成已选择值。
- 筛选改变后应保持其他条件，且通常把分页退回第一页；同步 URL 时要有可恢复的序列化模型。
- 模态内下拉由正确的 portal/overlay 容器托管，避免 focus 被 modal trap 阻断。

## 常见错误修复

- Select 看起来像输入框但不能打字：如果不能输入，请显示清晰的 disclosure；要搜索改 Combobox。
- Segmented 被用成十几个导航标签：压缩为侧栏/Tab/Select；优先保证完整文案。
- Filter 的 selected 只有蓝色背景：补「已选择」的文字/图标/勾选。
- 选项内容只有 hover 可读：focus 与 selected 分别拥有可见反馈。
- 只读字段灰到无法复制：readonly 保留焦点与复制；disabled 才不可操作。

## 验收

至少测试：Tab-only、箭头/Enter/Space/Esc、屏幕阅读器可访问名称、中文长选项、英文/RTL、空结果、异步响应乱序、200% 仅文字放大、modal 内打开选择器、Light/Dark、Reduce Transparency 与 High Contrast。
