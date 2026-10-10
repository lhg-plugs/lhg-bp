#!/usr/bin/env python3
"""lhg-bp 商业计划书确定性审计脚本。

检查 Markdown 格式的 BP 草稿：
  BP-SEC-001   blocker  必需章节缺失
  BP-NUM-001   warning  市场规模数字前后矛盾
  BP-HOLLOW-001 warning 空洞表述（无证据的断言）
  BP-FIN-001   warning  财务数字勾稽矛盾
  BP-CON-001   warning  融资需求章缺资金用途明细

用法：
  python3 bp_audit.py --target <BP草稿.md> --format json|text
退出码：0=无 blocker（只有 warning 也通过），1=有 blocker。

纯标准库，零第三方依赖。
"""

import argparse
import json
import re
import sys


# 必需章节：章节名 → 标题关键词列表（二级标题匹配）
REQUIRED_SECTIONS = [
    ("封面/项目概述", ["封面", "项目概述", "一句话介绍", "项目简介"]),
    ("痛点与机会", ["痛点", "机会", "为什么现在", "问题"]),
    ("市场分析", ["市场", "TAM", "SAM", "SOM", "规模"]),
    ("产品与方案", ["产品", "方案", "解决", "功能"]),
    ("商业模式", ["商业模式", "盈利模式", "怎么赚钱", "收费"]),
    ("竞争与壁垒", ["竞争", "壁垒", "护城河", "对手", "竞品"]),
    ("团队", ["团队", "创始人", "核心成员"]),
    ("财务预测", ["财务", "营收", "利润", "预测"]),
    ("融资需求", ["融资", "资金", "出让", "估值"]),
]

# 空洞表述：出现即 warning（除非同段有"数据/测算/来源"类证据词）
HOLLOW_WORDS = [
    "行业领先", "颠覆性", "独角兽", "全球首创", "革命性",
    "独家垄断", "碾压", "万亿赛道唯一", "前无古人",
]

NUM_RE = re.compile(r"(\d+(?:\.\d+)?)\s*(万|亿|万亿)\s*(?:元|美元|人|家|次)?")
# 市场口径标签：TAM/SAM/SOM 分层分别校验，不跨层比较
LAYER_RE = re.compile(r"(市场规模|TAM|SAM|SOM|整体市场|赛道规模)\s*(?:约|达|为|是)?\s*(\d+(?:\.\d+)?)\s*(万|亿|万亿)")
MARKET_KW = ["市场规模", "TAM", "SAM", "SOM", "整体市场", "赛道规模"]

# 财务勾稽：同一行里"营收X亿…成本Y亿…利润Z亿"
FIN_RE = re.compile(
    r"(?:营收|收入)\s*(\d+(?:\.\d+)?)\s*亿.*?成本\s*(\d+(?:\.\d+)?)\s*亿"
    r".*?(?:利润|净利润)\s*(\d+(?:\.\d+)?)\s*亿"
)


