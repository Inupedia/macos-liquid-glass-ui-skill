# Table、Data Grid 与高密度数据组件设计

Liquid Glass 的作用是**让数据表格周边的操作层更清晰，而不是让每个单元格透明**。业务数据、网格、图表优先 content-solid。

## 1. 先分清 Table 与 Grid

| 情景 | 推荐 |
|---|---|
| 只读/可排序/含行链接的数据清单 | 原生语义 `<table>` |
| 带每个单元格编辑、方向键二维导航、范围粘贴 | 成熟 Data Grid（真实 `grid` 模式） |
| 只有标题、时间、状态的对象 | List |
| 树形层级与披露 | Tree / Outline |
| 不具备可比字段的视觉封面 | Cards |

**不要**为了「桌面感」给只读 table 强行 `role="grid"`；Grid 的方向键、编辑态、焦点漫游属于额外责任。

## 2. Anatomy

`Container`（solid）→ `Toolbar`（批操作/筛选/搜索的功能层）→ `Scroll viewport`（唯一横向滚动区）→ `Header row`（列名、排序、单位）→ `Body rows`（选择框、数据、行操作）→ `Loading/empty/error overlay`（保留结构）→ `Footer`（计数、分页或 load more）。

- 默认 row 使用 `--lg-row-h`（48px）；宽松 52px / 紧凑 44px 仅为参考。文字实际增加时可增高，**不要用固定 height 裁内容**。
- 表头可用 `--lg-surface-secondary`，body 用 `--lg-surface`；必要边界 `--lg-border-strong`，装饰分隔 `--lg-separator`。
- 表格数字右对齐，`font-variant-numeric: tabular-nums`；金额、单位、精度在列内一致，缺失值与 0 明确区分。
- 行 hover、focus、selected 是三种状态。选中不能只靠 hover，批量选择必须有真实选择控件及计数。
- 表头固定时必须测试与 body 滚动同步、列宽相同、遮挡与 box-shadow。
- 长内容优先按列类型：名称可换行；路径提供完整访问方式；数字不拆；时间保持可读且提供时区。
- 容器能水平滚动；不以缩小字体/全屏卡片化代替横向滚动。冻结列只在必要时开启，检查阴影遮挡和交互焦点。

## 3. Sort / Filter / Page / Selection 的状态合同

| 模型 | 规则 |
|---|---|
| Sorting | 显示 asc/desc/none；在**唯一已排序列**的 `<th>` 标 `aria-sort`；按钮负责触发 |
| Filtering | 独立于 Search；active filters 可见可清；改条件时一般重置页码 |
| Pagination | 页数、每页条数、总量只在可信时显示；server sort/filter/page 合同一致 |
| Selection | 使用稳定 row ID；表头 select-all 对应当前页/当前可见结果须标明作用域 |
| Batch actions | 选中后出现明确数量和操作；危险操作确认，操作后更新选择/结果 |
| Row actions | hover 才显示不行：键盘/触摸仍可达；右键不是唯一入口 |
| Async loading | 初始加载可 skeleton；后台刷新保留旧行，并标记 busy |
| Server errors | 不覆盖整个表格；保留过滤/选择/列宽并给 Retry |
| Empty | 没有记录、过滤无结果、无权限、连接失败应有不同说明 |
| Virtualization | 大数据可用成熟虚拟库；键盘、screen reader、行索引与 selection 需要额外验收 |

选择策略必须预先声明：`single` / `multi current-page` / `multi filtered-results`。远程「选择全部结果」可能包含当前没有加载的记录，必须有明确的服务器支持和取消入口，不得只凭 DOM 勾选状态假装成功。

## 4. 列定义与响应式

每个列定义至少说明：`id`、显示名、类型、对齐、排序/筛选能力、minWidth、内容溢出策略、是否隐藏/固定及优先级。状态列用文案/图标不只用颜色；操作列保留菜单入口。窄屏：

1. 保留最关键主键/对象名称和 1–2 个重要状态；
2. 其他字段可移到 row details/Inspector（不意味着每行做卡片）；
3. 复杂的数据 Grid 可选择保留局部横向滚动；
4. 保留横向滚动的提示/可达性，不能隐藏真实内容没有替代入口；
5. 在 200% 文字放大下，表头和行内容仍能读到。

## 5. 框架适配

- Element Plus `el-table`、TanStack Table、AG Grid 等只映射主题 token，不覆盖内部所有单元格样式；性能与选中模型留给原库。
- 原生 HTML table：用 `<caption>`（可视觉隐藏）、`<thead>` / `<tbody>`、`<th scope="col">`，排序按键钮。行选择用 `<input type="checkbox">` 且提供可访问 label。
- 对动态异步结果使用合适的 `aria-busy` 与非嘈杂的状态区域；不要每次刷新逐行播报。
- 原生 SwiftUI / AppKit table 使用 native skill，不把 Web CSS token 直接注入 `NSTableView`。

## 6. 可执行验收

1. 键盘操作表头排序，按升/降排序；实际数据顺序变化，`aria-sort` 正确。
2. 筛选 → 无结果 → 清除 → 内容恢复，搜索条件没有无端丢失。
3. 选择一项 → 跨页 → 返回 → 根据预定作用域保留或清除，批操作计数正确。
4. 宽窗口到 320px：操作入口可达，允许**表格内部**横滚，不出现整个页面横滚。
5. 200% 仅文字放大 + 长 CJK/英文路径：表头不遮正文，数字列不换错行。
6. 后台刷新/失败：旧内容可读，错误和重试清楚，真实状态更新。
7. Light/Dark、Reduce Transparency、keyboard-only、Screen Reader（有环境时）检查。
