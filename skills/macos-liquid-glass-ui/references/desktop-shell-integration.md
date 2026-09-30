# 桌面壳集成：原生窗口材质优先（Electron / Tauri v2）

> 适用范围：Electron / Tauri v2 / 桌面 WebView 壳里的 macOS Liquid Glass 风格窗口。窗口材质一节描述的是**原生 API 调用**，取值以 Electron / Tauri 官方文档为准；页面内的玻璃仍然遵循 `materials-and-optics.md`，token 唯一定义源是 `assets/foundation.css`。

## 1. 决策顺序

先回答三个问题，答不出就退回页面内玻璃：

1. **是不是桌面壳？** 有 `window.__TAURI_INTERNALS__`、`process.versions.electron`，或自带 titlebar 而无浏览器 chrome。纯浏览器页面不适用本文件。
2. **要透出的是什么？** 窗口原生材质透出的是**桌面壁纸和其他应用窗口**；页面内 `backdrop-filter` 只能模糊**本页自己绘制的内容**。两者是不同来源，不是强弱关系。
3. **这层属于窗口还是页面？** 贴窗口边缘、背后只有桌面的（窗口底、titlebar 区域、sidebar 整条）→ 原生材质；浮在本页滚动内容之上的（menu、popover、浮动控制）→ `[data-material]`。

规则：

- **原生材质优先。** 壳层提供材质 API 时，窗口底用原生材质，`html`/`body` 不画任何背景，不用 `.lg-glass` 铺整页。
- **例外一：后方没有桌面可见。** 已全屏、或内容区不透明填满窗口时，材质不产生视觉信息 → 直接用 `--lg-surface` / `--lg-content`，不要浪费一次合成。
- **例外二：需要模糊本页内容。** 菜单下面是自己的列表、popover 下面是自己的表格 → 这是页面级玻璃，用 `[data-material]`（`--lg-surface-material` + `--lg-blur-material`），窗口材质帮不上忙。
- **例外三：Windows / Linux 语义不同。** Windows 只有 `mica` / `acrylic` / `tabbed`，且主要作用于标题栏与非客户区，不能等价替代 macOS vibrancy；Linux 无窗口材质，直接进降级链（§4）。

## 2. Electron

### 2.1 可直接复制的 BrowserWindow 配置

```js
// main.js —— 窗口材质 + 隐藏标题栏，保留系统 traffic lights
const { app, BrowserWindow, nativeTheme } = require('electron')
const isMac = process.platform === 'darwin', isWin = process.platform === 'win32'

function createWindow () {
  const win = new BrowserWindow({
    width: 1280, height: 800, minWidth: 960, minHeight: 600, show: false,
    // 不设不透明 backgroundColor（默认 #FFF，会盖住材质）；不设 transparent: true（代价见 §2.3）
    ...(isMac && {
      titleBarStyle: 'hiddenInset',     // 隐藏标题栏，保留 traffic lights（更内缩）
      vibrancy: 'under-window',         // 取值见 §2.2；没有 liquid glass 枚举
      visualEffectState: 'followWindow' // 失焦时材质自动变 inactive
    }),
    ...(isWin && {
      backgroundMaterial: 'mica',       // Windows 11 22H2+；否则退回 acrylic / none
      titleBarStyle: 'hidden',
      titleBarOverlay: { color: '#00000000', symbolColor: '#1d1d1f', height: 48 }
    }),
    webPreferences: { contextIsolation: true, sandbox: true, preload: __dirname + '/preload.js' }
  })
  win.once('ready-to-show', () => win.show()); win.loadFile('index.html'); return win
}

// 页面 color-scheme 必须与材质主题一致，否则浅色材质上出现深色控件
app.whenReady().then(() => {
  const win = createWindow()
  const push = () => win.webContents.send('lg-theme', nativeTheme.shouldUseDarkColors ? 'dark' : 'light')
  nativeTheme.on('updated', push); push()
})
```

