# 完整组件覆盖矩阵

本文件定义“足够充足”的组件覆盖范围。Agent 不需要在每次任务里实现全部组件，但完整规范、设计系统或审查必须知道这些组件类别，并只选择业务实际使用的部分。

## 通用状态

适用时至少考虑：

- default
- hover
- pressed
- focus-visible
- selected / active
- disabled
- readonly
- loading / busy
- validation success / warning / error
- empty
- long-content / localization
- narrow / short viewport
- reduced motion / transparency / increased contrast

不是每个组件都需要全部状态；不要制造不存在的交互。

## 1. Actions

| 组件 | 基线 | Liquid Glass 使用 |
|---|---|---|
| Primary Button | 40–48px 高，明确主动作 | 可 tint / prominent，保持高对比 |
| Secondary Button | 40px 左右 | 普通 surface 或共享 glass group |
| Tertiary/Ghost | 不抢主动作 | 透明但必须有 hover/focus |
| Icon Button | 图标 16–20/24px，扩大 hit area | toolbar/floating controls 常用 |
| Split Button | 主动作 + 菜单 | 仅确有“默认动作+更多”语义 |
| Destructive Button | 危险语义明确 | 不因玻璃弱化危险提示 |
| Button Group | 相关命令成组 | 优先共享 glass container |

## 2. Selection

| 组件 | 要求 |
|---|---|
| Checkbox | 多选；label 可点击；indeterminate 明确 |
| Radio Group | 单选；方向键支持；组有 label |
| Switch | 即时二元设置，不用来提交表单动作 |
| Segmented Control | 2–5 个同级视图/模式；选中状态清晰 |
| Chips / Filter Tokens | 用于过滤/标签；可移除时提供名称 |
| Selection List | focus 与 selected 区分；键盘可用 |

## 3. Input

| 组件 | 要求 |
|---|---|
| Text Field | 40–44px；稳定 label；错误邻近 |
| Text Area | 支持长文本；不锁死极小高度 |
| Search Field | 明确 scope；clear；suggestion 按业务需要 |
| Password | reveal 行为可访问；不破坏密码管理器 |
| Number Input | 单位、范围、precision 清楚 |
| Select | 选项较少且固定时使用 |
| ComboBox | 允许搜索/输入的大选项集合 |
| Token Field | 多值、标签、人员等复合输入 |
| Date/Time Picker | 使用 locale；避免手写难校验格式 |
| Color Picker | 颜色不是唯一语义时补文字/HEX |
| File Picker | 系统选择 + drag/drop 可选 |

## 4. Navigation

- Toolbar
- Sidebar item / section
- Tabs（仅适用层级）
- Breadcrumb / Path bar
- Back / Forward
- Pagination
- Stepper / Wizard progress
- Tree / Outline
- Command palette（专业工具可选）

规则：一个信息层级只选主要导航模式，不堆叠多套。

## 5. Data Display

### List

- row 44–56px 起；
- 主信息、次信息、状态、操作分层；
- hover 不等于 selected；
- 大列表考虑 virtualize，但不牺牲键盘/可访问性。

### Table / Data Grid

至少考虑：

- header
- sort
- filter
- resize（需要时）
- selection
- batch actions
- pinned/frozen columns（仅有必要）
- horizontal overflow
- empty/loading/error
- long cell
- numeric alignment
- unit/precision

不因 Liquid Glass 风格把表格全部卡片化。

### Tree / Outline

- expand/collapse 可键盘操作；
- 层级缩进稳定；
- folder/leaf 状态清楚；
- selection 与 disclosure 分离。

### Cards

只在对象天然适合摘要浏览时使用；卡片不是默认数据容器。卡片内容区通常 `content-solid`，不要每张卡片 backdrop blur。

## 6. Feedback

