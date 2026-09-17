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

## 8. Headless UI / Radix / Ark 等

这类库已经处理大量交互语义。保留：

- focus management
- keyboard navigation
- dismiss behavior
- portal
- aria

只替换 visual layer，不要因为自定义玻璃重新手写一套 dialog/menu/listbox 行为。

## 9. ECharts / Chart.js / D3

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

## 10. Electron / Tauri

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

## 11. 渐进迁移

大型旧项目按顺序：

1. tokens；
2. page shell / scroll ownership；
3. toolbar/sidebar；
4. button/input focus states；
5. dialog/drawer/popover；
6. data display；
7. polish。

不要一次 PR 重写所有页面。

## 12. Review checklist

- 是否复用了现有组件库？
- 是否避免全局 `!important`？
- 是否避免深度绑定组件库内部 DOM？
- 是否保留 keyboard/ARIA？
- 是否只在 control/navigation layer 用 blur？
- 是否有 fallback？
- 是否真实验证 resize / short viewport / 200%？
- 是否没有为了换肤改业务逻辑？