### 2.2 取值（已核对官方文档）

- `vibrancy`（`_macOS_`）：`appearance-based`、`titlebar`、`selection`、`menu`、`popover`、`sidebar`、`header`、`sheet`、`window`、`hud`、`fullscreen-ui`、`tooltip`、`content`、`under-window`、`under-page`。窗口级底材默认 `under-window`；sidebar 整条受材质控制时用 `sidebar`。
- `visualEffectState`（`_macOS_`，**必须与 `vibrancy` 同时使用**）：`followWindow`（默认，跟随窗口激活态）、`active`（恒为激活态）、`inactive`（恒为非激活态）。
- `backgroundMaterial`（`_Windows_`）：`auto`、`none`、`mica`、`acrylic`、`tabbed`；运行时用 `win.setBackgroundMaterial(material)`。
- `titleBarStyle`：`default`、`hidden`、`hiddenInset`（`_macOS_`）、`customButtonsOnHover`（`_macOS_`，实验性）。`hidden` / `hiddenInset` **保留** traffic lights；`frame: false` 则连 traffic lights 一起移除。

### 2.3 必须避开的坑

- **不透明层会吃掉材质。** 不透明 `backgroundColor`（默认 `#FFF`）或不透明的页面背景都会让材质不可见；`#AARRGGBB` 形式的 alpha **仅在 `transparent: true` 时**被支持。第一顺位检查顺序：① `html`/`body` 是否还有背景；② `backgroundColor` 是否不透明；③ 是否误设了 `transparent`。
- **`transparent: true` 的官方限制**：透明区域不可点击穿透；**透明窗口不可调整大小**（把 `resizable` 设回 `true` 可能让透明窗口在部分平台失效）；CSS `blur()` 只作用于 web contents，无法模糊窗口下方的其他应用；DevTools 打开时窗口不再透明；Windows 上无法用系统菜单或双击标题栏最大化；macOS 上不显示原生窗口阴影。矩形窗口不要用它。
- **拖拽区吞指针事件。** `app-region: drag`（旧写法 `-webkit-app-region: drag`）标记的矩形**忽略全部指针事件**：重叠的按钮收不到 click 与 enter/leave。规则：整窗可拖时给所有按钮加 `app-region: no-drag`；只拖 titlebar 时给 titlebar 内所有控件加 `no-drag`；拖拽区内加 `user-select: none` 防止选中文字；拖拽区内**不要**用自定义右键菜单（系统会弹原生菜单）。调试用环境变量 `ELECTRON_DEBUG_DRAGGABLE_REGIONS`。
- **traffic lights 与 `frame: false`。** 需要自定义窗口按钮才用 `frame: false`，代价是失去系统行为（三色按钮交互、双击标题栏缩放等），且要自己处理圆角（`roundedCorners`）与 `trafficLightPosition`。只想要"隐藏标题栏 + 原生按钮"就用 `titleBarStyle: 'hidden'` / `'hiddenInset'`。用 `titleBarOverlay`（Windows/Linux）时，titlebar 内容用 `env(titlebar-area-x, 0px)` / `env(titlebar-area-width, 100%)` 让开系统按钮，不要写死 padding。

## 3. Tauri v2

### 3.1 `src-tauri/tauri.conf.json`

```json
{
  "app": {
    "windows": [{
      "label": "main", "width": 1280, "height": 800,
      "titleBarStyle": "Overlay", "hiddenTitle": true,
      "trafficLightPosition": { "x": 16, "y": 18 },
      "windowEffects": {
        "effects": ["liquidGlassRegular", "underWindowBackground"],
        "state": "followsWindowActiveState", "radius": 24
      }
    }]
  }
}
```

`effects` 里第二个值是 macOS 15 及以下的回退材质：官方说明**一般冲突效果只应用第一个，但 macOS 上可以同时给一个 Liquid Glass 样式和一个 Visual Effect 材质**，让旧系统落到后者。

