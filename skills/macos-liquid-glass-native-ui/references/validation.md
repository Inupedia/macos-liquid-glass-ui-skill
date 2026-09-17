# 原生 macOS 验收

构建通过不等于原生体验通过。根据任务范围选择相关项验证，并在交付中区分“已验证”和“未验证”。

## 窗口矩阵

至少覆盖：

- 最小可用窗口；
- 常规窗口；
- 大窗口；
- 全屏（产品支持时）；
- Sidebar 展开/收起；
- Inspector 展开/收起；
- 多窗口（产品支持时）。

检查：

- toolbar 不挤压；
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

检查：

- Keyboard-only
- VoiceOver 语义（有条件时实测）
- Focus order
- Reduce Motion
- Reduce Transparency
- Increase Contrast
- Show Borders（目标系统支持时）
- 大字号/缩放

自定义 glass/control 是最高优先级检查对象；系统组件通常优先沿用系统行为。

## Toolbar / Commands

- 重要 toolbar action 在窄窗口 overflow 后仍可访问；
- toolbar 可隐藏/自定义时，关键命令仍有 menu/shortcut 路径；
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
- 背景 window/content 不被意外滚动或操作。

## Liquid Glass 自定义检查

对每一个手工 glass effect 逐项问：

1. 系统组件是否本来就能完成？
2. 它是否属于 controls/navigation functional layer？
3. Reduce Transparency 后是否仍可用？
4. Increase Contrast / Show Borders 后结构是否更清楚？
5. 背景变化时文字和 icon 是否仍可读？
6. 是否与系统 toolbar/sidebar 形成重复材质？
7. 是否在 inactive window 下表现合理？

任何一项答不出时，优先删除或简化自定义 glass。

## 性能

- 大列表/表格滚动；
- resize window；
- 打开/关闭 sidebar inspector；
- rich content 下 glass controls；
- 多窗口（相关时）。

自定义 blur/material 不应导致明显滚动或 resize 卡顿。

## 回归

现代化 UI 时特别检查：

- 原有菜单命令没有丢；
- keyboard shortcuts 没有冲突；
- undo/redo 仍正确；
- document dirty/save 状态正确；
- window restoration 没被破坏；
- accessibility label 没因 custom view 丢失；
- selection/focus 没因 bridge 重构发生漂移。

## 交付格式

建议：

```text
已验证
- macOS target: ...
- Window: min / normal / large
- Light/Dark
- Keyboard navigation
- Reduce Transparency
- Toolbar overflow

未验证
- VoiceOver 实机
- 多显示器
- macOS 某旧版本

自定义 Liquid Glass
- Map floating controls：保留，系统无等价产品结构
- Main content cards：移除 glass，退回 content surface
```

不要把“应该没问题”写成“已验证”。
