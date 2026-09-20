"""Stable semantic grouping with explicit parent/child category fields."""

from __future__ import annotations

import re
from collections import Counter, defaultdict

from atlas_model import SkillRecord
STOPWORDS = {
    "skill", "skills", "the", "and", "for", "with", "from", "when", "this", "that", "use", "useful",
    "create", "update", "help", "支持", "用于", "进行", "以及", "当前", "一个", "通过", "的", "和", "与",
    "omx", "codex", "skill", "skills", "local", "use", "when", "user", "agent", "current", "支持", "用于",
}

def _terms(skill: SkillRecord) -> str:
    return " ".join([skill.name, skill.description, *skill.triggers, *skill.headings]).lower()

FAMILY_RULES = [
    ("浏览器与自动化", "浏览器自动化", ("__name__:playwright", "__name__:screenshot")),
    ("技能管理", "安装与更新", ("__name__:skill-installer", "__name__:skill-creator", "__name__:skill-atlas")),
    ("设计", "图像生成", ("__name__:imagegen", "__name__:image-realism-enhancer", "__name__:ian-xiaohei-illustrations")),
    ("开发与运维", "上游同步", ("__name__:sub2api-upstream-sync", "__name__:cloudflare-deploy", "__name__:vercel-deploy")),
    ("规划与架构", "项目扫描", ("project-scan", "project scan", "代码库扫描", "陌生代码库")),
    ("交付与复盘", "经验沉淀", ("retrospective", "复盘", "经验沉淀", "memory")),
    ("设计", "产品设计", ("product design", "product-design", "产品设计", "design system")),
    ("设计", "UI 设计", ("ui", "frontend", "component", "界面", "前端")),
    ("设计", "UX 设计", ("ux", "user experience", "interaction", "用户体验", "交互")),
    ("设计", "视觉设计", ("visual", "brand", "banner", "illustration", "视觉", "品牌")),
    ("图像与媒体", "图像生成", ("imagegen", "image generation", "生图")),
    ("图像与媒体", "图像处理", ("image", "screenshot", "图片")),
    ("代码开发", "代码质量", ("review", "debug", "test", "qa", "评审", "调试")),
    ("代码开发", "开发实现", ("code", "coding", "frontend", "编程")),
    ("文档与写作", "文档处理", ("document", "pdf", "markdown", "文档")),
    ("文档与写作", "文章写作", ("article", "writing", "write", "写作")),
    ("研究与搜索", "研究分析", ("research", "search", "analysis", "研究", "搜索")),
    ("规划与架构", "规划需求", ("plan", "planning", "requirement", "需求")),
    ("规划与架构", "技术架构", ("architecture", "架构")),
    ("部署与运维", "部署发布", ("deploy", "cloud", "vercel", "cloudflare", "部署")),
    ("协作与自动化", "流程自动化", ("workflow", "automation", "pipeline", "autopilot", "流程")),
    ("协作与自动化", "团队协作", ("team", "worker", "协作")),
    ("平台与插件", "插件安装", ("plugin", "install", "插件", "安装")),
    ("浏览器与数据", "浏览器自动化", ("browser", "playwright", "浏览器")),
]

# OMX is an ecosystem namespace, so its skills stay under one top-level node;
# this explicit map only chooses the meaningful second-level branch.
OMX_CHILDREN = {
    "autopilot": "执行与编排", "ultragoal": "执行与编排", "ultrawork": "执行与编排",
    "ralph": "执行与编排", "ralplan": "执行与编排", "team": "执行与编排",
    "worker": "执行与编排", "pipeline": "执行与编排",
    "design": "设计工具", "visual-ralph": "设计工具", "impeccable": "设计工具",
    "ui-ux-pro-max": "设计工具", "zelda-hyrule-ui-style": "设计工具",
    "analyze": "质量与分析", "code-review": "质量与分析", "ai-slop-cleaner": "质量与分析",
    "bug-root-cause": "质量与分析", "self-review": "质量与分析", "ultraqa": "质量与分析",
    "beta-review": "质量与分析",
    "plan": "规划与需求", "deep-interview": "规划与需求", "prometheus-strict": "规划与需求",
    "architecture-design": "规划与需求", "requirement-analysis": "规划与需求",
    "project-scan": "规划与需求", "prd-writer": "规划与需求",
    "doctor": "配置与维护", "omx-setup": "配置与维护", "hud": "配置与维护",
    "configure-notifications": "配置与维护", "cancel": "配置与维护", "skill": "配置与维护",
    "ask": "顾问咨询",
    "autoresearch": "研究与优化", "autoresearch-goal": "研究与优化",
    "best-practice-research": "研究与优化", "performance-goal": "研究与优化",
}



def _tokens(skill: SkillRecord) -> list[str]:
    return re.findall(r"[A-Za-z][A-Za-z0-9_-]{1,}", " ".join([skill.name, skill.description, *skill.triggers, *skill.headings]).lower())


def _label(tokens: list[str], fallback: str = "综合技能") -> str:
    if not tokens:
        return fallback
    top = Counter(tokens).most_common(2)
    translated = [LABELS.get(item[0]) for item in top]
    known = [item for item in translated if item]
    return known[0] if known else fallback

def _family(skill: SkillRecord) -> tuple[str, str]:
    text = _terms(skill)
    name_key = f"__name__:{skill.name.lower()}"
    for family, child, terms in FAMILY_RULES[:4]:
        if name_key in terms:
            return family, child
    for family, child, terms in FAMILY_RULES[4:]:
        if any(term in text for term in terms):
            return family, child
    return "技能管理", "技能整理"


def _namespace_child(namespace: str, skill: SkillRecord) -> str:
    if namespace == "OMX":
        return OMX_CHILDREN.get(skill.name.lower(), "执行与编排")
    return _family(skill)[1]


def classify(skills: list[SkillRecord], max_depth: int = 3) -> list[SkillRecord]:
    if not skills:
        return skills
    # Preserve explicit ecosystem namespaces before semantic clustering.  These
    # markers are stronger than incidental prose overlap (for example every
    # `[OMX]` skill belongs together).
    namespaces: dict[str, list[SkillRecord]] = defaultdict(list)
    remainder: list[SkillRecord] = []
    for skill in skills:
        marker = re.search(r"\[([^\]]+)\]", skill.description)
        if marker and re.fullmatch(r"[A-Za-z][A-Za-z0-9_-]{1,20}", marker.group(1).strip()):
            namespaces[marker.group(1).strip().upper()].append(skill)
        else:
            remainder.append(skill)
    buckets: dict[str, list[SkillRecord]] = defaultdict(list)
    skills_for_clustering = remainder
    # Use compact deterministic semantic buckets. Namespace remains the parent node.
    token_sets = {skill.id: _tokens(skill) for skill in skills_for_clustering}
    ordered = sorted(skills_for_clustering, key=lambda s: s.id)
    for skill in ordered:
        family, child = _family(skill)
        buckets[(family, child)].append(skill)
    for namespace, members in namespaces.items():
        for member in members:
            child = _namespace_child(namespace, member)
            member.category = namespace.upper()
            member.parent_category = child
            member.level = 2
    for (category, child), members in sorted(buckets.items()):
        for member in members:
            member.category, member.parent_category, member.level = category, child, 2
    return sorted(skills, key=lambda item: (item.category.casefold(), item.name.casefold(), item.id))


def _assign_group(members: list[SkillRecord], category: str, level: int, max_depth: int, token_sets: dict[str, list[str]], parent: str = "") -> None:
    for member in members:
        member.category = category
        member.parent_category = parent
        member.level = level