**只用核心 API。** 社区里的第三方插件（如 `tauri-plugin-liquid-glass` 一类）不是官方 API，版本兼容与 App Store 审核都无法由 Tauri 官方保证；核心 `windowEffects` 已经覆盖 Liquid Glass 与 Visual Effect，先用它，不要为了省几行配置引入插件。

### 3.2 权限（不配就是运行时被拒）

`setEffects` / `clearEffects` 需要 `core:window:allow-set-effects`，它**不在 `core:window:default` 里**。

```json
{
  "$schema": "../gen/schemas/desktop-schema.json",
  "identifier": "main-capability", "windows": ["main"],
  "permissions": ["core:default", "core:window:allow-set-effects"]
}
```

### 3.3 运行时切换（JS）

```js
import { getCurrentWindow, Effect, EffectState } from '@tauri-apps/api/window'
const win = getCurrentWindow()

export async function applyMaterial ({ dark }) {
  await win.setEffects({
    effects: [Effect.LiquidGlassRegular, Effect.UnderWindowBackground],
    state: EffectState.FollowsWindowActiveState,  // 对 Liquid Glass 无效，仅作用于 VisualEffect
    radius: 24
  })
  document.documentElement.dataset.theme = dark ? 'dark' : 'light'  // 与材质同主题
}
export const dropMaterial = () => win.clearEffects()
```

`Effect` 取值（camelCase）：`appearanceBased` / `light` / `dark` / `mediumLight` / `ultraDark`（均 `@deprecated`，macOS 10.14-）、`titlebar`、`selection`、`menu`、`popover`、`sidebar`、`headerView`、`sheet`、`windowBackground`、`hudWindow`、`fullScreenUI`、`tooltip`、`contentBackground`、`underWindowBackground`、`underPageBackground`、**`liquidGlassRegular` / `liquidGlassClear`（macOS 26.0+）**、`mica`、`tabbed` / `tabbedDark` / `tabbedLight`（Windows 11）、`blur`、`acrylic`。`EffectState`：`followsWindowActiveState`、`active`、`inactive`。**已核对的差异**：`micaDark` / `micaLight` 只存在于 `tauri.conf.json` 的 schema 枚举，当前 JS `Effect` 枚举没有这两项 —— 需要它们时只能走配置，不能传给 `setEffects`。

### 3.4 配置要点

- `Effects.state` **对 Liquid Glass 效果无效**（官方注明）；`radius`、`color` 仅 macOS，且 `color` 只影响 Liquid Glass 效果。`interactive`（交互响应式玻璃）标注为 **macOS 27.0+**，默认 `false`。
- 配置里的 `titleBarStyle` 是 **`"Visible" | "Transparent" | "Overlay"`（PascalCase）**；JS API 的 `titleBarStyle` 选项是 **`'visible' | 'transparent' | 'overlay'`（小写）**。两者不一致，混用会静默失效。
- `transparent` 与 `windowEffects` 的官方表述**互相冲突**（JS API 注释说效果"要求窗口 transparent"，配置 schema 说"只需要半透明背景就用 `windowEffects`，它依赖公开 API"）。保守做法：**不要为材质打开 `transparent`** —— macOS 上它需要 `app.macOSPrivateApi: true`（Cargo `macos-private-api`），官方明确警告会导致无法上架 App Store。只有确实需要窗口圆角外透出桌面时才启用。
- `decorations: true` + `titleBarStyle: "Overlay"` 是保留 traffic lights 的组合；`hiddenTitle: true` 隐藏标题文字。`trafficLightPosition` 需要 `titleBarStyle: "Overlay"` 且 `decorations: true`。Windows 上若同时用 decorations/shadow 与 windowEffects，官方指向 tao #72 的 workaround，需实测。

## 4. 降级链

按顺序判定，命中即停；每一级都必须独立保证可读性，**不允许把对比度寄托在透明度上**。