def _read(path):
    try:
        with open(path, encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return None


def _headings(text):
    """返回 [(level, title, line_no)]"""
    out = []
    for i, ln in enumerate(text.split("\n"), 1):
        m = re.match(r"^(#{1,3})\s+(.+?)\s*$", ln)
        if m:
            out.append((len(m.group(1)), m.group(2).strip(), i))
    return out


def check_sections(text):
    heads = _headings(text)
    titles = [t for _, t, _ in heads]
    missing = []
    for sec_name, kws in REQUIRED_SECTIONS:
        if not any(any(k in t for k in kws) for t in titles):
            missing.append(sec_name)
    findings = []
    for sec in missing:
        findings.append({
            "rule_id": "BP-SEC-001",
            "severity": "blocker",
            "title": "必需章节缺失：%s" % sec,
            "line": 0,
            "detail": "投资人翻 BP 先看结构，缺一章就少一分信任。补上「%s」章节再往下走。" % sec,
        })
    return findings


def check_market_numbers(text):
    """同口径（TAM/SAM/SOM/市场规模）出现多个不同数值 → warning"""
    values = {}  # metric -> {num_yi: line_no}
    for i, ln in enumerate(text.split("\n"), 1):
        if not any(k in ln for k in MARKET_KW):
            continue
        for m in LAYER_RE.finditer(ln):
            label, num, unit = m.group(1), float(m.group(2)), m.group(3)
            num_yi = num * 10000 if unit == "万亿" else (num if unit == "亿" else num / 10000)
            metric = "SOM口径" if label == "SOM" else (
                "SAM口径" if label == "SAM" else "TAM口径")
            values.setdefault(metric, {})[round(num_yi, 2)] = i
    findings = []
    for metric, val_lines in values.items():
        if len(val_lines) > 1:
            vals = sorted(val_lines)
            findings.append({
                "rule_id": "BP-NUM-001",
                "severity": "warning",
                "title": "%s数字前后矛盾：%s" % (metric, " / ".join(
                    "%g亿(第%d行)" % (v, val_lines[v]) for v in vals)),
                "line": 0,
                "detail": "同一份 BP 里同一口径的市场规模写出两个数，投资人会直接质疑数据真实性。统一口径并注明来源与年份。",
            })
    return findings


def check_hollow(text):
    findings = []
    evidence_re = re.compile(r"(数据|测算|来源|调研|财报|占比|同比|环比|\d+%)")
    for i, ln in enumerate(text.split("\n"), 1):
        for w in HOLLOW_WORDS:
            if w in ln and not evidence_re.search(ln):
                findings.append({
                    "rule_id": "BP-HOLLOW-001",
                    "severity": "warning",
                    "title": "空洞表述：%s（第%d行）" % (w, i),
                    "line": i,
                    "detail": "「%s」没有证据支撑就是自嗨。要么删掉，要么在同段给出数据/来源/测算。" % w,
                })
                break  # 一行只报一次
        if len(findings) >= 10:
            break
    return findings


def check_finance(text):
    findings = []
    for i, ln in enumerate(text.split("\n"), 1):
        m = FIN_RE.search(ln)
        if not m:
            continue
        rev, cost, profit = (float(m.group(1)), float(m.group(2)), float(m.group(3)))
        if abs(rev - cost - profit) > max(0.05 * rev, 0.1):
            findings.append({
                "rule_id": "BP-FIN-001",
                "severity": "warning",
                "title": "财务勾稽矛盾（第%d行）：营收%g亿−成本%g亿≠利润%g亿" % (i, rev, cost, profit),
                "line": i,
                "detail": "投资人 10 秒就能验算出这个错。核对：利润口径（毛利/净利）与成本口径是否一致。",
            })
    return findings


def check_fund_use(text):
    """融资需求章存在，但没写资金用途明细 → warning"""
    heads = _headings(text)
    has_fund = any(any(k in t for k in ("融资", "资金", "出让")) for _, t, _ in heads)
    if not has_fund:
        return []
    if "资金用途" not in text and "怎么花" not in text:
        return [{
            "rule_id": "BP-CON-001",
            "severity": "warning",
            "title": "融资需求章缺资金用途明细",
            "line": 0,
            "detail": "只写「融多少钱、出让多少」不够。投资人要看到「钱怎么花」（研发x%/市场x%/团队x%），缺了就是融资章半成品。",
        }]
    return []


RULES = [
    check_sections,
    check_market_numbers,
    check_hollow,
    check_finance,
    check_fund_use,
]


def audit(text):
    findings = []
    for rule in RULES:
        findings.extend(rule(text))
    summary = {"blocker": 0, "warning": 0, "nit": 0}
    for f in findings:
        summary[f["severity"]] = summary.get(f["severity"], 0) + 1
    return {"findings": findings, "summary": summary}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", required=True)
    ap.add_argument("--format", choices=["json", "text"], default="text")
    args = ap.parse_args()

    text = _read(args.target)
    if text is None:
        print("无法读取目标文件：%s" % args.target, file=sys.stderr)
        return 2
    result = audit(text)
    if args.format == "json":
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print("lhg-bp 审计：%s" % args.target)
        print("blocker=%d warning=%d nit=%d" % (
            result["summary"]["blocker"], result["summary"]["warning"],
            result["summary"]["nit"]))
        for f in result["findings"]:
            print("[%s][%s] %s" % (f["severity"], f["rule_id"], f["title"]))
            if f["line"]:
                print("    第%d行" % f["line"])
            print("    %s" % f["detail"])
    return 1 if result["summary"]["blocker"] else 0


if __name__ == "__main__":
    sys.exit(main())
