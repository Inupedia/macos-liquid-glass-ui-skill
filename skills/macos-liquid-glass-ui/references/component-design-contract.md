# 组件级设计合同（Agent 必须执行）

这是从「组件覆盖清单」走向「可以实施的设计系统」的入口。`component-matrix.md` 负责列全类别，本文件负责**选型 → 解剖 → 状态 → 行为 → 验收**。用户说「设计弹窗/表格/selector」时，不得仅枚举组件名称。

## 1. 先做选型，不要先画一张玻璃卡片

对每个真实使用的组件，输出如下合同，并结合现有组件库实现：

| 必填项 | 需要回答的问题 |
|---|---|
| 任务 | 谁在什么位置，为完成什么动作使用它？ |
| Variant | 使用哪个具体模式，为什么不使用另外两种？ |
| Anatomy | Trigger、Label、Description、Body、Footer、Error、Empty 等实际存在的部位 |
| 尺寸/密度 | 使用哪些 `--lg-*` tokens，最小宽度、长文、短屏怎么退化？ |
| Material | `content-solid` / `glass-regular` / `glass-thick`；内容层与浮层不能混淆 |
| State | default、hover、focus-visible、selected、disabled、loading、invalid、empty 等**实际可触发**的状态 |
| Behavior | 点击、键盘、Escape、外部点击、滚动、提交、取消、焦点恢复 |
| Data | controlled / uncontrolled；异步取消、提交去重、错误恢复、选择是否保留 |
| Access | 可访问名称、描述、语义、对比、仅文字放大、RTL |
| Verify | 一个可以执行的场景 + 预期结果，不能只写「应良好」 |

输出规范时以「组件名 + Variant + anatomy + token + 交互状态 + 验收」为最低粒度；做项目时只实施实际出现的组件。

## 2. 选型速查

| 目标 | 优先选用 | 不推荐 |
|---|---|---|
| 立即确认不可逆危险动作 | Alert / confirmation dialog | 非阻塞 Toast、靠颜色示警 |
| 编辑当前窗口中的短任务 | Modal/Sheet；原生 macOS 优先系统 Sheet | 三层嵌套 modal |
| 附近的少量临时设置 | Popover | 占满页面的复杂模态 |
| 当前对象长期查看/修改 | Inspector / Drawer | 无端反复开关 modal |
| 三五个互斥的同层视图 | Segmented control | 多级下拉、伪 Tab 导航 |
| 固定值单选，空间紧张 | Native Select / Picker | 手写 combobox |
| 大量选项可搜索/自由输入 | Combobox | 显示数百项的简单下拉 |
| 多个独立开关 | Checkbox group | 使用 segmented control 假装多选 |
| 立即生效的二元设置 | Switch | 一次性确认、提交操作 |
| 可比较字段/排序/批量选择 | Table / Data Grid | 每行做玻璃卡片 |
| 标题+描述为主的对象浏览 | List / Cards | 复杂的假表格 |
| 层级树结构 | Tree / Outline | 伪装成缩进文本的普通 table |

**注意：** Web 的 `<select>` 与原生 macOS 的 `Picker` 不是同一实现；只借鉴语义，不强行复制平台像素。

## 3. Material × 组件

- `content-solid`：Table、grid body、form fields、编辑器、长内容、日期文本域、列表主内容。表头可用不透明 secondary surface；不要对每一行 blur。
- `glass-regular`：Toolbar、Sidebar、悬浮控件组（根据页面背景与性能）。
- `glass-thick`：短 Popover、Menu 与轻量浮层的**外层壳**；长列表、嵌套表单或选项列表的阅读表面仍要可读的实色。
- `glass-clear`：只在 rich media 上少数控制，并通过 `materials-and-optics.md` 对比度判定。不是弹窗默认值。
- 原生 SwiftUI/AppKit：系统已经处理的控件/浮层**不加** Web 玻璃配方；转 `macos-liquid-glass-native-ui`。

所有尺寸均为本仓库 Web 设计基线，非 Apple 官方像素规范；不得为不同组件另立一套随意数字。

## 4. 关键可见状态

| 状态 | 视觉 | 行为 |
|---|---|---|
| Hover | 小幅背景或边框变化 | 不触发选中，不代替 focus |
| Focus-visible | `--lg-focus-ring` + halo，双侧可见 | 键盘次序逻辑正确 |
| Pressed | 短暂反馈，不让文字跳动 | 不提前宣称异步成功 |
| Selected | 文字/图标/勾选显式识别；可使用 `--lg-accent-soft` | 焦点与选中分别建模 |
| Disabled | 仍可辨认文本；说明原因 | 不可提交，非只靠透明度 |
| Readonly | 可复制、可查看完整值 | 不混同 disabled |
| Loading | 显式 `aria-busy` 或状态文字 | 防重复操作；保留既有内容 |
| Empty | 区分首次/筛选/权限/错误 | 提供可用的下一步 |
| Error | 临近字段或表格错误区 | 保留输入、筛选与已选中项 |
| Long/localized | 换行、可滚动 | 不裁切 footer 和表头 |
| Reduce preferences | 实色、高对比、少位移动画 | 不损失任何必需操作 |

## 5. 合同示例

**「为数据列表做一个状态选择器」不等于只写一个下拉框。**

- 业务：按状态过滤表格；筛选不是改变记录本身。
- Variant：有限状态，单选时 Native Select；多条件则带复选项的 Filter Popover。
- Anatomy：可见标签、当前值、清空、有效条件摘要、筛选结果计数。
- Data：受控过滤状态；更改条件时重置页码，不重置其他筛选；URL/历史是否同步依产品要求。
- Behavior：键盘可打开与选择；Popover Esc 关闭并恢复触发器焦点；对异步查询取消过期响应。
- Material：控件实色，Popover 外壳可 thick，表格 content-solid。
- Verify：键盘选择 → 数据过滤 → 空结果 → 清除过滤 → 回到完整列表，过程中不丢焦点、不编造记录。

## 6. 精读路由

- 选择器、字段与过滤：`references/selection-and-input-components.md`
- Sheet / Dialog / Popover / Menu：`references/overlays-and-dialog-components.md`
- Table / Grid / 行选择 / 批操作：`references/tables-and-data-components.md`
- 现成的样式示例：`assets/component-recipes.css` + `assets/component-showcase.html`。示例只演示视觉与基础原生交互，不代替成熟 headless 组件库。
- 原生 macOS 组件对应关系：使用 native skill 的 `references/native-components.md`。

## 7. 交付验收

组件设计交付至少包括：使用的 variants、关键截图/结构（如环境支持）、材质归属、未覆盖的状态、键盘路径、实际测过的浏览器/系统及尚未验证的条件。不要把「文档写了」当成「交互跑过」。
