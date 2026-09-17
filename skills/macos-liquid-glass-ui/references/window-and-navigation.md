# Window、导航与 macOS 信息架构

本文件用于让 Agent 做出的产品不仅“像玻璃”，还符合桌面端信息架构和窗口行为。Web 实现可以视觉近似，但不要伪造没有功能的系统窗口控件。

## 1. Window Anatomy

常见桌面产品由以下区域组成：

1. Window frame / title region
2. Toolbar
3. Sidebar（可选）
4. Main content
5. Inspector / utility panel（可选）
6. Status / bottom actions（按任务需要）
7. Temporary overlays：popover、menu、sheet、dialog

不要把所有页面都做成三栏。先根据任务选择信息架构。

## 2. Toolbar

Toolbar 承载高频命令、导航、标题和搜索，不是按钮仓库。

规则：

- 控件按语义分组，通常控制在 1–3 组；
- leading：返回/前进、侧栏开关、标题等导航与定位；
- center：常用编辑或视图控制；
- trailing：搜索、分享、更多、关键动作；
- 同组内不要混入大量文字按钮和图标按钮造成视觉误读；
- 窄窗口时允许次要项进入 overflow，而不是无限缩小控件；
- 关键能力不要只存在于 toolbar；桌面产品应有可发现的替代入口，例如菜单、快捷键或上下文菜单；
- 不绘制纯装饰性的红黄绿“窗口灯”来假装原生应用。

Web 产品无法控制真实系统 toolbar 时，可以在应用窗口内部创建 toolbar-like 控制层，但应保持它是产品 UI，而不是伪造 OS chrome。

## 3. Sidebar

Sidebar 适合稳定的一级/二级导航、资料库、工作区、项目集合，不适合塞大量表单操作。

建议：

- 宽度起点 240–320px；
- 项目层级清晰，选中状态强于 hover；
- 图标统一家族，标题足够表达含义；
- 分组数量少而稳定；
- 可折叠时保留明确恢复入口；
- 搜索只在确实针对 sidebar 内容时置于 sidebar 顶部；全局搜索不要伪装成局部搜索；
- 内容可以在视觉上延伸到侧栏下方，但可读性不能依赖透明背景偶然变暗。

当窗口不足以同时容纳 sidebar 与主体时：优先收起 sidebar，而不是把主体压成不可用窄列。

## 4. Inspector

Inspector 用于编辑“当前选中对象”的属性，不用于承载全局导航。

建议：

- 260–380px 起步；
- 与当前选择强绑定；
- 无选择时显示合理空态或默认属性，不显示无意义空白框；
- 内容很长时 Inspector 自身滚动；
- 窄窗口优先变为 overlay / drawer，而不是把 main content 挤坏；
- 保存策略必须明确：即时生效、显式保存、批量应用三者不要混用。

## 5. Split View

常见模式：

- Sidebar + Detail
- List + Detail
- Sidebar + Content + Inspector
- Source + Preview
- Conversation + Artifact

Agent 需要记录每栏：

- 最小宽度
- 默认宽度
- 是否可折叠
- 是否可拖拽调整
- 哪一栏优先保留
- 哪一栏是主要滚动主体

可调整分割线应有足够指针命中区域，视觉线可以比命中区域细。

## 6. Search Placement

先判断搜索范围：

- 全局搜索：Toolbar / 主要导航层；
- 当前集合搜索：列表或 sidebar 顶部；
- 当前文档查找：文档局部 Find UI；
- 数据筛选：Filter，而不是把所有筛选条件叫 Search。

搜索需要明确 scope。可根据业务提供：

- recent searches
- suggestions
- corrections / completions
- filters / tokens
- clear history

不要同时放两个外观相同但范围不同的搜索框而不给范围提示。

## 7. Menus 与 Context Menus

菜单适合低频、补充和上下文动作。

