# 国际化排版与文字系统

> 适用范围：Web / 跨端视觉近似。本文件只管「文字怎么排」：语言与字体栈、中西文混排、CJK 断行、逻辑属性与 RTL、数字与字距、仅文字缩放、文字相关动效。不重复色板与材质（见 `visual-system.md`、`materials-and-optics.md`），不改动 `assets/foundation.css` 中的任何 token 值。

## 1. 语言与字体栈

`lang` 不是注释，是排版前提。三件事只在 `lang` 正确时成立：

1. **字形选择**：汉字被中日韩共用，同一码位在不同语言下取不同字形（`直`、`骨`、`今`）。`lang="zh-Hans"` 取简体字形，`lang="zh-Hant"` 取繁体字形，`lang="ja"` 取日文字形。不给或给错，浏览器按系统语言兜底 → 中文页出现日式汉字或繁体字形。
2. **断行规则**：`line-break`、`hyphens` 与断词字典都按语言生效。`hyphens: auto` 在无 `lang` 的元素上不产生任何连字符（这是「`hyphens` 失效」的常见原因）。
3. **中西文间距**：`text-autospace`、`text-spacing-trim` 需要语言标记来判定 CJK 上下文。

```html
<html lang="zh-Hans">   <!-- 简体；繁体用 lang="zh-Hant"，日文用 lang="ja" -->
<p lang="zh-Hans">中文段落…</p>   <!-- 局部混排逐段标语言，不靠继承 -->
<span lang="ja">日本語の語句</span>
```

字体栈只改动**主字体**，基础栈必须与 `foundation.css` 的 `--lg-font` 逐字一致，不得改写：

```
--lg-font: -apple-system, BlinkMacSystemFont, "SF Pro Display", "SF Pro Text",
  "PingFang SC", "Helvetica Neue", "Segoe UI", sans-serif;
```

```css
/* 只改主字体，基础栈（= --lg-font）保持一致 */
:where([lang="zh-Hant"]) { font-family: "PingFang TC", "Heiti TC", var(--lg-font); }
:where([lang="ja"])      { font-family: "Hiragino Sans", "Hiragino Kaku Gothic ProN", "Yu Gothic", var(--lg-font); }
:where([lang="ko"])      { font-family: "Apple SD Gothic Neo", "Malgun Gothic", var(--lg-font); }
/* Linux/Android 兜底：在 --lg-font 末尾追加 "Noto Sans CJK SC"，仍保留 sans-serif */
/* 简体中文直接沿用 var(--lg-font)，它已含 "PingFang SC" */
```

规则：CJK 字体排在拉丁系统字体之后、`sans-serif` 之前；不下载分发 Apple 字体；不把 `"PingFang SC"` 放到 `-apple-system` 之前（会让 macOS 失去 SF 拉丁字形）；不为「多语言」把多套 CJK 主字体堆进同一份 `font-family`（中文 Windows 上会先命中日文字体）。

## 2. 中西文混排

中西文之间那点空隙由**排版引擎**负责，不由 `letter-spacing` 负责。禁止用全局 `letter-spacing: 0.02em` 造间距：它同时拉大拉丁词内与中文字内间距，中文会松散。`text-autospace` 与 `letter-spacing` / `word-spacing` 是**叠加**关系，已用字距微调标题时再开 `text-autospace` 会得到双份间距。

| 特性 | 已核实现状 |
|---|---|
| `text-autospace` | Firefox 145+（2025-11）、Safari 27+（2026-09）；**Chrome / Edge 尚未实现**（Chromium bug 429178779） |
| `text-spacing-trim` | Chrome / Edge 123+（2024-03）；**Firefox 未实现**（性能顾虑）、**Safari 未实现**（WebKit bug 252068） |

两者互补但不重叠，**都不能当唯一样式**：中日文产品靠 `text-spacing-trim: space-first` 收窄全角标点（仅 Chromium 生效），中英混排密集处靠 `text-autospace: normal`（仅 Firefox / Safari 生效）。不支持时**什么都不做**就是正确降级，不要改用 `letter-spacing` 补。

```css
/* 可全文尝试的排版增强：只做增强，不承担必备视觉 */
.lg-theme {
  text-spacing-trim: space-first; /* 可降级：不支持则忽略 */
  text-autospace: normal;         /* 可降级：不支持则忽略 */
}
```

