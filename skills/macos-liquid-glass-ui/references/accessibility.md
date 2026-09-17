# Accessibility 与可适应性

Liquid Glass 的视觉效果必须服从可读性、可操作性和系统偏好。Agent 不得把“保持玻璃效果”放在用户可访问性之前。

## 1. 最低要求

任何完整规范、实现或审查至少检查：

- 键盘可达
- 明确焦点
- 文字与必要图形对比度
- 不只靠颜色表达状态
- 200% 文字/页面缩放
- Reduce Motion
- Reduce Transparency
- Increase Contrast
- 明确边界需求（例如系统 Show Borders）
- 屏幕阅读器可理解名称与状态
- 短屏/软键盘下操作可达

## 2. 键盘

所有核心能力必须不依赖鼠标 hover、右键或拖拽。

要求：

- Tab 顺序与视觉/任务顺序一致；
- `focus-visible` 清楚，不能为了“干净”移除 outline；
- 复合组件按其语义实现方向键等内部导航；
- Escape 关闭当前最高层可关闭浮层；
- Dialog 打开后焦点进入合理位置，关闭后回到触发点；
- 菜单、listbox、tree、tabs 不用一堆普通 div 模拟而没有键盘行为；
- 拖拽、右键菜单、hover 操作必须提供可点击/键盘替代路径。

## 3. Focus

默认建议：

```css
:focus-visible {
  outline: 3px solid var(--lg-accent);
  outline-offset: 3px;
}
```

实际实现根据背景调整。透明玻璃上必须在浅色、深色、复杂图片背景分别检查焦点是否仍可见。

不要让 box-shadow 动效完全替代 focus indicator，除非对比度和边界经过实际验证。

## 4. 对比度

目标：

- 普通文字：至少 4.5:1；
- 大字：至少 3:1；
- 必要 UI 边界、图标、焦点和状态图形：目标 3:1；
- disabled 可以更弱，但不能与正常状态无法区分。

玻璃的对比度必须在**真实背景**上测，而不是只看 token 之间的理论值。

若背景变化导致不可预测：

1. 提高 glass opacity；
2. 使用 regular 而不是 clear；
3. 加局部 scrim/dimming；
4. 最后退回 solid surface。

## 5. Reduce Transparency

减少透明时：

- 移除 backdrop-filter；
- 使用稳定 surface；
- 保留边界和层级；
- 内容不能因为失去“透光”而失去分组关系。

示例：

```css
@media (prefers-reduced-transparency: reduce) {
  .lg-glass {
    backdrop-filter: none;
    -webkit-backdrop-filter: none;
    background: var(--lg-surface);
  }
}
```

如果浏览器不支持该媒体查询，也要保证基础 fallback 可读。

## 6. Increase Contrast / Show Borders

系统或用户要求更明确结构时：

- 提高 separator / border 对比；
- 选中状态增加形状、图标或明确边界；
- 自定义透明按钮补足轮廓；
- 不依赖很淡的内高光作为唯一边界；
- 原生 SwiftUI/AppKit 优先读取系统环境值并让系统组件自动适应。

不要为了默认主题“高级感”而阻止高对比模式产生明显变化。

## 7. Reduce Motion

当用户减少动态：

- 移除非必要平移、缩放、弹性、视差；
- 保留必要的状态切换反馈；
- 不使用持续呼吸光、循环悬浮、背景流体动画；
- loading 可以保留低刺激旋转或直接使用文字/进度；
- 关键结果不能只通过动画表达。

```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    scroll-behavior: auto !important;
  }
}
```

不要全局 `animation: none !important` 破坏功能性状态；只关闭非必要动画。

## 8. 文字缩放与 200%

200% 缩放后允许布局变化，不要求维持原来的“一屏三栏”。

优先级：

1. 文本完整；
2. 操作可达；
3. 焦点可见；
4. 信息顺序正确；
5. 最后才是保持原布局。

允许：

- 三栏变两栏/单栏；
- toolbar 次要项进入 overflow；
- action row 纵向排列；
- table 自身横向滚动。

禁止：

- 整页 `transform: scale()`；
- 字号锁死在极小 px；
- 用省略号隐藏关键错误、金额、状态和按钮含义。

## 9. Screen Reader / Semantic UI

图标按钮必须有可访问名称。状态变化只播报必要摘要，不把整个页面重新读一遍。

要求：

- 表单 label 与输入关联；
- 错误通过 `aria-describedby` / 等效机制和字段关联；
- loading、expanded、selected、checked 等真实状态暴露给辅助技术；
- decorative icon 隐藏于语义树；
- data table 使用正确表格语义，不用纯 grid div 替代却不实现对应可访问行为。

## 10. Color Independence

以下状态不能只靠颜色：

- selected
- success/error
- required
- active/inactive
- chart critical threshold
- online/offline

至少同时使用文字、图标、形状、线型或位置中的一种。

图表中相邻系列避免只用相近色区分；必要时增加 marker / dash / direct label。

## 11. Target Size

桌面可以比触屏紧凑，但重要交互仍需可稳定命中。

- 常规按钮视觉高度约 40px 起；
- 紧凑工具栏控件可更小，但扩大 hit area；
- icon-only 控件不要只留下 16×16 的实际点击区域；
- 相邻危险动作与普通动作留足间隔。

## 12. Form Errors

提交失败后：

- 保留用户输入；
- 聚焦错误摘要或第一处错误；
- 每个错误靠近字段；
- 错误不只显示红边；
- 修正后及时清理过期错误；
- 异步校验避免旧请求覆盖新值。

## 13. Glass-specific QA

对每个关键 glass component 做四次检查：

1. 浅色稳定背景；
2. 深色稳定背景；
3. 高细节图片/图表背景；
4. Reduce Transparency / Increase Contrast。

如果只有场景 1 好看，材质方案未通过。

## 14. 交付检查清单

完整实现至少说明：

- 键盘检查范围；
- 焦点恢复是否验证；
- 200% 缩放结果；
- reduce-motion / transparency 的处理；
- 高对比与边界策略；
- 未实测的设备/辅助技术限制。

不得用“构建通过”替代可访问性验收。

## 官方核对入口

- https://developer.apple.com/design/human-interface-guidelines/accessibility
- https://developer.apple.com/design/human-interface-guidelines/materials
- https://developer.apple.com/design/human-interface-guidelines/designing-for-macos/