- 最常用动作直接可见；
- 危险动作与普通动作分组；
- 互斥项使用 check / radio 语义；
- 快捷键在菜单中显示时保持一致；
- 右键菜单只包含和当前对象直接相关的动作；
- 菜单不是隐藏整个产品主要功能的地方。

上下文菜单必须有其他可访问路径；键盘用户不能因为没有右键而失去能力。

## 8. Sheet、Dialog、Popover

### Sheet / Modal

用于需要集中完成、阻断当前任务的流程：

- 新建、导入、确认关键修改；
- 标题、正文、操作独立分区；
- 正文滚动，主按钮区域稳定；
- Escape、关闭按钮、保存/放弃行为明确；
- 有未保存内容时不要静默丢失。

### Popover

用于轻量、上下文相关、可快速关闭的选择或辅助信息：

- 不承载复杂长流程；
- 自动避开视口边界；
- 内容过长时内部滚动；
- 普通 popover 不强行做完整焦点陷阱。

### Alert

只用于用户必须立即理解并做出选择的重要事件。普通成功提示不要升级成 alert。

## 9. Command Model

桌面端同一能力可以有多个入口：

- toolbar
- menu
- context menu
- keyboard shortcut
- command palette

但它们应调用同一个业务动作，不要复制出不同实现和不同状态。

常见快捷键语义尽量遵循平台习惯：

- Cmd/Ctrl + F：查找
- Cmd/Ctrl + S：保存（若产品存在显式保存）
- Cmd/Ctrl + Z / Shift+Cmd/Ctrl+Z：撤销/重做
- Cmd/Ctrl + ,：设置（原生 Mac 特别常见）

Web 产品根据浏览器冲突做适配，不抢占系统级或浏览器关键快捷键。

## 10. Selection Model

列表/表格/文件式 UI 必须明确：

- 单选还是多选；
- Cmd/Ctrl 切换选中；
- Shift 连续范围；
- 当前焦点与当前选中不是同一概念；
- 批量操作只在有合法选择时出现/启用；
- 删除后焦点和选择移动到合理位置。

不要只用背景颜色表达选中；图标、文字、焦点边界需要在高对比设置下仍然成立。

## 11. Drag & Drop

仅当拖拽能显著降低操作成本时加入：

- 文件导入
- 列表排序
- 移动节点
- 画布对象组织

要求：

- 有明确 drag handle 或足够可发现的可拖对象；
- 拖拽过程中显示落点；
- 禁止落点有清晰反馈；
- 同一动作提供非拖拽替代路径；
- 拖拽失败不能静默丢数据。

## 12. 页面导航模式选择

| 类型 | 推荐结构 |
|---|---|
| 文档/阅读 | Toolbar + content，必要时目录 sidebar |
| 知识库/文件 | Sidebar + list/detail |
| 设置 | Sidebar + form sections |
| Dashboard | Toolbar + stable content surfaces |
| IDE/Workbench | Sidebar + workspace + optional inspector |
| Chat/Agent | conversation + artifact/detail，可加 history sidebar |
| 媒体/地图 | content-first + floating glass controls |
| 管理后台 | navigation + table/form，不强行模拟 Finder |

## 13. Anti-patterns

- toolbar 塞 12 个同权重按钮；
- 页面同时有 top nav、toolbar、tab、breadcrumb、sidebar 五套主导航；
- inspector 被当成第二个 sidebar；
- 全局搜索和列表过滤长得一样、位置相邻；
- 窄窗口只缩小字体，不改变结构；
- 所有操作都藏进 `...`；
- 为了“macOS 感”伪造不能点击的窗口红黄绿按钮；
- 把移动端底部 tab bar 原样搬到宽屏桌面管理工具。

## 官方核对入口

- https://developer.apple.com/design/human-interface-guidelines/toolbars
- https://developer.apple.com/design/human-interface-guidelines/sidebars
- https://developer.apple.com/design/human-interface-guidelines/searching
- https://developer.apple.com/design/human-interface-guidelines/designing-for-macos/