若视觉必须收窄标点留白（例：窄侧栏中文列表），只能在局部用 `-webkit-text-stroke: 0.01em` 这类取巧手段并逐个视口验证；该属性无 MDN 标准页面（见「未确证项」），默认不采用。

行高：汉字是满字身方形，拉丁小写有 x-height 与升降部，同样行高下中文更挤。

| 文字 | 行高 |
|---|---|
| 纯中文正文 | **1.6–1.75**；`--lg-leading-body: 1.6` 已在区间下沿，长文可到 1.7 |
| 中西混排正文 | 1.6（不为拉丁单独减小） |
| 拉丁为主短文案 / 标题 | 1.3–1.45，即 `--lg-leading-section: 1.35`、`--lg-leading-card-title: 1.4` |
| 展示与数值 | 1.15，即 `--lg-leading-display` / `--lg-leading-metric`，中英一致 |

**只允许把中文正文行高往上调，不允许按中文把标题行高往下压。** 行高一律写 `var(--lg-leading-*)`，不写裸数字。

## 3. CJK 断行

```css
/* 三者职责互不重叠；只在正文区域开启，避免影响控制层 */
.lg-theme p, .lg-theme li, .lg-theme td, .lg-theme .lg-card-title {
  line-break: strict;      /* 标点禁则：不允许「。」「、」「）」出现在行首 */
  word-break: normal;      /* 中文无空格即可断行，这是默认行为，不要改 */
  overflow-wrap: anywhere; /* 只兜底超长不可断 token：URL、订单号、连续 ASCII */
}
.lg-actions, .lg-toolbar, .lg-sidebar { overflow-wrap: normal; }
```

- 中文无空格断行是默认行为，`word-break: normal` 即正确；禁止 `break-all`（会在拉丁单词中间断开，并让标点禁则失效）。
- **禁止对中文用 `hyphens: auto`**：中文不靠连字符断词。`hyphens` 只对设有正确 `lang` 的西文有意义。
- 避头尾由 `line-break: strict` 负责，已全平台可用；不要用 `text-wrap` 代替它。
- `text-wrap: balance` 只用于 1–2 行标题（可降级）；`text-wrap: pretty` 支持面窄（Chrome 117+、Safari 26+，Firefox 未实现），**不得作为唯一手段**。

```css
.lg-page-title, .lg-card-title {
  text-wrap: balance;      /* 不支持时退化为普通换行 */
  max-inline-size: 28ch;   /* 中文标题宽度上限，避免单行过长 */
}
.lg-metric, .lg-metric-unit, .lg-time, .lg-range { white-space: nowrap; } /* 短 token 不断行 */
```

`white-space: nowrap` 的风险：进 flex 容器不收缩（须配 `min-width: 0`），长文本会整段溢出。**只用于 1 行以内的数值/单位 token**；正文、表格单元格、说明文字禁止使用。单位与数字之间用 `&nbsp;` 或 `<span class="lg-metric-unit">` 包裹，不要靠 `nowrap` 兜全文。

## 4. 逻辑属性与 RTL

`foundation.css` 已用 `padding-inline` / `border-block-start`。凡有方向含义的物理属性一律换成逻辑属性，`dir="rtl"` 下才能自动镜像。

| 物理属性 | 逻辑属性 |
|---|---|
| `padding-left` / `padding-right` | `padding-inline-start` / `padding-inline-end` |
| `padding-top` / `padding-bottom` | `padding-block-start` / `padding-block-end` |
| `margin-left` / `margin-right`（含 `margin-left: auto`） | `margin-inline-start` / `margin-inline-end` |
| `border-left` / `border-right` | `border-inline-start` / `border-inline-end` |
| `border-top` / `border-bottom`（含工具栏分隔线） | `border-block-start` / `border-block-end` |
| `left` / `right` | `inset-inline-start` / `inset-inline-end` |
| `top` / `bottom` | `inset-block-start` / `inset-block-end` |
| `width` / `height` | `inline-size` / `block-size` |
| `text-align: left` / `right` | `text-align: start` / `end` |
| `float: left` / `right` | `float: inline-start` / `inline-end` |