| 级 | 触发条件 | 窗口层 | 页面层 | 可读性保证 |
|---|---|---|---|---|
| L0 | macOS 26.0+ 且 Tauri v2 | `liquidGlassRegular` + `underWindowBackground` 回退 | `html`/`body` 透明；内容区 `--lg-content` | 正文永远落在不透明 `--lg-content`/`--lg-surface` 上，按 `--lg-text` 对 `--lg-surface` 校验（≥4.5:1） |
| L1 | macOS 10.14–15（无 Liquid Glass） | 原生 vibrancy / `underWindowBackground`（Electron `vibrancy` + `visualEffectState`） | 同上 | 同上；材质只出现在 sidebar/titlebar 带，文字另加 `--lg-edge` 边与 `--lg-shadow-light` |
| L2 | Windows 11 22H2+ | `backgroundMaterial: 'mica'` / `mica` | 同上；titlebar 交给 `titleBarOverlay` | 内容区不透明；标题栏文字对最坏情况（浅色壁纸）用 `--lg-text-secondary` 以上 |
| L3 | Windows 10 1903+ | `backgroundMaterial: 'acrylic'` / `acrylic`（噪点重、拖拽卡顿） | 同上，且不使用 `[data-material="clear"]` | 同 L2；`clear` 在任何 Windows 材质上都不允许 |
| L4 | Linux、旧 Windows、材质 API 调用失败 | 无窗口材质，窗口底色用 `--lg-bg` | 退回页面内玻璃：控制层 `[data-material="regular"]`；或直接 `--lg-surface` | `@supports not (backdrop-filter: blur(1px))` 下 `.lg-glass` 落到 `--lg-surface` + `--lg-border` + `--lg-shadow-light` |
| L5 | Reduce Transparency / Increase Contrast / forced-colors | 系统自决（Electron 读 `nativeTheme.prefersReducedTransparency`） | `prefers-reduced-transparency: reduce` → 全部 `backdrop-filter: none`、背景 `--lg-surface` | 层级改由 `--lg-border` / `--lg-border-strong` / `--lg-separator` 表达；焦点环 `--lg-focus-ring` + `--lg-focus-halo` 仍然可见 |

判定顺序是自上而下：L5 是叠加条件（任何一级命中 Reduce Transparency 都要再降一档），不是只在 L4 后才检查。

## 5. DOM / CSS 侧配合

窗口材质之上，页面只负责"透明"，不负责"再玻璃一次"。

```css
html, body { background: transparent; }      /* 硬性：页面不得有任何不透明底 */
.lg-panel, .lg-content-scroll, .lg-sidebar, .lg-inspector {
  background: var(--lg-surface);             /* 内容区永远不透明 */
}
.lg-toolbar {                                /* 贴窗口边缘：只允许透明或不透明 */
  background: transparent;
  -webkit-backdrop-filter: none;             /* 禁止再叠一层 blur */
  backdrop-filter: none;
  border-block-end: 1px solid var(--lg-separator);
}
```

规则：

