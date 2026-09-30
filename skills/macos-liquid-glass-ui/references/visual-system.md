# 视觉系统

银白冷灰、深石墨、系统蓝、乳白玻璃控制层、轻阴影与连续圆角。保留用户批准的品牌。全页主题一致，语义色和图表系列色可合理超出单强调色。

本文件的每个数值都在 `assets/foundation.css` 里有同名 `--lg-*` token；实现时读 token，不要在业务代码里重复写十六进制值。

## 完整基础色板

| Token | 浅色 | 深色 | 用途 |
|---|---|---|---|
| `--lg-bg` | #F5F5F7 | #16181D | 页面 |
| `--lg-bg-secondary` | #ECEEF2 | #1C1F25 | 次背景 |
| `--lg-surface` | #FFFFFF | #22252C | 内容 |
| `--lg-surface-secondary` | #F8F9FB | #2B2F38 | 分区 |
| `--lg-text` | #1D1D1F | #F5F5F7 | 标题正文 |
| `--lg-text-secondary` | #62626A | #B5B8C2 | 解释 |
| `--lg-text-tertiary` | #85858E | #969BA8 | 非关键注释 |
| `--lg-border` | #DCDDE3 | #424854 | 装饰边界（1.2–1.7:1） |
| `--lg-border-strong` | #6E7076 | #9AA0AC | 需要 3:1 的边界（实测 4.95:1 / 5.84:1） |
| `--lg-separator` | #E8E9EE | #363B46 | 分隔（装饰） |
| `--lg-edge` | rgba(255,255,255,.75) | rgba(255,255,255,.12) | 玻璃高光边 |
| `--lg-accent` | #007AFF | #409CFF | 强调：边框、焦点环、图标、大字号（浅色下 3.69:1） |
| `--lg-accent-hover` | #006BE0 | #63AEFF | 悬停 |
| `--lg-accent-pressed` | #005BC4 | #2485EC | 按下 |
| `--lg-accent-soft` | #EAF3FF | #203B58 | 选中浅底 |
| `--lg-accent-text` | #005FCC | #79BAFF | 链接文字 |
| `--lg-button` | #006BE0 | #409CFF | **白字按钮底**（配白字 5.02:1） |
| `--lg-button-text` | #FFFFFF | #101B29 | 主按钮字 |

两条不可越界的规则：

- **白字按钮只能压 `--lg-button`。** `#007AFF` 配白字只有 4.02:1，低于 4.5:1；`--lg-accent` 只用于边框、焦点环、图标和 ≥18.66px 的大字号强调，不能当白字按钮底色。
- **`--lg-border` / `--lg-separator` 是装饰性的**，实测只有 1.2–1.7:1，只能承担大面积分隔。表单框、选中容器、需要被看见的边界一律用 `--lg-border-strong`。深色下 `#424854` 对 `#22252C` 仅 1.67:1，尤其不能当输入框边界。

| 状态 | 浅色文字 / 底色（对比度） | 深色文字 / 底色（对比度） |
|---|---|---|
| 成功 | #1B6B2F / #EAF6ED（5.92:1） | #76D892 / #183B27（7.09:1） |
| 提醒 | #8A5300 / #FFF4DF（5.80:1） | #F4C56C / #44331C（7.52:1） |
| 错误 | #C40012 / #FFF0F1（5.66:1） | #FF929B / #46232A（6.41:1） |
| 信息 | #005FCC / #EAF3FF（5.35:1） | #79BAFF / #203B58（5.62:1） |
| 中性 | #5A5A62 / #EFF0F3（6.00:1） | #B5B8C2 / #2B2F38（6.77:1） |

五组状态色均已达到 4.5:1，因此可以承载正文级文字；对应 token 为 `--lg-success` / `--lg-warning` / `--lg-danger` / `--lg-info` / `--lg-neutral` 及 `-bg` 后缀的底色。状态仍需文字或图标表达，不能只靠颜色。

状态色**不是**图表或玻璃染色板；不要用成功绿当图表主系列色。

## 图表系列色

浅色与深色各一套，全部按"对内容底色 ≥3:1"筛选：

| Token | 浅色（对 #FFFFFF） | 深色（对 #22252C） |
|---|---|---|
| `--lg-chart-1` | #0A63B0（6.13:1） | #5AA9F0（6.11:1） |
| `--lg-chart-2` | #14706B（5.90:1） | #4FC3B8（7.18:1） |
| `--lg-chart-3` | #5B57A8（6.22:1） | #A9A5E8（6.75:1） |
| `--lg-chart-4` | #8A5A12（5.91:1） | #E0B36A（7.91:1） |
| `--lg-chart-5` | #A83A5C（6.13:1） | #EE8FA8（6.67:1） |
| `--lg-chart-grid` | #E7EEF5 | #2F343D |

`--lg-chart-grid` 是纯装饰网格线（1.2–1.4:1），不承担 3:1 义务；如果网格线要参与读数（例如阈值线），它必须换成 `--lg-border-strong` 或状态色并加标签。

颜色不是唯一编码：每条系列同时给 marker 形状或 dash pattern，图例与 tooltip 都要带该标记，色盲用户与黑白打印下仍可区分。

可选环境色：冰蓝 #DCEEFF、浅紫 #E9E3FA、银灰 #E7EBF1，8%–18% 透明度，限背景边缘。深色降低环境光。

## 材质