支持（已核实）：`border-block-start` Safari 12.1+ 即可用；`padding-inline` / `inset-inline-start` 需 Safari 14.1+、Chrome/Edge 87+、Firefox 63–66+。即 **Safari 12.1–14.0 只有部分逻辑属性**——产品若必须覆盖这一段，用 PostCSS 逻辑属性降级插件转物理属性，不要手写两套。方向标记写在 `<html dir="rtl" lang="ar">`；局部反向内容用 `<bdi>` 或 `dir="auto"` 包住，不要对整个页面 `transform`。

### Glass 控制层在 RTL 下会坏在哪里

1. **主按钮位置**：`.lg-actions` 用 `justify-content: flex-end`。flex 的 `end` 是主轴终点，RTL 下自动指向左侧 —— 这是**正确**的，主按钮跟随阅读方向。真正会坏的是 `margin-left: auto`、`right: 0`、`order: -1` 这类硬编码。
2. **图标方向**：chevron、返回/前进箭头、`⇧` 类方向指示**必须镜像**（`transform: scaleX(-1)`）；播放/暂停、时钟、相机等媒体控制图标**不镜像**。用 `dir` 选择器统一处理，不要逐个图标加 class，并同步检查 `aria-label` 语义（写「上一页」而不是「左箭头」）。
3. **滚动条位置**：跟随 inline 方向，RTL 下到左侧。不要用 `direction: ltr` 强行固定滚动条位置（会连带改掉内容方向），也不要凭猜测加 `scrollbar-gutter` 补偿。
4. **阴影方向**：`--lg-shadow-*` 的 X 偏移为 0，RTL 下无需调整。若某处用了非零 X 偏移，必须 `[dir="rtl"] { box-shadow: <X 取反> }`，否则光从反方向来。
5. **`outline-offset`**：`outline` 向四周均等扩展，与方向无关；不要改成只加单边的 `border`。

```css
/* .lg-actions 的 RTL 正确处理：保住逻辑属性即可，无需 RTL 分支 */
.lg-actions {
  justify-content: flex-end;         /* 方向无关：RTL 下自动到左侧 */
  padding-inline: var(--lg-space-5); /* 不要写 padding-left/right */
  border-block-start: 1px solid var(--lg-separator);
}
[dir="rtl"] .lg-icon-directional { transform: scaleX(-1); } /* 仅方向指示类图标 */
/* 反例：.lg-actions { margin-left: auto } / .lg-primary { order: -1 } */
```

## 5. 数字、字距与等宽

`font-variant-numeric: tabular-nums` 与 `font-feature-settings: "tnum" 1` **同时写**，在保留小数、负号、千分位与 `%` 的前提下把数字变等宽。直接复用 `foundation.css` 已有的 `.lg-num` / `.lg-tabular`（两者实现相同），不另建类名。适用选择器必须逐项确认，不做全局：

| 场景 | 选择器 | 原因 |
|---|---|---|
| 表格数字列 | `.lg-table td.lg-num`、`th[data-numeric]` | 列对齐 |
| KPI / 指标卡 | `.lg-metric`、`.lg-kpi` | 值更新时宽度不跳 |
| 时间、时长、倒计时 | `.lg-time`、`.lg-duration` | 秒数跳动不抖动 |
| 金额、百分比、用量 | `.lg-amount`、`.lg-percent`、`.lg-usage` | 右对齐比较 |
| 代码、ID、日志 | `.lg-code`、`.lg-token` | 配合等宽字族 |

**不适用**：大号展示数值（`--lg-text-display` / `--lg-text-metric`）用 `--lg-font` 默认的比例数字更接近 macOS 观感。判据是「是否需要跨行 / 跨刷新对齐」，不是「是否是数字」。

中文标点与半角数字混排：全角 `，。：` 与半角数字的字面宽度差异是正常的，**不要为「看起来一致」把数字改成全角**，也不要手动插 `&nbsp;` 造间距（引擎负责，`text-autospace` 生效时自动补位）。金额、版本号、序列号一律半角。

```css
/* 字距工具类：只给拉丁元素用，绝不放在 .lg-theme 根上 */
.lg-caps { text-transform: uppercase; letter-spacing: 0.06em; font-weight: var(--lg-weight-semibold); }
.lg-theme :lang(zh-Hans), .lg-theme :lang(zh-Hant), .lg-theme :lang(ja), .lg-theme :lang(ko) {
  letter-spacing: normal; /* 兜底：任何全局字距都不作用于 CJK */
}
```

