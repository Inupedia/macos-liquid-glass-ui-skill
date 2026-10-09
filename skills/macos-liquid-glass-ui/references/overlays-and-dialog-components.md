# 弹窗、Sheet、Popover 与 Menu 的组件设计

本文件是 Web / Electron / Tauri Web 内容的设计合同；原生 macOS 通过系统 `Sheet` / `Popover` / `NSAlert` 实现，见 native skill。

## 选型决策

| Variant | 场景 | 关闭规则 | 焦点 | 材质 |
|---|---|---|---|---|
| Alert dialog | 重要确认、危险决定 | 不允许外部点击静默关闭；取消/确认可见 | 打开后转入 alert；关闭还原 | 可读的实色正文、外层 thick |
| Modal dialog / Sheet-like | 中短表单、一次任务 | Esc 可按业务取消；有脏数据需确认 | 限制在 modal 内 | 外壳 thick，长正文 solid |
| Non-modal dialog | 辅助浮窗、需要并行查看 | 可与背景交互 | 不设 modal trap | regular/thick 按位置 |
| Popover | 与触发器锚定的少量轻操作 | 外点/Esc，一般不含危险未保存内容 | 通常不 trap | thick；选项正文清晰 |
| Menu / Context menu | 低频对象命令 | 选择后关闭；Esc；外点 | 方向键/typeahead | thick，行内无逐项玻璃 |
| Tooltip | 简短补充信息 | hover/focus 触发，不可作为唯一标签 | 不抢焦点 | 对比达标的单层表面 |
| Inspector/Drawer | 当前对象长期属性 | 明确可关闭与窄屏 overlay 模式 | 非 modal 时不 trap | 内容 solid，壳按需 regular |

**优先级**：操作是否阻塞 > 内容量 > 是否有锚点 > 用户是否需要同时操作背景。不要因为动画好看把所有组件都做成 modal。

## Dialog anatomy

`Overlay`（遮罩、屏蔽背景） / `Surface`（可读内容容器） / `Header`（名称和可选关闭按钮） / `Body`（唯一主滚动主体） / `Footer`（明确取消及主要操作） / `Error region`（提交/权限/网络错误靠近操作） / `Busy state`。

- 常规 Web modal 宽度 480–640px，最大宽度 `calc(100vw - 32px)`，高度起点 `min(80dvh,760px)`；这是建议起点，不是写死所有变体。
- 标题不会被 body 滚走；短屏底栏按 `layout-and-scroll.md` 退为文档流或 dialog 内可滚，不压住最后一个输入。
- 表单字段保留 label、helper、error；Footer 按语义分组并预留本地化换行空间，危险动作与安全取消清晰区分。
- 内容很短时不要为了「风格」加入巨大空白；复杂长期工作应变为独立页面或 Inspector。
- 不支持 Esc/关闭按钮时，明确说明任务原因并提供等效取消或退出路径，不能把用户困住。

## 交互与状态合同

| 事件 | Modal / Alert | Popover / Menu |
|---|---|---|
| 打开 | 记录触发点、标题有可访问名称、合适初始焦点 | 关联触发器；`aria-expanded` 反映状态 |
| Tab / Shift+Tab | 焦点限制在当前 modal；使用成熟 dialog primitive 或原生 `showModal()` | 顺序符合类型；menu 用方向键、listbox 用选项键盘模式 |
| Enter | 只有有明确默认动作时才提交；文本区域不误触 | 选择高亮项/执行命令 |
| Escape | 关闭最上层；脏表单需确认，不直接丢失 | 关闭最上层且还原到 trigger |
| 外部点击 | Alert 不自动取消；一般 Modal 根据数据丢失策略 | 非模态浮层可关闭 |
| 异步提交 | 按钮 busy、防重入；失败保留用户输入与错误 | 保留选中与搜索条件；可展示局部错误 |
| 关闭 | 解锁背景滚动；恢复触发点焦点（触发器已删除则返回逻辑替代点） | 还原 trigger，清理浮层监听 |
| 重开 | 草稿是否持久化由业务定义，不得意外复用上一次错误 | 按语义初始化高亮项和滚动位置 |

## 层级、定位与滚动

- 用 `--lg-z-menu`、`--lg-z-drawer`、`--lg-z-modal`、`--lg-z-toast`，不新造散落的 9999 层。
- 浮层由触发器 anchor 定位；靠边自动 flip/shift，宽高不越 viewport。动态重新定位要考虑缩放、滚动、resize。
- Modal 内部 Select/Menu 必须显示在 modal 交互层内，或者由所用 dialog/portal primitive 正确管理；不能跳到不可聚焦的背景层。
- Portal 不解决 focus/scroll/body-lock 所有问题。叠多层 dialog 前先审视任务设计是否过度。
- 触摸模式不能仅依赖 hover Tooltip；必要说明放在正文或帮助按钮中。
- 页级 Toast 不替代 Modal 提交错误，尤其权限、验证、危险冲突错误。

## 实现建议

- 原生 Web `<dialog>` + `showModal()` 适合较简单的 modal：自带 top layer 与 modal 焦点限制；仍需亲自处理初始焦点、cancel/脏数据、关闭后焦点、滚动与表单失败。
- Headless UI、Radix、Ark、Element Plus、shadcn-vue 已提供 focus/portal 键盘行为时直接复用；不要重写 `role=dialog` 假装具有完整模态语义。
- 仅给一层有材质的浮层外壳；正文、复杂表单、下拉列表不要 glass-on-glass。降低透明度/强制高对比时应变成稳定实色。
- 动画：用 `--lg-dur-panel` 为默认 Web 过渡上限基线；Reduce Motion 时直接出现，不做大幅缩放或飞入。

## 可执行验收

1. 仅用键盘打开 → 阅读标题和内容 → Tab/Shift+Tab → Esc 关闭 → 焦点回到触发器。
2. Modal 中打开 Select：选项可见、可键盘选择、不会被 modal 遮罩挡住。
3. 在 320×568 和 200% **仅文字放大** 下显示长字段错误：Footer 和最后一个字段都可达。
4. 危险确认：点击遮罩不删除数据；按 Cancel 不执行；成功后状态真实更新。
5. 脏数据状态：Esc 或关闭先提示保存/丢弃，不静默清除输入。
6. Reduced Transparency / forced-colors / 明暗主题下标题、边界、焦点与按钮可辨。
7. 打开 Popover 后滚动页面、调整窗口和 RTL：锚点正确，不出现页面横滚。