| 材质 | Token | 浅色 | 模糊 | 使用 |
|---|---|---|---|---|
| 内容 | `--lg-content` | #FFFFFF | 无 | 正文、表格、图表 |
| 轻玻璃 | `--lg-glass-light` | rgba(255,255,255,.62) | 20px | 轻导航 |
| 标准 | `--lg-glass-regular` | rgba(250,251,253,.78) | 24px | Toolbar、Sidebar |
| 厚玻璃 | `--lg-glass-thick` | rgba(250,251,253,.92) | 32px | 菜单、Popover、Sheet |
| 清澈 | `--lg-glass-clear` | rgba(255,255,255,.42) | 20px | 视觉丰富背景上的少量控制 |
| 品牌染色 | `--lg-glass-tinted` | rgba(234,243,255,.82) | 24px | 选中、关键操作 |

饱和度 `--lg-saturation: 140%`；高光边缘 `--lg-edge`；深色标准 rgba(35,39,48,.82)。实现方式是把 `--lg-surface-material` 与 `--lg-blur-material` 两个变量切到对应值（`[data-material="light|regular|clear|thick|tinted"]`），不要为每种材质复制一份 `.lg-glass` 规则。

clear 不能凭感觉使用：合成后背景亮度进入中间区间时正文对比会掉到 4.5:1 以下，判定线与补偿方式见 `references/materials-and-optics.md`。

阴影：`--lg-shadow-light`、`--lg-shadow-float`、`--lg-shadow-modal`。深色更多依靠明度和边界。

## 主题与系统外观

- `.lg-theme` 必须同时设置 `color-scheme: light`，`.lg-theme[data-theme="dark"]` 设置 `color-scheme: dark`。否则 `<select>` 下拉、日期选择器、自动填充、原生滚动条在深色主题下仍是浅色系统皮肤。
- 主题变量定义在哪个元素上，`color-scheme` 就要定义在哪个元素上；不要只给内部卡片设 `color-scheme`。
- 系统偏好对应 `prefers-contrast: more`（提高对比）、`prefers-reduced-transparency: reduce`（仅 Chromium，见 accessibility.md）、`forced-colors: active`（Windows 高对比）。三者都已在 foundation.css 中实现，实现时不要覆盖。

## 字体、间距与圆角

系统字体栈即 `--lg-font`：

```css
--lg-font: -apple-system, BlinkMacSystemFont, "SF Pro Display", "SF Pro Text",
  "PingFang SC", "Helvetica Neue", "Segoe UI", sans-serif;
```

不要随意下载分发 Apple 字体。中日韩字形差异、`lang` 属性前提与中西文混排规则见 `references/i18n-and-typography.md`。

字号表使用确定值（不是区间），每级都有 token：

| 层级 | Token 前缀 | 大小 | 行高 | 字重 |
|---|---|---|---|---|
| 展示标题 | `--lg-text-display` | 48px | 1.15 | 600 |
| 页标题 | `--lg-text-page-title` | 32px | 1.25 | 600 |
| 区块标题 | `--lg-text-section` | 22px | 1.35 | 600 |
| 卡片标题 | `--lg-text-card-title` | 17px | 1.4 | 600 |
| 正文 | `--lg-text-body` | 15px | 1.6 | 400 |
| 辅助 | `--lg-text-aux` | 13px | 1.5 | 400 |
| 按钮 | `--lg-text-button` | 14px | 1.3 | 500–600 |
| 数值 | `--lg-text-metric` | 32px | 1.15 | 500–600 |

行高 token 为 `--lg-leading-*`，字重为 `--lg-weight-regular|medium|semibold`。同一个产品内层级数量不要超过上表；不要为了"层级丰富"新增字号。

中文正常字距，英文短标题可微负字距；不要用 `letter-spacing` 解决中西文间距问题（见 i18n reference）。表格数字、KPI、时间、金额使用 `font-variant-numeric: tabular-nums`（工具类 `.lg-num` / `.lg-tabular`）。

投影/远距离观看场景：不要靠猜设备。用容器查询在足够宽的容器里放大正文（`@container (min-width: 1200px) { --lg-text-body: 20px }` 这类做法），并保证放大后控制层高度跟随文字增长。

间距刻度 `--lg-space-1..9`：4/8/12/16/20/24/32/48/64px。图文 8px、字段 12–16px、容器内边距 20–24px、区域 24–32px、页面 24–40px、小屏 16px。20px 属于刻度内（`--lg-space-5`），不要再写刻度外的 18/22px。

圆角只有一套刻度：

| 用途 | Token | 值 |
|---|---|---|
| 标签、chip | `--lg-radius-xs` | 8px |
| 输入、按钮 | `--lg-radius-sm` | 12px |
| 菜单、Popover | `--lg-radius-md` | 16px |
| 面板、玻璃容器 | `--lg-radius-lg` | 24px |
| 模态 | `--lg-radius-xl` | 28px |
| 胶囊 | `--lg-radius-pill` | 999px |

内层圆角随内边距递减（外层 24px + 内边距 8px → 内层 16px）。不要出现 6px、14px、18px 这类刻度外半径。

## 图标与装饰

沿用一致图标家族，16/20/24px，描边约 1.5–2px，图标按钮提供可访问名称。不要添加无功能红黄绿按钮或 Dock。

## 官方边界

本表是 Web 基线，不是 Apple 官方尺寸。需要核实原生行为时参考：

- https://developer.apple.com/design/human-interface-guidelines/materials
- https://developer.apple.com/documentation/technologyoverviews/liquid-glass