| 组件 | 适用 |
|---|---|
| Inline validation | 字段级错误/提醒 |
| Banner | 页面级持续信息 |
| Toast | 非关键、短暂确认 |
| Alert | 必须立即决定的重要情况 |
| Progress bar | 有可靠总量 |
| Spinner / indeterminate | 无可靠总量的短等待 |
| Skeleton | 可预测结构的首次加载 |
| Status badge | 稳定状态，不只靠颜色 |

关键失败不能只靠 Toast。

## 7. Overlays

### Tooltip

- 补充解释，不放关键唯一信息；
- 键盘/触摸也能获取；
- 不用 tooltip 修复本来就应该有 label 的控件。

### Popover

- 短、上下文相关；
- 自动翻转；
- 过长内部滚动。

### Menu

- 低频命令；
- 分组；
- destructive 分离；
- shortcut 与 command 一致。

### Context Menu

- 对当前对象操作；
- 必须有替代入口。

### Modal / Sheet

- title/body/actions 三段；
- body scroll；
- focus trap；
- close 恢复 focus；
- long/short viewport 均可用。

### Drawer / Inspector

- 当前对象详情/编辑；
- 窄屏 overlay；
- 不挤坏主内容。

## 8. Search / Filter

搜索和筛选不要混成一个万能框。

Search：关键词查找、建议、recent、scope。

Filter：结构化条件，例如状态、日期、人员、类型。

大量筛选条件：

- 常用 1–3 个直接显示；
- 其余进入 filter popover/panel；
- 已激活条件可见并可一键清除；
- 不把筛选条做成十几个彩色 chip 永久占满 toolbar。

## 9. Charts

至少定义：

- title/subtitle
- axes
- series palette
- legend
- tooltip
- selection/zoom（若需要）
- missing vs zero
- loading/empty/error
- resize behavior
- data freshness

玻璃通常只用于 chart controls / tooltip，不用于绘图区本身。

## 10. Canvas / Flow / Map

需要考虑：

- zoom
- pan
- fit-to-view
- current selection
- minimap（确有必要）
- floating controls
- keyboard actions
- pointer modes
- undo/redo

用户手动 pan/zoom 后不要持续自动抢回当前节点。

## 11. File / Asset Components

- File row/card
- Upload queue
- Drag/drop zone
- Preview
- Rename
- Path display
- Conflict resolution
- Progress/error/retry

长路径 `overflow-wrap:anywhere` 或专用 path UI；不要截断后没有查看完整路径的方法。

## 12. AI / Agent Components

适用于 Chat/Agent 产品：

- Message
- Composer
- Attachment
- Tool call / action card
- Streaming state
- Retry / regenerate
- Citation / source
- Artifact preview
- Approval request
- Partial completion

规则：

- tool/action 状态真实；
- streaming 不造成整页跳动；
- 用户审批操作清晰；
- conversation 与 artifact 各自滚动时避免焦点竞争；
- 不把每条消息都做强玻璃泡泡。

## 13. Developer / Professional Components

- Code editor frame
- Diff
- Log console
- Terminal-like output
- JSON/tree viewer
- Run status
- Problems/issues list
- Resizable panel

这类区域优先高信息密度和稳定底色，Liquid Glass 只用于周边控制层。

## 14. Empty States

至少区分：

- 尚未创建
- 搜索无结果
- 筛选无结果
- 无权限
- 数据暂不可用
- 加载失败

不要用同一句“暂无数据”覆盖所有情况。

## 15. Component Density

建议三档：

- Comfortable：触屏/普通用户，44–48px 控件；
- Standard：桌面产品默认，40–44px；
- Compact：专业工具 32–36px，但扩大 hit area 并确保可访问性。

同一页面不要无规律混用三种 density。

## 16. 完整规范输出时

用户要求“完整 design system”时，至少给出：

- Actions
- Selection
- Inputs
- Navigation
- Data display
- Feedback
- Overlays
- Search/filter
- 业务特定组件

每类只展开项目实际需要的组件，不输出与任务无关的百科全书。