`letter-spacing` 建议值：全大写拉丁小标题 `0.04em–0.08em`；全大写按钮文案 `0.02em`；常规拉丁正文 `0`（不要负字距）；≥32px 的大号拉丁展示标题 `-0.01em ~ -0.02em`；**中文/CJK 任意字号一律 `0`**，禁止为「紧凑」设负字距。

## 6. 文字缩放（不是整页缩放）

浏览器「仅缩放文字」、用户自定义默认/最小字号、系统文字放大**都不会触发媒体查询**，但会放大文字。而 `foundation.css` 的尺寸 token 是 px 字面量（`--lg-control-h-md: 40px`、`--lg-text-body: 15px`）：px 字号不响应根字号，px 高度不响应文字尺寸，文字放大到 200% 时控件仍是 40px 高、按钮文字被裁切。本节的职责就是给出换算策略。

策略：token 保持 px（设计基线的唯一定义源），在**使用处**换算。

- 根字号 16px 时：`15px = 0.9375rem`、`13px = 0.8125rem`、`17px = 1.0625rem`、`32px = 2rem`、`48px = 3rem`。
- 需要跟随「仅文字缩放」的**高度与内边距用 `em`**（以自身字号为基准），它随父级 `font-size` 变化；`rem` 只随根字号变化，对「仅缩放文字」响应较弱。
- 字号只写一次并全部走 `var(--lg-text-*)`，组件内不再写 px 字号。
- **可以继续用 px 的场合**：不承载文字的装饰尺寸 —— `--lg-blur-*`、`--lg-shadow-*` 的偏移与模糊半径。

```css
/* 文字放大安全：值仍是设计基线，但随文字增长 */
.lg-primary {
  font-size: var(--lg-text-button);      /* 不写 px */
  line-height: var(--lg-leading-button); /* 1.3，无单位 */
  min-height: 2.75em;                    /* 原 40px ÷ 15px = 2.667em，取 2.75em 留弹性 */
  padding-block: var(--lg-space-2);
  padding-inline: var(--lg-space-5);
}
.lg-toolbar { min-height: 3.2em; padding-block: var(--lg-space-2); } /* 48px ÷ 15px */
.lg-actions { flex-wrap: wrap; row-gap: var(--lg-space-2); }         /* 按钮换行而不是被裁掉 */
.lg-glass { border-radius: var(--lg-radius-lg); }                    /* 装饰尺寸可留 px */
```

可判定验收（浏览器「仅缩放文字」200%，或根字号改 32px）：

1. `.lg-actions` 中每个按钮仍完整可见可点，按钮多时**换行**，不出现 `overflow: hidden` 或省略号吞掉按钮文案。
2. `.lg-toolbar` / `.lg-primary` / `.lg-menu` 高度随文字增长，首行顶部与末行基线均未被切边。
3. 错误信息、金额、状态、按钮文案**不得**被 `text-overflow: ellipsis` 隐藏；`.lg-sidebar` / `.lg-inspector` 允许降宽或折叠，但内容不可溢出且不可达；表格自行横向滚动，不靠压缩字号「塞进去」。
4. 禁止用 `transform: scale()` 或 `zoom` 实现文字放大。

## 7. 动效与语言无关，但排版相关

- **不要对 `letter-spacing` 或 `font-size` 做过渡/动画**：字距变化会让每行断行点重算、文字抖动；字号变化触发整块回流。文字入场只改透明度。
- `prefers-reduced-motion: reduce` 下文字淡入改为立即显示，**不改字号**，也不改最终布局尺寸。
- 文字出现前必须已占据最终排版空间：用 `opacity` 而不是 `display: none → block`，避免入场瞬间回流。

```css
@keyframes lg-text-in { from { opacity: 0 } to { opacity: 1 } }
.lg-text-enter { animation: lg-text-in var(--lg-dur-content) var(--lg-ease) both; }
@media (prefers-reduced-motion: reduce) {
  .lg-text-enter { animation-duration: .01ms; animation-iteration-count: 1; }
}
```

## 8. 交付与验证

