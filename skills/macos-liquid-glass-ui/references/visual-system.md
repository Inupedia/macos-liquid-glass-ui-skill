# 视觉系统

银白冷灰、深石墨、系统蓝、乳白玻璃控制层、轻阴影与连续圆角。保留用户批准的品牌。全页主题一致，语义色和图表系列色可合理超出单强调色。

## 完整基础色板

| Token | 浅色 | 深色 | 用途 |
|---|---|---|---|
| background | #F5F5F7 | #16181D | 页面 |
| background-secondary | #ECEEF2 | #1C1F25 | 次背景 |
| surface | #FFFFFF | #22252C | 内容 |
| surface-secondary | #F8F9FB | #2B2F38 | 分区 |
| text-primary | #1D1D1F | #F5F5F7 | 标题正文 |
| text-secondary | #62626A | #B5B8C2 | 解释 |
| text-tertiary | #85858E | #969BA8 | 非关键注释 |
| border | #DCDDE3 | #424854 | 控件边界 |
| separator | #E8E9EE | #363B46 | 分隔 |
| accent | #007AFF | #409CFF | 强调 |
| accent-hover | #006BE0 | #63AEFF | 悬停 |
| accent-pressed | #005BC4 | #2485EC | 按下 |
| accent-soft | #EAF3FF | #203B58 | 选中浅底 |
| accent-text | #005FCC | #79BAFF | 链接 |
| primary-button | #006BE0 | #409CFF | 主按钮底 |
| primary-button-text | #FFFFFF | #101B29 | 主按钮字 |

小字白字按钮使用更深 #006BE0；不能假定白字配 #007AFF 对所有字号都达标。焦点外环采用强调色并与背景区分。

| 状态 | 浅色文字 / 底色 | 深色文字 / 底色 |
|---|---|---|
| 成功 | #248A3D / #EAF6ED | #76D892 / #183B27 |
| 提醒 | #A66500 / #FFF4DF | #F4C56C / #44331C |
| 错误 | #D70015 / #FFF0F1 | #FF929B / #46232A |
| 信息 | #005FCC / #EAF3FF | #79BAFF / #203B58 |
| 中性 | #62626A / #EFF0F3 | #B5B8C2 / #2B2F38 |

状态搭配文字/图标。可选环境色：冰蓝 #DCEEFF、浅紫 #E9E3FA、银灰 #E7EBF1，8%–18% 透明度，限背景边缘。深色降低环境光。

## 材质

| 材质 | 浅色背景 | 模糊 | 使用 |
|---|---|---|---|
| 轻玻璃 | rgba(255,255,255,.62) | 20px | 轻导航 |
| 标准 | rgba(250,251,253,.78) | 24px | 工具栏 |
| 厚玻璃 | rgba(250,251,253,.92) | 32px | 弹层 |
| 内容 | #FFFFFF | 无 | 正文图表 |

饱和度约 140%；高光边缘 rgba(255,255,255,.75)，内高光 rgba(255,255,255,.65)。深色标准 rgba(35,39,48,.82)，边缘 rgba(255,255,255,.12)。避免多层模糊；不支持或减少透明时退实色，基本可读性不能依赖偏好查询支持。

阴影：轻层 0 2px 8px rgba(25,40,65,.04)；浮层 0 8px 28px rgba(25,40,65,.08)；模态 0 24px 64px rgba(25,40,65,.16)。深色更多依靠明度和边界。

## 字体、间距与圆角

系统字体栈：-apple-system, BlinkMacSystemFont, "SF Pro Display", "SF Pro Text", "PingFang SC", "Helvetica Neue", "Segoe UI", sans-serif。不要随意下载分发 Apple 字体。

| 层级 | 大小 | 字重 | 行高 |
|---|---|---|---|
| 展示标题 | 40–56px | 600 | 1.15 |
| 页标题 | 28–36px | 600 | 1.25 |
| 区块标题 | 20–24px | 600 | 1.35 |
| 卡片标题 | 16–18px | 600 | 1.4 |
| 正文 | 14–16px | 400 | 1.6 |
| 辅助 | 12–13px | 400 | 1.5 |
| 按钮 | 13–14px | 500–600 | 1.3 |
| 数值 | 28–40px | 500–600 | 1.15 |

中文正常字距，英文短标题可微负字距。数据 tabular-nums；投屏解释 20–24px 起。使用 rem 保留文字放大能力。

间距 4/8/12/16/24/32/48/64px；图文 8px、字段 12–16px、容器内边距 20–24px、区域 24–32px、页面 24–40px、小屏 16px。

圆角：标签 6–8px；输入按钮 10–12px；菜单 14–16px；主面板 20–24px；模态 24–28px；胶囊 999px。内层圆角随内边距递减。

沿用一致图标家族，16/20/24px，描边约 1.5–2px，图标按钮提供可访问名称。不要添加无功能红黄绿按钮或 Dock。

## 官方边界

本表是 Web 基线，不是 Apple 官方尺寸。需要核实原生行为时参考：
- https://developer.apple.com/design/human-interface-guidelines/materials
- https://developer.apple.com/documentation/technologyoverviews/liquid-glass
