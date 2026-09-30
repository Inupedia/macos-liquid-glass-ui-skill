# Web 实现适配：Vanilla、Vue、React 与现有组件库

本文件不要求项目换框架。目标是把 Liquid Glass 规范映射到现有工程，而不是新建第二套设计系统。

## 1. 通用实施顺序

1. 找现有 design tokens / CSS variables；
2. 找全局 layout shell 与主要滚动容器；
3. 找 Button/Input/Table/Dialog/Drawer 等基础组件来源；
4. 建立 Liquid Glass token 映射；
5. 只新增项目缺少的语义 token；
6. 在 scoped root 下启用，不全局污染；
7. 逐组件验证，不用大段全局 CSS 强行覆盖组件库。

## 2. Token Mapping

推荐先映射语义，不直接复制值：

```text
app background       -> --lg-bg
content surface      -> --lg-surface
secondary surface    -> --lg-surface-secondary
primary text         -> --lg-text
secondary text       -> --lg-text-secondary（--lg-muted 是它的历史别名）
boundary             -> --lg-border（装饰） / --lg-border-strong（需 3:1）
separator            -> --lg-separator
accent               -> --lg-accent（边框/焦点/图标/大字）
solid button         -> --lg-button + --lg-button-text
control glass        -> --lg-glass-regular
floating glass       -> --lg-glass-thick
rich-media glass     -> --lg-glass-clear（需通过 clear 判定线）
status               -> --lg-success/warning/danger/info/neutral（+ -bg）
chart series         -> --lg-chart-1..5 与 --lg-chart-grid（明暗各一套）
layering             -> --lg-z-content/sticky/menu/drawer/modal/toast
```

已有品牌色优先。只有用户明确要求完整换肤时才替换 accent。**不要把这些值再抄一份十六进制进业务代码**：`assets/foundation.css` 是唯一定义源，项目里要么直接引用它，要么把值搬进项目自己的 token 层后只保留语义别名。

双向映射是迁移的一部分，不是一次性动作：写清"项目 token → lg token"，也写清"lg token 找不到对应项时怎么处理"（新增语义 token / 复用最接近的旧 token / 记录为待办），否则下次反向同步会互相覆盖。

## 3. Vanilla CSS

基础结构：

```css
.lg-workspace {
  height: 100dvh;
  display: grid;
  grid-template-rows: auto minmax(0, 1fr) auto;
  overflow: hidden;
}

.lg-scroll {
  min-width: 0;
  min-height: 0;
  overflow: auto;
}
```

Glass：

```css
.lg-glass {
  background: var(--lg-surface-material);
  border: 1px solid var(--lg-edge);
  -webkit-backdrop-filter: blur(var(--lg-blur-material)) saturate(var(--lg-saturation));
  backdrop-filter: blur(var(--lg-blur-material)) saturate(var(--lg-saturation));
}
/* 材质由 data-material 切换，两个活动变量跟着变，不要复制多份玻璃规则 */
[data-material="thick"] {
  --lg-surface-material: var(--lg-glass-thick);
  --lg-blur-material: var(--lg-blur-thick);
}
```

根容器同时带上字体与配色方案：

```css
.lg-theme {
  font-family: var(--lg-font);
  color-scheme: light;               /* data-theme="dark" 时改为 dark，否则原生控件不跟随 */
}
```

必须提供不支持 backdrop-filter 和 reduce transparency 的 solid fallback，并且**背景、边框、阴影一起改**（只改背景会留下透明高光边，在白底上等于没有边界）。

## 4. Vue 3

### 原则

- 保留 View → Store → API 等项目既有分层；
- Liquid Glass 是 UI concern，不进入 store/business logic；
- 通用材质封装成小型 presentational component 或 utility class；
- 不为样式调整复制业务组件。

### 推荐结构

```text
src/
  styles/
    tokens.css
    liquid-glass.css
  components/ui/
    GlassPanel.vue       # 只有确实需要共享行为时
    StableActions.vue
```

不要创建几十个 `LgButton/LgInput/LgTable` 去包裹成熟组件库，除非项目本来就在做独立 design system。

## 5. Element Plus

优先通过 CSS variables / scoped class 映射，不用深层 DOM 选择器绑死内部实现。

策略：

- `el-button`：保留状态行为，只调整 token、radius、shadow；
- `el-input` / `el-select`：稳定 surface，focus 使用 accent ring；
- `el-dialog`：header/body/footer 明确，body 可滚，footer 稳定；
- `el-drawer`：用于 inspector/detail，窄屏 overlay；
- `el-table`：保持 content-solid，不给行做 backdrop blur；
- `el-popover` / dropdown：可以使用 thick glass；
- `el-tabs`：只有符合信息架构时使用，不和 sidebar 重复导航。