实现或审查时至少报告：`lang` 是否逐层正确（尤其混排段落）；中文正文行高实测值（应 ≥1.6）；是否存在全局 `letter-spacing`（应为否）；`text-spacing-trim` / `text-autospace` 缺失时是否仍可读；物理属性残留清单；200% 仅文字缩放与 `dir="rtl"` 下的实测结果（见 §6.3 与 §4.1）。

## 9. 来源（2026-03 核实）

- MDN `text-spacing-trim`（Limited availability；字体缺 `halt`/`chws` 特性时该属性整体失效）：https://developer.mozilla.org/en-US/docs/Web/CSS/text-spacing-trim
- MDN `text-autospace`（Baseline 2025）：https://developer.mozilla.org/en-US/docs/Web/CSS/text-autospace
- Web platform features explorer `text-spacing-trim`（Chrome/Edge 123；Firefox 不支持/性能顾虑；Safari 不支持/WebKit bug 252068）：https://web-platform-dx.github.io/web-features-explorer/features/text-spacing-trim/
- Web platform features explorer `text-autospace`（Firefox 145、Safari 27；Chromium bug 429178779）：https://web-platform-dx.github.io/web-features-explorer/features/text-autospace/
- caniuse `text-autospace: insert`（Safari 27 / Firefox 145+；Chrome、Edge 不支持）：https://caniuse.com/mdn-css_properties_text-autospace_insert
- MDN `line-break`（Baseline，2020-07 起跨浏览器可用）：https://developer.mozilla.org/en-US/docs/Web/CSS/line-break
- caniuse `overflow-wrap: anywhere`（Chrome/Edge 80+、Firefox 65+、Safari 15.4+）：https://caniuse.com/mdn-css_properties_overflow-wrap_anywhere
- Web platform features explorer Hyphenation（Chrome 88、Firefox 43、Safari 17）：https://web-platform-dx.github.io/web-features-explorer/features/hyphens/
- Web platform features explorer `text-wrap: balance`（Chrome 114、Firefox 121、Safari 17.5）：https://web-platform-dx.github.io/web-features-explorer/features/text-wrap-balance/
- Web platform features explorer `text-wrap: pretty`（Chrome 117、Safari 26；Firefox 未实现）：https://web-platform-dx.github.io/web-features-explorer/features/text-wrap-pretty/
- caniuse CSS Logical Properties（Safari 12.1–14.x 部分、15+ 完整；Chrome/Edge 89+；Firefox 66+）：https://caniuse.com/css-logical-props
- caniuse `padding-inline`（Chrome/Edge 87+、Firefox 66+、Safari 14.1+）：https://caniuse.com/mdn-css_properties_padding-inline
- caniuse `inset-inline-start`（Chrome/Edge 87+、Firefox 63+、Safari 14.1+）：https://caniuse.com/mdn-css_properties_inset-inline-start
- caniuse `border-block-start`（Chrome 69+、Firefox 41+、Safari 12.1+）：https://caniuse.com/mdn-css_properties_border-block-start
- MDN `font-variant-numeric`（Baseline，2020-01 起跨浏览器可用）：https://developer.mozilla.org/en-US/docs/Web/CSS/font-variant-numeric

### 未确证项

- **macOS Safari 是否仍提供「最小字号」设置项**：未在 Apple 官方文档或 WebKit 发布说明中确证（公开资料多为 Safari 5 时代的可访问性指南）。验证方式：在目标 Safari 版本的「设置 → 高级 / 网站」逐项核对，或在本地页面同时渲染 `font-size: 9px` 与 `1rem` 文本比较实际尺寸；确证前不得把它写成已知约束。
- **`text-spacing-trim` 在 PingFang SC / Hiragino Sans 下的实际收窄量**：MDN 指出字体缺 `halt` 或 `chws` 特性时该属性整体失效，但未确证这两款字体各自是否提供、效果差异多大。验证方式：Chrome 123+ 中对同一段含 `（）「」、。` 的中文与日文文本分别渲染并量测行宽差；确证前不要假设中文一定收窄。
- **`-webkit-text-stroke` 作为标点收窄替代手段**：无 MDN 标准页面（`/Web/CSS/text-stroke` 返回 404），属非标准实现，行为未确证，本文件默认不采用。
