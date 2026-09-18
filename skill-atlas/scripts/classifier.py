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

LABELS = {"code":"代码","coding":"代码","review":"评审","debug":"调试","design":"设计","ui":"界面","ux":"体验","frontend":"前端","visual":"视觉","image":"图像","illustration":"插图","document":"文档","documents":"文档","write":"写作","writing":"写作","article":"文章","markdown":"文档","pdf":"文档","presentation":"演示","slides":"演示","data":"数据","analytics":"分析","dashboard":"看板","report":"报告","metric":"指标","project":"项目","plan":"规划","planning":"规划","requirement":"需求","architecture":"架构","task":"任务","team":"协作","workflow":"流程","search":"搜索","research":"研究","source":"资料","web":"网络","deploy":"部署","cloud":"云服务","doctor":"诊断","performance":"性能","upstream":"同步","automation":"自动化","autopilot":"自动化","pipeline":"流水线","worker":"执行","lark":"飞书","calendar":"日程","mail":"邮件","wiki":"知识库","security":"安全","test":"测试","browser":"浏览器","plugin":"插件","install":"安装","generate":"生成","render":"渲染","openai":"模型","pdf":"文档","imagegen":"生图"}



def _tokens(skill: SkillRecord) -> list[str]:
    return re.findall(r"[A-Za-z][A-Za-z0-9_-]{1,}", " ".join([skill.name, skill.description, *skill.triggers, *skill.headings]).lower())


def _label(tokens: list[str], fallback: str = "综合技能") -> str:
    if not tokens:
        return fallback
    top = Counter(tokens).most_common(2)
    translated = [LABELS.get(item[0]) for item in top]
    known = [item for item in translated if item]
    return known[0] if known else fallback


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
        words = _tokens(skill)
        label = _label(words, "综合技能")
        buckets[label].append(skill)
    for namespace, members in namespaces.items():
        for member in members:
            member.category = namespace.upper()
            member.parent_category = _label(_tokens(member), "综合技能")
            member.level = 2
    for category, members in sorted(buckets.items()):
        for member in members:
            member.category, member.parent_category, member.level = category, "", 1
    for category, members in list(buckets.items()):
        if len(members) <= 10: continue
        for member in members:
            member.parent_category, member.level = _label(_tokens(member), "综合技能"), 2
    return sorted(skills, key=lambda item: (item.category.casefold(), item.name.casefold(), item.id))


def _assign_group(members: list[SkillRecord], category: str, level: int, max_depth: int, token_sets: dict[str, list[str]], parent: str = "") -> None:
    for member in members:
        member.category = category
        member.parent_category = parent
        member.level = level