1. **页面背景透明可判定验证**：`getComputedStyle(document.body).backgroundColor` 必须是 `rgba(0, 0, 0, 0)`；祖先链上任意一层不透明都会让材质失效。
2. **内容层永远不透明**：`.lg-content-scroll`、`.lg-panel`、图表 canvas、表格主体使用 `--lg-content` / `--lg-surface`，不使用任何 `--lg-glass-*`。
3. **控制层玻璃有条件**：只有当元素**下方还有本页自己的内容**时，才用 `.lg-glass` + `[data-material="regular"|"thick"]`；模糊半径与饱和度只从 `--lg-blur-material`（来源于 `--lg-blur-light` / `--lg-blur-regular` / `--lg-blur-thick`）和 `--lg-saturation` 读取。`[data-material="clear"]` 仍须配 `.lg-glass-scrim`（`--lg-scrim`）。菜单/Popover 用 `.lg-menu` / `.lg-popover`，模态用 `.lg-modal` + `--lg-scrim`（`--lg-z-modal` 层级不受窗口材质影响）。
4. **禁止 glass-on-glass**：`.lg-glass`、`[data-material]` 或任何 `backdrop-filter` 不得出现在 `.lg-workspace`、`.lg-toolbar`、`.lg-sidebar`、`.lg-inspector` 这类贴窗口边缘、背后只有原生材质的容器上。它二次模糊已经糊过的结果并二次降饱和，是本 Skill 与 `anti-patterns` 共同禁止项。工具栏因此只有两种合法实现：`background: transparent`（材质直接作底）或 `background: var(--lg-surface)`（完全不透明）。
5. **`color-scheme` 必须与原生材质同主题**：页面根 `color-scheme` 与 `.lg-theme[data-theme]` 由窗口主题驱动，而不是只由 `prefers-color-scheme` 决定 —— 壳内主题可被 `nativeTheme.themeSource` 或窗口 `theme` 覆盖，不一致时会出现浅色材质 + 深色文字的混合态。Electron 读 `nativeTheme.shouldUseDarkColors`；Tauri 用 `getCurrentWindow().theme()` 与 `onThemeChanged`（`allow-theme` 属于 `core:window:default`）。
6. 原生材质只决定窗口底色，**不替代** `--lg-text`、`--lg-surface`、`--lg-radius-*`、`--lg-space-*`、`--lg-control-h-*`、`--lg-sidebar-width` / `--lg-inspector-width` 这套 token；材质切换不应改变布局，过渡只用 `--lg-dur-panel` / `--lg-ease`，不新增时长或缓动 token。

## 6. 可判定验收

**前置：必须真实运行打包或不打包的桌面应用并肉眼+截图核对；在浏览器里预览不算验证，`@supports`/媒体查询通过也不算。** 每项都要给出平台、OS 版本、缩放。

| 场景 | 检查项 | 判定 |
|---|---|---|
| Light / Dark | 窗口底材质可见；正文落在不透明表面上；无灰蒙蒙的"假玻璃" | 截图对比壁纸：材质区域能看到壁纸细节；正文区域对比度 ≥4.5:1；`.lg-theme[data-theme]` 与材质同主题，无浅色材质 + 深色文字 |
| Reduce Transparency 开启 / Increase Contrast / forced-colors | 材质被系统降为不透明；页面所有 `backdrop-filter` 关闭；边界与焦点环仍可见 | 层级仍可辨（靠 `--lg-border` / `--lg-border-strong` / `--lg-separator`）；`:focus-visible` 的 `--lg-focus-ring` + `--lg-focus-halo` 在材质与 `--lg-surface` 上都可辨 |
| 多显示器不同缩放（1x / 2x 混插） | 材质与 1px 边不出现半像素毛边；拖动窗口跨屏后布局与圆角正常 | 监听缩放变化事件（Tauri `onScaleChanged`；Electron `screen` 的 display 变化）后重测 1px 线与 `--lg-radius-lg` |
| 全屏 / 非全屏切换 | 全屏后材质无意义 → 走 §1 例外一，用 `--lg-surface`；退出全屏后恢复 | 切换时无白闪、无残留透明区 |
| 失焦（Electron `visualEffectState: 'inactive'`） | 失焦态下材质变暗/变灰后，其上文字仍可读；titlebar 控件对比度不塌 | 失焦截图里 `--lg-text-secondary` 以上仍 ≥4.5:1 |
| 拖拽区 / 窗口缩放 | 拖拽区内的按钮真的能点；拖拽时不会选中文字；右键不弹自定义菜单；材质窗口仍可调整大小 | 手动点击 titlebar 内每个控件；`app-region: no-drag` 已覆盖全部可交互元素；拖动边缘能改变尺寸（若设了 `transparent: true` 会失败，见 §2.3） |
| 权限（Tauri） | 未加 `core:window:allow-set-effects` 时 `setEffects` 被拒 | DevTools 里 `invoke` 返回权限错误，即证明 capability 生效 |

