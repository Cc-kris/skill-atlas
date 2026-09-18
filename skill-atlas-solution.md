# Skill Atlas：跨终端 Skill 动态盘点与脑图方案

| 项目 | 内容 |
| --- | --- |
| 文档版本 | v0.1 |
| 日期 | 2026-09-16 |
| 状态 | 方案确认，待实现 |
| 目标产物 | 一个可分别安装到不同终端/桌面端的 skill |
| 默认输出 | 本地、离线可打开的静态 HTML |

## 1. 背景

需要开发一个 skill，用于罗列当前终端或桌面端已经安装的 skills，根据当前集合动态归纳分类，并生成一份可交互的 skill 脑图。页面需要能展示分类、二级分类、skill 名称，以及每个 skill 的简短用途说明，整体风格应具有开发者工具和数据可视化产品的质感。

该 skill 可能被安装到 Codex、Claude Code、WorkBuddy、OpenCode 等不同宿主中。它们共享一套实现，不维护四套独立代码；运行时自动识别当前宿主，只读取当前宿主的 skill，不混入其他终端的数据。

当前环境已确认存在以下代表性来源：

- Codex：`~/.codex/skills`
- Claude Code：`~/.claude/skills`
- 共享 skill：`~/.agents/skills`
- Gemini 目录目前未发现明确的标准 skill 目录，因此不作为默认扫描源

这些来源主要使用 `SKILL.md`，其 YAML frontmatter 中通常包含 `name` 和 `description`，正文还可能提供触发词、能力说明和使用场景。

## 2. 设计目标

### 2.1 功能目标

1. 一套代码、一个 skill 包，适配多个终端或桌面端。
2. 安装后自动识别当前宿主。
3. 默认只扫描当前宿主的白名单目录。
4. 解析 skill 元数据并生成统一数据模型。
5. 根据当前 skill 集合动态归纳分类，不使用固定业务分类表。
6. 当某个分类超过 10 个 skill 时自动拆分二级分类，必要时支持三级分类。
7. 生成完全自包含、无需联网的 HTML 页面。
8. 支持搜索、筛选、展开、折叠、缩放、拖拽和 skill 详情查看。
9. 单个损坏或格式不完整的 skill 不应导致全量扫描失败。

### 2.2 非目标

第一版不做以下事情：

- 不扫描整个 Home 目录来猜测所有终端。
- 不自动安装、修改、删除或升级其他 skill。
- 不读取 API key、认证文件、历史会话或完整脚本内容。
- 不将本地 skill 上传到外部服务。
- 不依赖常驻 Web 服务、数据库或 CDN。
- 不把分类结果写回原始 skill 文件。
- 不默认抓取在线 marketplace 或远程仓库。

## 3. 核心原则

### 3.1 宿主隔离

安装同一个 skill 后，由运行时探测当前宿主并启用对应 adapter。每次只使用一个确定的扫描根目录，避免 Codex 页面出现 Claude Code 的 skill。

如果无法可靠判断宿主，应 fail closed：提示用户使用 `--host codex`、`--host claude-code` 等显式参数，而不是扩大扫描范围。

### 3.2 动态分类

分类名称来自当前发现的 skill 内容，固定的只有分类算法、阈值和安全规则。换一个终端或换一批 skill，分类名称和层级可以不同。

### 3.3 静态交付

默认产物是一个包含 CSS、JavaScript 和 JSON 数据的单文件 HTML。用户可以直接双击打开、归档或分享，不需要启动服务，也不依赖网络。

### 3.4 可解释与可恢复

每个分类应能追溯到所包含的 skill；每个解析异常都记录为 warning；生成失败时保留扫描 JSON，便于定位问题和重建页面。

## 4. 用户工作流

默认触发示例：

```text
生成当前终端的 skill 脑图
盘点我的 skill
更新 skill atlas
查看当前 skill 分类
```

执行流程：

```text
识别当前宿主
  -> 校验唯一的扫描根目录
  -> 扫描 SKILL.md 和可选 skill.json
  -> 提取元数据和摘要
  -> 动态聚类与命名
  -> 超过 10 个时递归拆分
  -> 生成 atlas.json
  -> 内嵌数据并生成静态 HTML
  -> 返回 HTML 路径和统计摘要
```

可选参数：

```text
--host <codex|claude-code|workbuddy|opencode>
--output <path>
--include-project
--no-ai-label
--open
--refresh
```

## 5. 总体架构

```text
SKILL.md
    |
    v
Host Detector
    |
    v
Host Adapter
    |
    v
Scanner + Metadata Extractor
    |
    v
Normalized SkillRecord[]
    |
    v
Dynamic Classifier
    |
    v
Atlas JSON
    |
    v
Static HTML Renderer
```

### 5.1 Host Detector

建议按以下顺序识别：

1. 当前宿主提供的环境变量或运行上下文。
2. skill 的安装位置。
3. 已知宿主配置文件。
4. 宿主目录特征。
5. 用户显式指定的 `--host`。

