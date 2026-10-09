# 验收与交付

实施前记录区域、固定/弹性角色、滚动主体、主操作归属、最小尺寸及窄屏/短屏降级，不强制所有页面变三栏。

## 场景矩阵

"规范出处"列指向该场景的规则来源；"静态可查"表示不需要真实浏览器即可核对（代码审查/脚本）。

| 场景 | 验证目标 | 规范出处 | 方式 |
|---|---|---|---|
| 正文从 2 项变 50 项、展开长说明 | 按钮底边稳定，末项可达 | `layout-and-scroll.md` 固定底栏 | 真实浏览器 |
| 多行错误、按钮加载 | 不跳位，不丢输入 | `components-and-states.md` 表单 | 真实浏览器 |
| 侧栏开关、容器缩放 | 图表重新测量，无零尺寸或裁切 | `components-and-states.md` 图表 | 真实浏览器 |
| 空态→执行→结果 | 框架稳定，不意外导航 | `components-and-states.md` 状态 | 真实浏览器 |
| 长文件名、翻译 | 不撑宽，不挤走操作 | `layout-and-scroll.md` 多栏溢出 | 真实浏览器 |
| 系统常驻滚动条 | 无明显横向跳动 | `layout-and-scroll.md` 滚动条 | 真实浏览器（三种滚动条偏好） |
| 查看旧日志时新增事件 | 不强制跟随 | `layout-and-scroll.md` 展开 | 真实浏览器 |
| 模态开关、键盘操作 | 背景不滚、焦点恢复、菜单不被遮挡 | `window-and-navigation.md`、`layout-and-scroll.md` 层级 | 真实浏览器 |
| 短屏、200% 页面缩放 | 操作可达，无非必要页面横滚 | `layout-and-scroll.md` 窄屏短屏 | 真实浏览器 |
| **仅文字放大到 200%** | 控制层高度随文字增长、不裁切，action bar 换行 | `accessibility.md` `8 | 真实浏览器（改基准字号，非页面缩放） |
| 减少动态 | 状态完整，反馈类变化仍可见 | `accessibility.md` `7 | 真实浏览器 + `emulateMedia` |
| 减少透明 | 实色可读，边界仍成立 | `accessibility.md` `5 | 见下方"减少透明度怎么测" |
| 提高对比 / Windows 高对比 | 层级靠文字与边框成立 | `accessibility.md` `6 | 真实浏览器 + 系统设置 |
| 焦点环对比度 | 环两侧各 ≥ 3:1 | `accessibility.md` `3 | 取色器实测 |
| 玻璃层数与帧率 | 符合性能预算表 | `materials-and-optics.md` `9 | DevTools Performance / Layers |
| token 一致性 | 无未定义 `--lg-*`、无裸十六进制/裸 z-index | `visual-system.md`、`assets/foundation.css` | 静态可查（脚本/grep） |

## 组件专项验收（新增）

以下是 **Dialog / Selector / Table** 设计或实施任务的最小行为验证集。单纯 CSS 断言或页面截图不能替代交互检查：

| 组件 | 正向路径 | 必须包含的反例 | 对应规范 |
|---|---|---|---|
| Modal / Sheet | Trigger → 弹窗 → Tab → 保存 → 焦点恢复 | 关闭时脏数据；短屏 Footer 遮挡；Modal 内下拉被挡 | `overlays-and-dialog-components.md` |
| Alert | 安全取消 / 明确确认 | 遮罩点击或默认 Enter 意外执行危险动作 | `overlays-and-dialog-components.md` |
| Popover / Menu | 锚点打开、键盘选项、Esc 关闭 | 触发器附近窗口边界、RTL、嵌套 Portal | `overlays-and-dialog-components.md` |
| Select / Combobox | Arrow / Enter / Escape、已选值清楚 | 远程请求乱序、零结果、标签过长 | `selection-and-input-components.md` |
| Segmented / Checkbox | 键盘切换，勾选与焦点可区分 | 200% 文字放大下 label 裁切、仅靠颜色标选择 | `selection-and-input-components.md` |
| Table | 排序、筛选、选中、批操作、回退 | server sorting 不同步、跨页选择错乱、320px 横滚错误 | `tables-and-data-components.md` |

样式演示见 `assets/component-showcase.html`。它只验证了浏览器原生 dialog/select/table 的基础路径；提交生产代码时仍需针对真实框架和异步状态测试。

## 视口矩阵与断点命中

参考尺寸：1920×1080、1440×900、1280×720、1024×768、768×1024、390×844、320×568。按目标设备及实际断点两侧选择，不因局部修改机械重跑全部。

以 foundation.css 的默认断点（宽度 ≤ 767.84px 或高度 ≤ 560px 触发降级）为准，各尺寸命中情况：

| 视口 | 宽度分支 | 高度分支 | 结论 |
|---|---|---|---|
| 1920×1080 | 否 | 否 | 完整多栏 |
| 1440×900 | 否 | 否 | 完整多栏 |
| 1280×720 | 否 | 否 | 完整多栏 |
| 1024×768 | 否 | 否 | 完整多栏 |
| 768×1024 | 否（768 > 767.84） | 否 | 完整多栏，**紧贴宽度断点，必须测** |
| 390×844 | 是 | 否 | 宽度降级 |
| 320×568 | 是 | 否 | 宽度降级（高度 568 > 560，不触发高度分支） |

如果你改了断点值，这张表必须一起改——否则"降级验证过了"可能只是没命中任何分支。高度分支针对软键盘压缩后的可用高度，不是常见的 720p 桌面窗口。

## 减少透明度怎么测（方法学）

`prefers-reduced-transparency` **只有 Chromium 系支持**（Firefox / Safari 未实现），所以不能把它当成可复现的通用开关：

1. Chromium：DevTools → Rendering → Emulate `prefers-reduced-transparency: reduce`，验证玻璃退为实色且边框仍成立；
2. Safari / Firefox：用 `prefers-contrast: more` 路径 + 手动强制实色基线（临时覆盖 `backdrop-filter: none`）两条路径验证；
3. 桌面壳：在 macOS 系统设置里真实开启「降低透明度」，验证窗口原生材质的变化（见 `desktop-shell-integration.md`）；
4. 交付说明里写清哪条路径真正跑过，哪条没有。

## 其他验收规则

固定操作可测量展开前后按钮底边：视口、字级、操作内容不变时应稳定。浏览器缩放不能用缩小截图代替。二维画布/表格允许自身横向滚动。

对比度：普通文字 4.5:1，大字 3:1，必要控件/状态图形 3:1；`--lg-border` / `--lg-separator` / `--lg-chart-grid` 属装饰豁免，一旦参与读数即升级为必要图形。

沿用已有测试工具（axe-core / Lighthouse / Playwright `emulateMedia` 等），测试交互与行为，不只匹配标题或 CSS 字符串。构建/类型检查后检查实际浏览器；模拟数据验证明确标注，不等于真实后台验收。检查与初始化相关的控制台错误。

无浏览器时明确实屏、软键盘、滚动条偏好与系统辅助设置未验证。

## 交付

规范请求交付独立完整文本，不要求用户拼接多轮答案。实现交付修改范围、实际验证和限制；性能结论要写测过的设备与断点数据来源。审查给复现条件、建议及验证方式。不自动发布、改系统设置或扩大原任务。