## 7. 未确证项与验证方法

- **Electron 是否有 Liquid Glass 等价取值：未确证。** 官方当前 `vibrancy` 取值列表中没有 liquid glass 项，第三方绑定（如 `electron-liquid-glass`）不是官方 API。验证：查 Electron 官方 BrowserWindow / BaseWindow 文档的 `vibrancy` 枚举与 release notes 是否新增取值；未新增前不要写 `vibrancy: 'liquidGlassRegular'` —— 无效字符串不会报错，只会静默降级。
- **Electron 中 `vibrancy` 是否必须 `transparent: true`：未确证。** 官方未把 `transparent` 列为 vibrancy 前置条件（Tauri 文档则明确要求透明）。验证：矩形窗口只设 `vibrancy` + 页面 `background: transparent`，若材质透出即不需要；若被盖住，先排查 `html/body` 背景与 `backgroundColor`，最后才考虑 `transparent`。
- **Reduce Transparency 的确切渲染，以及在 Tauri（WKWebView）里如何检测：未确证。** 官方未规定 vibrancy / `windowEffects` 在开启该偏好后的像素结果；WebKit 未实现 `prefers-reduced-transparency`，`@media` 分支在 Tauri 下可能永不命中，且未确证 Tauri v2 是否暴露对应前端 API。验证：先在目标 WebView 实测该媒体查询是否命中；若不命中，用 Rust 侧读 `NSWorkspace.accessibilityDisplayShouldReduceTransparency` 经自定义 command 下发给前端，或接受系统对窗口材质的处理；开/关系统偏好各截图对比并记入项目验收。
- **Windows `backgroundMaterial` 与 `transparent` / decorations 的组合行为：未确证。** 官方只给出 tao #72 的 workaround 链接。验证：在 Windows 11 与 Windows 10 1903+ 上分别测 mica / acrylic / tabbed，记录是否需要 `decorations: false`。

## 来源

- BrowserWindow 与窗口选项（`vibrancy` / `visualEffectState` / `backgroundMaterial` / `titleBarStyle` / `titleBarOverlay`）：https://www.electronjs.org/docs/latest/api/browser-window 、https://www.electronjs.org/docs/latest/api/structures/base-window-options
- 窗口样式与交互（透明/无边框限制、`app-region: drag` / `no-drag`、`ELECTRON_DEBUG_DRAGGABLE_REGIONS`）：https://www.electronjs.org/docs/latest/tutorial/custom-window-styles 、https://www.electronjs.org/docs/latest/tutorial/custom-window-interactions 、https://www.electronjs.org/docs/latest/tutorial/custom-title-bar
- `nativeTheme`（`shouldUseDarkColors`、`prefersReducedTransparency`、`updated`）：https://www.electronjs.org/docs/latest/api/native-theme
- Tauri v2 window JS API（`setEffects` / `clearEffects` / `Effect` / `EffectState`，含 `LiquidGlassRegular`、`LiquidGlassClear`）：https://v2.tauri.app/reference/javascript/api/namespacewindow/ 、https://raw.githubusercontent.com/tauri-apps/tauri/dev/packages/api/src/window.ts
- Tauri v2 权限与 capability（`core:window:allow-set-effects`）：https://v2.tauri.app/reference/acl/core-permissions/ 、https://raw.githubusercontent.com/tauri-apps/tauri/dev/crates/tauri/permissions/window/autogenerated/reference.md 、https://v2.tauri.app/security/capabilities/
- Tauri v2 配置 schema（`windowEffects.effects` 枚举、`TitleBarStyle`、`transparent` / `macOSPrivateApi`）：https://schema.tauri.app/config/2
- Apple 材质与 Liquid Glass：https://developer.apple.com/design/human-interface-guidelines/materials 、https://developer.apple.com/documentation/technologyoverviews/liquid-glass 、https://developer.apple.com/documentation/appkit/nsvisualeffectview/state
