# 通用组件：Actions、Navigation、Feedback、List 与 Empty States

本文件负责用户常说的「等等这些」：在 Dialog / Selector / Table 之外，补齐高频基础组件的**变体、结构、状态、语义和可执行验收**。每次按业务挑选，不强制在单页展示全部。

## 1. Actions

| Variant | Anatomy | 关键状态与行为 | 材质 |
|---|---|---|---|
| Primary button | 标签、可选前置图标、busy indicator | 一个操作区通常一个主要动作；loading 防重复，错误恢复；快捷键由业务决定 | `--lg-button` + `--lg-button-text`，不是白字叠 `--lg-accent` |
| Secondary | 标签、可选图标 | 明确取消/辅助动作；focus-visible、disabled | 实色或工具栏共享 regular 控制组 |
| Tertiary/Ghost | 标签或命令图标 | hover 与 focus 必须可见，不能只依赖背景透明 | 默认透明，必要时轻强调 |
| Destructive | 真实动词+风险上下文 | 不可逆操作二次确认；可撤销则优先提供撤销 | 使用语义危险色，不用红色玻璃装饰 |
| Icon-only | icon + 可访问名称 + Tooltip 可选 | 逻辑点击区域 ≥ 控件所需密度；不可依赖 hover 才能发现 | Toolbar 可共享 regular，内容行操作保持稳定 |
| Split button | 默认动作 + 独立 disclosure | 主按钮不会意外打开菜单；Arrow/Menu 键盘模式正确 | 共享一个组，不叠两块玻璃 |
| Button group | 相关且互斥/非互斥的控制集合 | 每个动作可见可聚焦，启用状态与命令模型一致 | 单层玻璃容器（确实需要时） |

- 宽度由文字与内边距决定，不统一钉死宽度；文案本地化后自动扩展或换行。控件使用 `--lg-control-h-sm/md/lg` 与 `--lg-radius-sm`；主操作默认 `--lg-control-h-md`，单一强调动作可用 lg。
- 禁用按钮不能成为错误解释的唯一载体，必要时就近说明为什么不能点击。
- Busy：用 `aria-busy` / 状态文案或可访问 loading 名称，不要只旋转图标；重复点击不产生重复提交。
- 操作上的成功/失败需来自真实请求结果，按钮不能在请求发送时就显示「已完成」。

## 2. Navigation

| 组件 | 适用 | 结构与状态 |
|---|---|---|
| Tabs | 同一层级的持久内容面板切换 | tablist、tab、tabpanel；selected 与 focus 区分；左右键与 tab 次序按照 APG |
| Segmented | 2–5 个同级模式/视图快捷切换 | 是否真正是 tabs/radio 必须预先定性；长文字不裁切 |
| Breadcrumb / Path bar | 表达当前位置层级、可回上级 | 当前项明确，父层为链接/命令；超长路径中间折叠但可访问 |
| Pagination | 可预期页单位的数据集合 | 当前页、总页（可信才显示）、每页数、前后可用状态；操作保留筛选条件 |
| Stepper / Wizard | 有顺序依赖的多步任务 | 当前/完成/错误/尚未开始，允许后退，数据保留；不是任意 Form 都做 Wizard |
| Sidebar item | 应用导航/集合选择 | 图标可选、文字、可选计数/状态；focus 与 selected 不混淆 |
| Tree / Outline | 可展开层级对象 | Disclosure 与 row selection 独立；Arrow 展开/折叠、层级可读 |
| Search field | 关键词查找 | scope、clear、empty、suggestions、loading、error；不与结构化 Filter 混为一谈 |

导航尽量只保留一个主要模式；Tabs 和 Sidebar 不应重复导航同一级集合。横向空间不够时重新组织层级，不能缩小到无法点选。

## 3. Feedback

| Variant | 什么时候用 | 视觉/生命周期要求 |
|---|---|---|
| Inline error/help | 字段本地校验、权限原因 | 就近于字段，文案+必要标识；`aria-describedby` / `aria-invalid` |
| Banner | 需要持续阅读的页面级信息 | 明确标题/行动/关闭语义，可跨操作持续 |
| Toast | 非关键短暂确认 | 不替代重要失败；可访问 live region；不可被焦点遮挡 |
| Alert | 需立即处理的重要确认 | 使用 `overlays-and-dialog-components.md`，危险操作不能点击遮罩执行 |
| Progress determinate | 真实可计算百分比/单位 | 明确当前值/总量，不捏造进度 |
| Spinner indeterminate | 时长未知且确实等待 | 不虚构百分比；任务长时提供可取消/离开策略 |
| Skeleton | 初次结构可预测 | 只用于首次加载，不在每次后台刷新清空既有内容 |
| Status badge | 稳定状态 | 文案/图标+语义色；不可只红绿小圆点 |
| Empty state | 区分不同缺失原因 | 合理解释 + 下一步，不用同一「暂无数据」覆盖所有情况 |

Toast 处理后的真实数据变化仍需同步到内容区；辅助播报简洁，不要每秒大量重复播报。

## 4. Lists、Cards、File rows

- **List row**：主标题、必要副标题、状态和可操作区；hover、active、selected、focus 四态分开。行内按钮必须不触发整行导航；在触控设备上不能藏到 hover-only。
- **Card**：只用于天然适合摘要或媒体浏览的对象。主体用 `content-solid`，状态、CTA 和内容层级清晰；卡片可选择后不是整个卡都 blur。
- **File row**：类型/文件名/路径/状态/操作分层，提供完整路径阅读方式，支持冲突命名、上传失败重试和进度真实展示。
- **Upload dropzone**：拖入区域可见，键盘/文件选择有等效入口，上传排队/校验/失败/取消清楚，不只依赖拖放。
- **Tree row**：Disclosure 的 click target 与 row select 分开，完整的层级关系对屏幕阅读器可达。
- **Long content**：换行、截断与访问完整值是一个整体合同；不能用 `text-overflow:ellipsis` 抹掉必须知道的信息。

## 5. 状态-事件-结果最小表

| 事件 | 预期视觉 | 预期业务结果 | 校验 |
|---|---|---|---|
| Tab 到 icon button | focus ring + 可访问名称 | 不会执行 action | keyboard-only |
| 激活危险操作 | 清楚风险 + 明确确认入口 | Cancel 无副作用 | 不点鼠标完成取消 |
| 后台刷新 | 旧内容仍可读 + 刷新信号 | 成功/失败状态更新 | 断网/慢请求 |
| 文件上传失败 | 每项错误 + retry | 不损坏已成功文件 | 批量部分成功 |
| 进入列表空态 | 按原因给文案/入口 | 保留可复原的筛选/权限信息 | 筛选无结果 ≠ 无权限 |
| 窄窗口/文字放大 | 内容换行，操作区域可到达 | 真实命令仍可执行 | 320×568 + 仅文字 200% |
| Reduce preferences | 实色、明确边界、静态反馈 | 所有可操作能力保留 | reduced motion/transparency/contrast |

## 6. 实施边界

Web 组件的无障碍 keyboard/focus/portal 优先复用原项目的 Radix / Headless / Ark / Element Plus 等库，样式通过现有 token 适配。原生 SwiftUI/AppKit 始终由系统 Button、List、Table、Menu、Sheet、Picker 优先承载，不引入本文件的 CSS 数值。

完成设计后，至少提交各组件的 Variant、Anatomy、响应状态、材质/Token 归属、键盘路径、失败回退和一条可复现实测场景；没有实际测试则说明未验证。
