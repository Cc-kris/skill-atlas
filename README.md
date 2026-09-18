# Skill Atlas｜本地 Skill 技能地图

Skill Atlas 是一个面向 Codex、Claude Code、WorkBuddy 和 OpenCode 的本地 Skill 清单扫描器与可视化工具。它会读取当前终端已经安装的 `SKILL.md`，提取技能名称、触发词、说明和路径，并生成一个可以直接用浏览器打开的交互式技能地图。

## 你可以用它做什么

- 一次查看当前终端安装了哪些 Skill
- 以“终端 → 一级分类 → 二级分类 → Skill”的脑图方式浏览
- 从左侧分类列表展开、收起并定位右侧脑图
- 点击 Skill 查看触发词、中文详细说明和本地路径
- 搜索技能名称、说明和触发词
- 识别 Codex、Claude Code、WorkBuddy、OpenCode 或自定义 Skill 根目录
- 在不联网的情况下打开已经生成的 HTML 结果

## 预览

项目内包含一份示例结果：[output/skill-atlas.html](output/skill-atlas.html)。

生成后的页面以当前终端名称为中心，分类向左右两侧展开；一级、二级分类使用发光节点，Skill 使用独立节点。页面不依赖外部 CDN，复制 HTML 后即可离线打开。

## 快速开始

要求：Python 3.11 或更高版本。

```bash
python3 skill-atlas/scripts/build_atlas.py \
  --host codex \
  --output output/skill-atlas.html
open output/skill-atlas.html
```

常用选项：

```text
--host codex|claude-code|workbuddy|opencode|generic
--root PATH              generic 模式下指定 Skill 根目录
--include-project        同时扫描当前项目中的 .agents/skills
--no-ai-label            不调用本机终端模型，只生成结构数据
--open                   生成后尝试用系统默认浏览器打开
```

例如扫描 Claude Code：

```bash
python3 skill-atlas/scripts/build_atlas.py --host claude-code --output output/claude-skills.html
```

## 模型与隐私

当没有使用 `--no-ai-label` 时，中文说明由安装所在终端的默认模型生成：Codex 安装使用 `codex exec`，Claude Code 安装使用 `claude`。程序不会把模型名硬编码成 Gemini，也不会自动把数据发送到其他终端。

扫描默认只读取本地 `SKILL.md`、可选的 `skill.json` 和公开元数据；不会读取密钥、凭据、历史记录或缓存目录。生成的 JSON/HTML 可能包含本机 Skill 路径，请在公开发布前确认路径是否适合分享。

## 目录结构

```text
skill-atlas/
├── SKILL.md              # 可安装到 Codex 的 Skill 入口
├── scripts/              # 扫描、分类、AI 总结和 HTML 构建
├── adapters/             # 不同终端的 Skill 根目录适配器
├── references/           # 主机配置与输出结构说明
├── assets/               # 内置脑图布局库
└── tests/                # 单元测试与扫描 fixture
```

## 安装为 Codex Skill

把 `skill-atlas` 目录复制到 Codex 的 Skill 目录：

```bash
cp -R skill-atlas ~/.codex/skills/skill-atlas
```

重新打开 Codex 会话后即可使用。

## 开发与验证

```bash
python3 -m py_compile skill-atlas/scripts/*.py
python3 -m unittest discover -s skill-atlas/tests -p 'test_*.py'
```

项目不要求安装第三方 Python 依赖；脑图库已随项目内置。

## 当前边界

- Skill 的触发词只从源文件明确出现的 frontmatter、触发字段、`$命令` 和反引号命令中提取，不会凭空创造。
- 分类是基于 Skill 自身名称、描述、标题和触发词生成的语义分组；带有明确命名空间的 Skill（例如 `[OMX]`）会优先保持在同一一级分类下。
- AI 总结需要当前终端的 CLI 已安装并且可用；不可用时可以使用 `--no-ai-label` 生成结构化结果。

## 许可证

本项目暂未指定开源许可证。若要在项目外分发或二次开发，请先联系仓库维护者确认授权。