自动识别得到高置信度结果后才继续。低置信度或多个宿主同时命中时停止并要求显式指定。

### 5.2 Host Adapters

adapter 只负责宿主差异，不包含扫描、分类或渲染逻辑：

```python
class HostAdapter:
    host_name: str
    def discover_roots(self) -> list[str]: ...
    def discover_files(self, root: str) -> list[str]: ...
    def normalize_scope(self, path: str) -> str: ...
```

建议内置：

- `CodexAdapter`
- `ClaudeCodeAdapter`
- `WorkBuddyAdapter`
- `OpenCodeAdapter`
- `GenericAdapter`，用于用户显式提供的自定义 skill 根目录

WorkBuddy 和 OpenCode 的实际目录若因版本或安装方式不同，应通过配置注入，而不是写死未经验证的路径。

## 6. 扫描与统一数据模型

扫描器只读取：

- `SKILL.md`
- 可选的 `skill.json`
- 可选的宿主元数据文件

不读取脚本正文作为分类输入，不执行 skill 内的脚本。

标准记录示例：

```json
{
  "id": "codex:skill-creator",
  "name": "skill-creator",
  "displayName": "Skill Creator",
  "host": "codex",
  "scope": "user",
  "path": "~/.codex/skills/.system/skill-creator/SKILL.md",
  "description": "Create or update Codex skills",
  "triggers": ["create skill", "update skill"],
  "summary": "用于创建和更新 Codex skill 的流程指导",
  "category": "Skill 开发",
  "level": 1,
  "status": "valid",
  "warnings": []
}
```

处理要求：

- frontmatter 缺失时使用目录名和 Markdown 标题作为降级值。
- YAML 解析失败时保留文件记录，并添加 warning。
- 使用真实路径去重，但不同宿主中的同名 skill 不能互相覆盖。
- HTML 中显示缩短后的路径，不展示不必要的用户目录细节。
- 保证同一批输入的记录和分类顺序稳定。

## 7. 动态分类与递归拆分

### 7.1 分类输入

仅使用低敏感度文本：

- skill 名称
- description
- triggers
- Markdown 一级和二级标题
- 已存在的公开 metadata 标签

### 7.2 分类模式

默认模式为纯本地处理：

```text
文本归一化
  -> 关键词提取
  -> TF-IDF 或等价的本地相似度计算
  -> 聚类
  -> 根据聚类关键词生成分类名
```

可选增强模式由当前宿主模型辅助生成分类名称和摘要。增强模式只发送名称、描述、触发词和标题摘要，不发送完整脚本、认证内容或本地密钥。

### 7.3 层级规则

```text
分类包含 1～10 个 skill：直接展示 skill
分类包含 11 个及以上 skill：拆分为二级分类
二级分类仍超过 10 个：继续拆分
最大深度：三级
```

保护条件：

- 子分类至少包含 2 个 skill。
- 无法形成有意义子类时，保留“其他”。
- 分类结果显示每层节点数量。
- 分类名称、层级和成员记录在 HTML 快照中，便于复核。

## 8. HTML 交互与视觉方案

页面定位为深色的开发者工具控制台，而不是普通树状列表。

```text
┌─────────────────────────────────────────────┐
│ Skill Atlas · Codex · 54 skills              │
│ 搜索   分类筛选   状态筛选   重置视图         │
├──────────────┬──────────────────────────────┤
│ 分类统计      │                              │
│ 节点图例      │        交互式脑图画布          │
│               │                              │
├──────────────┴──────────────────────────────┤
│ 当前选中 skill 的详情面板                     │
└─────────────────────────────────────────────┘
```

交互要求：

- 分类节点可以展开和折叠。
- skill 支持名称、描述、触发词搜索。
- 支持按分类、状态和层级筛选。
- 点击节点打开详情面板。
- 支持缩放、拖拽、聚焦和重置视图。
- 节点过多时默认折叠分类，避免初始画布不可读。
- 移动端改为分类列表加详情抽屉，避免横向溢出。
- 所有图标按钮提供可访问名称，支持键盘操作。
- 遵循 `prefers-reduced-motion`，动画不能影响信息读取。

实现建议使用原生 SVG、CSS 和 JavaScript，不引入运行时依赖，不使用 CDN，不依赖外部图片或字体。

## 9. 推荐目录结构

```text
skill-scanner/
└── skill-atlas/
    ├── SKILL.md
    ├── agents/
    │   └── openai.yaml
    ├── scripts/
    │   ├── detect_host.py
    │   ├── scan_skills.py
    │   ├── extract_metadata.py
    │   ├── classify_skills.py
    │   └── build_html.py
    ├── adapters/
    │   ├── base.py
    │   ├── codex.py
    │   ├── claude_code.py
    │   ├── workbuddy.py
    │   ├── opencode.py
    │   └── generic.py
    ├── assets/
    │   ├── atlas-template.html
    │   ├── atlas.css
    │   └── atlas.js
    ├── references/
    │   ├── host-profiles.yaml
    │   └── output-schema.json
    └── tests/
        ├── fixtures/
        ├── test_detector.py
        ├── test_scanner.py
        ├── test_classifier.py
        └── test_html.py
```

