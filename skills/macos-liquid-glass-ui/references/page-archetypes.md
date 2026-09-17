# 页面范式（Page Archetypes）

目的：降低 Agent 每次从零自由发挥导致的风格漂移。先选择最接近的页面范式，再套视觉系统、材质和组件规则。范式不是模板锁死，可以组合，但必须说明为什么组合。

## 1. Document / Reading

适合：文档、报告、知识文章、帮助中心、阅读器。

结构：

- 顶部轻 toolbar
- 可选目录 sidebar
- 中央稳定 content surface
- 可选右侧注释/属性 inspector

规则：

- 正文宽度优先 65–75ch；
- 不给每段正文做 glass card；
- 目录滚动与正文滚动关系清楚；
- 注释/目录可以玻璃化，正文保持稳定底色；
- 长文主操作不要固定遮挡内容。

## 2. Finder-style Browser

适合：文件、知识库、资产库、项目集合、数据目录。

结构：

- Sidebar：位置/集合/分类
- Main：list/grid/browser
- Detail/Inspector：当前对象详情
- Toolbar：搜索、排序、视图切换、创建

规则：

- Sidebar 是导航，不是筛选器垃圾桶；
- list/grid 的选择模型要完整；
- inspector 只描述当前选中项；
- 搜索范围必须明确；
- 批量操作只在 selection 合法时出现。

## 3. Settings

适合：系统设置、用户偏好、项目配置。

结构：

- 左侧类别 sidebar
- 右侧 form sections
- 必要时顶部 search

规则：

- 一个页面只承载相关设置；
- section 标题和说明短而明确；
- 即时生效与显式保存不要混淆；
- 高风险设置独立分组；
- 不把所有开关做成彩色玻璃胶囊。

## 4. Data Dashboard

适合：监控、经营分析、项目看板、指标展示。

结构：

- Toolbar / filters
- KPI summary
- Charts
- Table / detail

规则：

- 图表与数据使用稳定 surface；
- glass 用于 toolbar、filter、floating controls；
- KPI 卡片可轻材质，但不要每个数值都独立 blur；
- 图例、筛选、时间范围保持位置稳定；
- 空态、延迟、部分失败不能伪造“全部正常”。

## 5. IDE / Workbench

适合：代码、流程编排、AI 工具、数据实验、专业工作台。

结构：

- Sidebar：项目/历史/资源
- Workspace：主要编辑或画布
- Inspector：属性/详情
- Bottom/secondary panel：日志、输出、问题

规则：

- 主工作区最大化；
- 各窗格可独立滚动但避免滚动套滚动；
- 面板可折叠、可调宽；
- 命令可由 toolbar + menu + shortcut 共同触发；
- 日志新增时不抢用户滚动位置。

## 6. Chat / Agent

适合：对话式 AI、助手、Copilot、Agent 工作台。

结构：

- 可选 history sidebar
- Conversation
- Composer
- 可选 artifact/detail panel

规则：

- Composer 稳定可达，不因历史变长被推走；
- 消息正文不是一堆玻璃气泡，优先稳定阅读表面；
- tool call / reasoning summary / artifact 用层级区分；
- streaming 时不造成整页跳动；
- 长 artifact 与 conversation 分离时，明确哪边是主要焦点；
- error、retry、partial success 就地表达。

## 7. Media / Map / Canvas

适合：地图、照片、视频、3D、白板、流程图。

结构：

- Content-first 全幅画布
- Floating glass toolbar / control groups
- 可选 sidebar / inspector

规则：

- 这是最适合 `glass-clear` 的范式之一；
- 控件不能遮挡关键内容；
- 控件组数量少；
- 缩放、定位、播放等控制按任务分组；
- rich background 下检查 clear glass 对比度；
- 鼠标/触摸/键盘均可找到核心控制。

## 8. Form Workflow

适合：新建项目、审批、配置向导、提交任务。

结构：

- Header / progress（若确有多步）
- Form body
- Stable action area

规则：

- 主按钮位于所属流程稳定底部；
- 长表单滚动不把操作推走；
- 错误不清空输入；
- 步骤只在业务真的存在阶段时使用；
- 不为简单 5 个字段强行做 wizard；
- 短屏时允许 action area 转正常流，优先可达。

## 9. Table-centric Admin

适合：管理后台、台账、审核、运营列表。

结构：

- Navigation
- Search/filter row
- Table
- Batch actions / pagination
- Drawer/detail

规则：

- 不要为了 macOS 风格把成熟 data table 改成卡片海洋；
- 横向维度多时 table 自身横滚；
- 固定列只在确实提升任务效率时使用；
- 筛选条件多时用 filter panel/popover；
- 行内操作保留在行附近；
- 批量操作与 selection 强绑定。

## 10. Landing / Presentation

适合：产品介绍、演示页、营销型展示。

结构：

- Hero
- Feature sections
- Demo/artifact
- CTA

规则：

- 与生产工作台不同，可以更强视觉氛围；
- glass 可以用于导航和重点 demo frame；
- 不要把生产 UI 规范机械应用到营销页；
- 仍保持字体、圆角、品牌色和材质一致。

## 范式选择决策

先问：

1. 用户的主要任务是阅读、浏览、编辑、配置、监控、对话还是操作画布？
2. 主要对象是“集合”还是“当前对象”？
3. 是否需要持久导航？
4. 是否需要 Inspector？
5. 主体是自然滚动内容还是锁高工作台？
6. 哪个区域必须始终可达？

根据答案选择 1 个主范式，最多组合 1 个次范式。不要一次叠加五种布局模式。

## 范式与材质速查

| 范式 | Glass 强度 | 内容层 |
|---|---|---|
| Document | 低 | solid |
| Finder-style | 中 | solid |
| Settings | 低 | solid |
| Dashboard | 低-中 | solid |
| IDE/Workbench | 中 | solid |
| Chat/Agent | 低-中 | solid |
| Media/Map | 中-高 | rich content + floating glass |
| Form Workflow | 低 | solid |
| Table Admin | 低 | solid |
| Landing | 可适度提高 | mixed |
