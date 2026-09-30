# Accessibility 与可适应性

Liquid Glass 的视觉效果必须服从可读性、可操作性和系统偏好。Agent 不得把“保持玻璃效果”放在用户可访问性之前。

## 1. 最低要求

任何完整规范、实现或审查至少检查：

- 键盘可达
- 明确焦点
- 文字与必要图形对比度
- 不只靠颜色表达状态
- 200% 页面缩放 **与仅文字放大**（两者是不同路径，都要测）
- Reduce Motion
- Reduce Transparency（注意浏览器支持限制，见 §5）
- Increase Contrast
- 明确边界需求（例如系统 Show Borders）
- Windows 高对比 / `forced-colors`
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

"可见"必须写成可测条件：**焦点环与它内侧相邻的颜色、以及它外侧越过 offset 后的背景色，两侧对比度都要 ≥ 3:1。** 只测其中一侧是常见漏洞——在玻璃上尤其容易翻车，因为外侧背景是随时变化的合成色。

```css
:focus-visible {
  outline: var(--lg-focus-ring-width) solid var(--lg-focus-ring);
  outline-offset: var(--lg-focus-ring-offset);
  box-shadow: 0 0 0 1px var(--lg-focus-halo); /* 与玻璃之间留一条已知色的分离环 */
}
```

`outline-offset` 的作用是让环脱离元素自身边界、落在背景上；代价是环外侧对比度由背景决定。玻璃上无法保证时，用上面这种"outline + 1px `--lg-focus-halo`"双层环：内层用已知的 surface 色隔开玻璃，外层用强调色保证可见。不要用 `box-shadow` 动效单独替代 focus indicator，除非两层对比都实测过。

必须在浅色、深色、高细节图片/视频背景上各测一次，并记录实测对比度，而不是写"检查是否仍可见"。

## 4. 对比度

目标：

- 普通文字：至少 4.5:1；
- 大字（≥18.66px 粗体或 ≥24px）：至少 3:1；
- 必要 UI 边界、图标、焦点和状态图形：至少 3:1；
- **装饰性元素豁免**：`--lg-border`、`--lg-separator`、`--lg-chart-grid` 属于纯装饰分隔（实测 1.2–1.7:1），不承担 3:1 义务。一旦某个边界/线条参与读数或状态表达（输入框框、选中容器、阈值线、图表参考线），它就升级为"必要图形"，必须改用 `--lg-border-strong` 或状态色。
- disabled 可以更弱，但不能与正常状态无法区分。

玻璃的对比度必须在**真实背景**上测，而不是只看 token 之间的理论值；动态背景按最亮帧与最暗帧各测一次。

若背景变化导致不可预测：

1. 提高 glass opacity；
2. 使用 regular 而不是 clear；
3. 加局部 scrim/dimming；
4. 最后退回 solid surface。

## 5. Reduce Transparency

**先认清支持边界**：`prefers-reduced-transparency` 目前只有 Chromium 系（Chrome/Edge 119+）实现，Firefox 与 **Safari 都不支持**（WebKit 以隐私为由拒绝，见文末链接）。macOS 上 Safari 是默认浏览器，因此这个媒体查询只是增强，不是唯一降级路径。必须同时保证：

1. **无媒体查询时的实色基线**——默认状态本身就可读；
2. `prefers-contrast: more` 路径（Safari / Firefox / Chromium 均支持）；
3. 桌面壳里 macOS 系统「降低透明度」对窗口原生材质的影响（见 `references/desktop-shell-integration.md`）。

减少透明时：

- 移除 backdrop-filter；
- 使用稳定 surface；
- **同时改边框色**——白玻璃的 `--lg-edge` 是半透明白，只换背景会把白边留在白底上（对比度≈1.0，边界消失）；
- 保留边界和层级；
- 内容不能因为失去"透光"而失去分组关系。

```css
@media (prefers-reduced-transparency: reduce) {
  .lg-glass, .lg-toolbar, .lg-menu, .lg-popover, [data-material] {
    backdrop-filter: none;
    -webkit-backdrop-filter: none;
    background: var(--lg-surface);
    border-color: var(--lg-border);
  }
}
```

`@supports not (backdrop-filter: blur(1px))` 的回退同理：**背景、边框、阴影三者要一起改**，否则玻璃退化成一张看不出边界的白卡。

## 6. Increase Contrast / Show Borders

系统或用户要求更明确结构时：

- 提高 separator / border 对比；
- 选中状态增加形状、图标或明确边界；
- 自定义透明按钮补足轮廓；
- 不依赖很淡的内高光作为唯一边界；
- 原生 SwiftUI/AppKit 优先读取系统环境值并让系统组件自动适应。