该目录是实现规划，不代表本次已经创建了 skill 代码。

## 10. 安全与隐私

- 只访问当前宿主 adapter 返回的白名单目录。
- 明确排除 `auth.json`、凭据目录、历史记录、缓存和备份目录。
- 不执行被扫描 skill 的脚本。
- 不在 HTML 中输出完整敏感路径。
- AI 增强分类默认关闭。
- 任何外部模型调用都应在页面和终端输出中明确提示。
- 无法识别宿主时 fail closed。
- 扫描异常只记录文件路径、错误类型和可公开元数据，不记录文件全文。

## 11. 实施顺序

1. 使用 `skill-creator` 规范初始化 skill 目录和元数据。
2. 实现统一 `SkillRecord` 和 frontmatter 降级解析。
3. 实现宿主探测与 Codex adapter。
4. 实现动态聚类、分类命名和超过 10 个节点的递归拆分。
5. 实现自包含 HTML、SVG 脑图、搜索和详情面板。
6. 用当前 Codex 环境生成第一份真实快照。
7. 增加 Claude Code adapter，并用 Claude skill 验证宿主隔离。
8. 增加 WorkBuddy、OpenCode 的可配置 adapter。
9. 增加移动端、键盘操作和异常输入测试。
10. 最后补充可选的模型增强分类模式。

## 12. 验证方案

### 12.1 单元测试

- frontmatter 正常、缺失和损坏输入。
- 同名 skill 的跨宿主去重边界。
- 备份目录和迁移目录排除。
- 宿主检测的高置信度、冲突和未知状态。
- 10、11、超过 20 个 skill 时的递归拆分。
- 空目录和无可解析 skill 的结果。
- 分类结果排序稳定性。

### 12.2 集成测试

- Codex 安装版只读取 `~/.codex/skills`。
- Claude Code 安装版只读取 `~/.claude/skills`。
- 显式 `--host` 能覆盖自动探测结果。
- 单个损坏文件不会阻断其他 skill。
- 生成 HTML 后 JSON、节点数量和分类数量一致。

### 12.3 浏览器验证

使用 Playwright 检查：

- 桌面端页面实际渲染，画布非空。
- 搜索和筛选后节点正确隐藏或显示。
- 点击分类和 skill 能打开详情。
- 缩放、拖拽和重置视图正常。
- 移动端无横向溢出，详情抽屉不遮挡核心内容。
- 离线打开时页面仍可用。

## 13. 验收标准

以下条件全部满足才视为 MVP 完成：

- 同一个 skill 包可以安装到至少两个宿主。
- 每个宿主只展示自身 skill，不混入其他终端。
- 分类名称来自当前 skill 集合，而非预设固定分类。
- 分类超过 10 个时自动产生二级分类。
- 生成 HTML 不需要网络或常驻服务。
- 页面可搜索、筛选、展开、折叠、缩放并查看详情。
- 解析异常可见但不阻断全量结果。
- 不读取、不执行、不输出认证数据和密钥。
- 同样的输入能够生成稳定的节点顺序和层级结果。
- 桌面端和移动端均通过实际浏览器检查。

## 14. 风险与回滚点

| 风险 | 处理方式 | 回滚点 |
| --- | --- | --- |
| 宿主无法可靠识别 | fail closed，要求 `--host` | 暂时仅支持显式宿主参数 |
| 不同宿主的 SKILL.md 格式差异 | adapter 内做格式兼容 | 回退到通用 frontmatter 解析 |
| 本地聚类分类名不自然 | 保留聚类结果，改进命名器或启用模型增强 | 使用“未分类/其他” |
| skill 数量过多导致画布拥挤 | 默认折叠、递归分类、列表降级 | 只展示分类节点和详情列表 |
| 分类每次变化过大 | 稳定排序、固定参数、保存快照 | 使用上次分类结果作为人工覆盖 |
| 外部模型带来隐私风险 | 默认关闭，限制发送字段 | 完全使用本地模式 |

## 15. 后续增强

MVP 稳定后再考虑：

- `--watch` 监视 skill 目录并重新生成快照。
- `--serve` 启动本地开发服务器。
- 分类结果人工编辑和 override 文件。
- 两次快照之间的新增、删除和变更对比。
- 导出 PNG、SVG 或 Markdown 索引。
- 扫描远程 skill 仓库，但必须由用户显式指定并单独展示远程来源。

## 16. 最终结论

推荐实现为“一套核心代码 + 多个轻量宿主 adapter + 运行时自动识别 + 当前宿主白名单扫描 + 动态分类 + 本地静态 HTML”。

这样既满足跨 Codex、Claude Code、WorkBuddy、OpenCode 等终端复用，又能确保每个终端看到的只是自身 skill；分类不会被固定枚举限制，并能在分类过密时自动建立二级结构。第一阶段应先实现 Codex 版真实闭环，再用 Claude Code 做隔离验证，最后接入其他宿主的路径适配。
