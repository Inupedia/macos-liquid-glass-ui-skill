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
secondary text       -> --lg-muted
separator            -> --lg-separator
accent               -> --lg-accent
control glass        -> --lg-glass-regular
floating glass       -> --lg-glass-thick / clear
```

已有品牌色优先。只有用户明确要求完整换肤时才替换 accent。

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
  background: var(--lg-glass-regular);
  border: 1px solid var(--lg-glass-edge);
  backdrop-filter: blur(var(--lg-blur)) saturate(140%);
  -webkit-backdrop-filter: blur(var(--lg-blur)) saturate(140%);
}
```

必须提供不支持 backdrop-filter 和 reduce transparency 的 solid fallback。

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

容器 resize：

- 监听实际 container；
- sidebar/inspector 改变后重新测量；
- hidden -> visible 后再初始化/resize；
- dispose/cleanup listener。

## 11. Electron / Tauri

使用本 Web Skill 做内容 UI，但区分：

- app content chrome
- real native window controls

如果项目真的自定义 titlebar/window buttons，它们必须连接真实窗口 API；否则不要添加装饰性 traffic lights。

同时验证：

- drag region；
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

不要一次 PR 重写所有页面。

## 13. Review checklist

- 是否复用了现有组件库？
- 是否避免全局 `!important`？
- 是否避免深度绑定组件库内部 DOM？
- 是否保留 keyboard/ARIA？
- 是否只在 control/navigation layer 用 blur？
- 是否有 fallback？
- 如果使用 Inspira UI，是否只是必要的增强而非整页炫技？
- Inspira 持续动画是否有 reduced-motion / performance fallback？
- 是否真实验证 resize / short viewport / 200%？
- 是否没有为了换肤改业务逻辑？