```css
@media (prefers-contrast: more) {
  .lg-theme {
    --lg-separator: #7a7a85;
    --lg-edge: rgba(0, 0, 0, .28);
    --lg-border: #6e7076;
    --lg-scrim: rgba(15, 18, 24, .52);
  }
  .lg-theme[data-theme="dark"] {
    --lg-separator: #8a90a0;
    --lg-edge: rgba(255, 255, 255, .34);
    --lg-border: #9aa0ac;
    --lg-scrim: rgba(0, 0, 0, .62);
  }
}

/* Windows 高对比：让系统接管颜色，不要用 forced-color-adjust:none 保住品牌色 */
@media (forced-colors: active) {
  .lg-glass, .lg-toolbar, .lg-menu, .lg-popover, .lg-modal {
    background: Canvas;
    border: 1px solid CanvasText;
    backdrop-filter: none;
    -webkit-backdrop-filter: none;
    box-shadow: none;
  }
  .lg-primary { background: ButtonFace; color: ButtonText; border: 1px solid ButtonText; }
  :focus-visible { outline: 2px solid Highlight; box-shadow: none; }
}
```

不要为了默认主题"高级感"而阻止高对比模式产生明显变化。Show Borders 在 macOS 上是由系统驱动的边界增强：自定义控件要在有边框/无边框两条路径下都可辨认，而不是把边框烘焙成默认视觉。

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
    animation-duration: .01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: .01ms !important;
    scroll-behavior: auto !important;
  }
}
```

白名单（这些在 reduced-motion 下**保留**，因为它们承担状态反馈）：透明度变化、颜色变化、≤130ms 的边框变化。黑名单（一律关闭）：位移、缩放、弹性、视差、呼吸光、循环悬浮、背景流体动画、自动轮播。

不要全局 `animation: none !important` 破坏功能性状态；也不需要把"非必要"交给临时判断——按上面两张清单判定即可。

## 8. 文字缩放与 200%

**页面缩放（zoom）与仅文字放大（text-only zoom / 用户调大基准字号）是两条不同路径，必须分别验证。** 只测页面缩放会漏掉 macOS Safari 的最小字号设置、用户自定义 `font-size`、以及系统级文字放大。

200% 缩放后允许布局变化，不要求维持原来的"一屏三栏"。

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
- 字号锁死在极小 px（`font-size` 不要让容器高度写死，控制层高度用 `min-height` 跟随文字）；
- 用省略号隐藏关键错误、金额、状态和按钮含义。

仅文字放大的可判定验收：把根字号/浏览器最小字号调到 200%，控制层（toolbar、button、action bar）高度**随文字增长**且不裁切，`.lg-actions` 换行而不是把按钮挤出容器；表格允许横向滚动但不遮挡首列。

自动化手段（沿用项目现有测试栈，不要另建脚手架）：

- `axe-core`（或 `@axe-core/playwright`）跑对比度与语义规则；
- Lighthouse 的 accessibility 分类做回归门槛；
- Playwright `page.emulateMedia({ reducedMotion: 'reduce', forcedColors: 'active', contrast: 'more' })` 覆盖偏好路径；
- 对比度实测用取色器/脚本，不靠目视。

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

图表中相邻系列避免只用相近色区分；使用 `--lg-chart-1..5` 时同时给 marker 或 dash pattern，并保证深色主题用的是深色那一套系列值。

## 11. Target Size

桌面可以比触屏紧凑，但重要交互仍需可稳定命中。

- 常规按钮视觉高度用 `--lg-control-h-md`(40px) 起，主操作 `--lg-control-h-lg`(48px)；
- 紧凑工具栏控件可用 `--lg-control-h-sm`(32px)，但扩大 hit area；
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
- 200% 页面缩放**与仅文字放大**的结果（分别写）；
- reduce-motion / transparency 的处理，以及 Safari 等不支持该媒体查询时的降级路径；
- 高对比（`prefers-contrast`）与 forced-colors 策略；
- 实测过的对比度数值与测量位置；
- 未实测的设备/辅助技术限制。

不得用"构建通过"替代可访问性验收。

## 官方核对入口

- https://developer.apple.com/design/human-interface-guidelines/accessibility
- https://developer.apple.com/design/human-interface-guidelines/materials
- https://developer.apple.com/design/human-interface-guidelines/designing-for-macos/

`prefers-reduced-transparency` 支持现状（仅 Chromium 系）：

- https://web-platform-dx.github.io/web-features-explorer/features/prefers-reduced-transparency/
- https://github.com/WebKit/standards-positions/issues/145
- https://webkit.org/b/175497