避免：

```css
.el-table * { background: transparent !important; }
```

这会破坏可读性和组件状态。

## 6. React

规则与 Vue 相同：视觉层不侵入数据逻辑。

推荐：

- theme tokens 放 CSS variables / theme provider；
- `GlassSurface` 只表达材质语义；
- `WorkspaceShell` 只表达布局合同；
- 业务组件继续复用现有 Button/Table/Dialog；
- 状态管理不因为换视觉而迁移。

不要为了 Liquid Glass 引入新的全量 UI framework。

## 7. Tailwind

Tailwind 项目优先扩展 theme token / CSS variables，而不是在 JSX/模板堆几十个任意值：

不推荐：

```text
bg-white/73 backdrop-blur-[27px] rounded-[23px] shadow-[...]
```

推荐建立语义 utilities/component layer：

```css
@layer components {
  .lg-control-surface { ... }
  .lg-content-surface { ... }
  .lg-floating-surface { ... }
}
```

让 blur、opacity、border、shadow 由统一 token 控制。

## 8. Inspira UI（Vue / Nuxt 可选增强层）

当用户明确要求 Inspira UI，或 Vue/Nuxt 产品确实需要更强的背景、卡片、beam、reveal、text effect、visualization 等表现力时，读取 `references/inspira-ui.md`。

定位：

```text
Liquid Glass Skill
  -> design system / layout / material / accessibility / motion budget

现有基础组件库（Element Plus / shadcn-vue / Nuxt UI 等）
  -> reliable Button / Form / Table / Tree / Dialog / Menu behavior

Inspira UI
  -> optional visual enhancement / expressive components
```

### 不要默认安装

普通 Vue 项目不因为使用本 Skill 就自动加 Inspira UI。只有真实区域需要时才安装具体组件。

当前官方安装方向常见依赖包括：

```bash
pnpm add @vueuse/core motion-v tw-animate-css @inspira-ui/plugins
```

实际执行前以当前官方文档和项目 Tailwind 版本为准。

### Element Plus + Inspira UI

推荐：

- Element Plus 保留表格、树、表单、分页、Dialog 等基础行为；
- Inspira UI 用于 empty/onboarding、少量 feature card、流程连接、KPI 数值增强、媒体预览等；
- Liquid Glass tokens 统一两者颜色、圆角、阴影和材质。

禁止：

- 为每个 `el-card` 加不同动画；
- 用 spotlight/beam 替代选中、focus、error；
- 把 `el-table` 行改成动态玻璃卡片；
- 为了一个效果升级整个 Vue/Tailwind 技术栈。

### shadcn-vue / Nuxt + Inspira UI

这是较自然的组合，但仍应：

- 复用现有 aliases 和 theme tokens；
- 保留 primitive 的 keyboard/ARIA/portal；
- 安装前检查 registry 是否覆盖项目已修改文件；
- 把 demo 的颜色、gradient、文案映射回项目 design tokens；
- browser-only/Canvas/WebGL 组件单独处理 SSR，不把整页变成 client-only。

### Motion / Performance

Inspira UI 示例里的持续动效不能直接等同于产品默认动效。

工作台默认：

- 同视口最多 1 个明显持续装饰动画；
- Table/Form/Dialog/Toolbar 不使用持续背景动画；
- `prefers-reduced-motion` 下回退到静态最终状态；
- Canvas/WebGL 只有在业务表达明显受益时采用；
- observer、RAF、listener、WebGL context 在卸载时 cleanup。

### macOS-style Dock

Inspira UI 提供 Dock 类组件，但不要因为产品想“像 Mac”就加入。只有产品确实存在 launcher / app switcher / tool palette 语义时才可采用，并且必须是真实功能控件，不冒充操作系统 Dock。

## 9. Headless UI / Radix / Ark 等

这类库已经处理大量交互语义。保留：

- focus management
- keyboard navigation
- dismiss behavior
- portal
- aria

只替换 visual layer，不要因为自定义玻璃重新手写一套 dialog/menu/listbox 行为。

## 10. ECharts / Chart.js / D3

图表绘图区默认 content-solid。

Liquid Glass 可用于：

- tooltip
- floating zoom controls
- legend/filter toolbar
- context popover

系列色必须把 `--lg-chart-1..5` 真的喂给图表库，而不是在库的 theme 里另写一套色值；明暗主题各取一套：

```js
// ECharts：从 CSS 变量读，主题切换时重新取一次
const css = getComputedStyle(document.querySelector('.lg-theme'));
const series = [1, 2, 3, 4, 5].map((n) => css.getPropertyValue(`--lg-chart-${n}`).trim());
option = {
  color: series,
  xAxis: { axisLine: { lineStyle: { color: css.getPropertyValue('--lg-border-strong').trim() } } },
  splitLine: { lineStyle: { color: css.getPropertyValue('--lg-chart-grid').trim() } },
};
```

Chart.js 用 `Chart.defaults.color` / `borderColor` 读同样的变量；D3 直接 `stroke="var(--lg-chart-1)"`。注意 ECharts/Canvas 类库**读不到 CSS 变量字符串**时要用 `getComputedStyle` 解析成具体色值（上面示例即此做法），并在主题切换后重新解析一遍。

颜色不是唯一编码：series 上同时给 `symbol` 或 `lineStyle.type`，图例复用同一标记；阈值线用 `--lg-border-strong` 或状态色并加文字标签，不要用装饰网格色。

容器 resize：

- 监听实际 container；
- sidebar/inspector 改变后重新测量；
- hidden -> visible 后再初始化/resize；
- dispose/cleanup listener。

## 11. Electron / Tauri

**窗口原生材质优先于页面内 backdrop-filter**，细节（Electron `vibrancy` / `backgroundMaterial`、Tauri v2 `setEffects()` 与 `Effect.LiquidGlassRegular` / `LiquidGlassClear`、权限与透明窗口、降级链）见 `references/desktop-shell-integration.md`。

在本文件层面只记三条：

- 页面内 backdrop-filter 只能模糊 WebView 自己绘制的内容，不会模糊桌面壁纸；窗口不透明时"半透明页面"是假的。
- 窗口材质之上不要再叠 `.lg-glass`，否则变成 glass-on-glass。
- 自定义 titlebar/window buttons 必须连接真实窗口 API；否则不要添加装饰性 traffic lights。

同时验证：

- drag region（`-webkit-app-region: drag` 区域内的按钮必须显式 `no-drag`，否则点不动）；
- window resize；
- maximize/fullscreen；
- Windows/Linux fallback（若跨平台）；
- 高 DPI。

## 12. 渐进迁移

大型旧项目按顺序：

1. tokens；
2. page shell / scroll ownership；
3. toolbar/sidebar；
4. button/input focus states；
5. dialog/drawer/popover；
6. data display；
7. optional Inspira UI enhancements；
8. polish。

不要一次 PR 重写所有页面。每个阶段都要能独立回滚：

- 阶段范围写清"改了哪些文件/组件"，避免一个 PR 横跨 tokens 与业务逻辑；
- 回滚策略明确到"删掉 `.lg-theme` 类是否回到原样"——如果做不到，说明改动已经侵入业务结构，需要拆小；
- 视觉回归基线：进入第 3 步之前，先对要改的关键页面截一组基线图（目标浏览器 + 目标视口），每阶段后对比；没有基线的"看起来没变"不算验收；
- 主题切换与 token 变更后，图表/Canvas 类组件要重新解析色值（见 §10）。

## 13. SSR / Hydration

玻璃相关代码大量依赖运行时（`getComputedStyle`、`matchMedia`、`backdrop-filter` 特性检测、Canvas/WebGL、Inspira UI 的 motion 组件），在 SSR 下容易产生 hydration mismatch。

规则：

- 服务端渲染阶段**不要**根据 `window`/`matchMedia` 决定类名或结构；
- 需要客户端能力时用 `ClientOnly`（Nuxt）、`defineAsyncComponent` + `ssr: false`、或 `useState`/`useEffect` 在水合后再挂载增强类（例如水合后才加 `.lg-glass` 的真实 blur）；
- 首屏 HTML 必须是**可读的实色基线**，水合后再增强为玻璃；反过来（先玻璃后实色）会造成可见跳变；
- Inspector/表格等尺寸相关逻辑，水合后再测量，服务端不要输出零尺寸占位；
- Canvas/WebGL 组件单独隔离，不要把整页变成 client-only。

## 14. Review checklist

- 是否复用了现有组件库？
- 是否避免全局 `!important`？
- 是否避免深度绑定组件库内部 DOM？
- 是否保留 keyboard/ARIA？
- 是否只在 control/navigation layer 用 blur？
- 是否引用了存在的 token（没有 `--lg-glass-edge`→`--lg-edge`、`--lg-blur`→`--lg-blur-material` 这类笔误）？
- 是否有 fallback（背景 + 边框 + 阴影一起降级）？
- 是否显式设置了 `color-scheme`？
- 是否把 `--lg-chart-*` 真正喂给了图表库，明暗两套都用上？
- SSR 首屏是否为可读实色基线，没有 hydration mismatch？
- 如果使用 Inspira UI，是否只是必要的增强而非整页炫技？
- Inspira 持续动画是否有 reduced-motion / performance fallback？
- 是否真实验证 resize / short viewport / 200% / 仅文字放大？
- 是否没有为了换肤改业务逻辑？
