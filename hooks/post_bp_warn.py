#!/usr/bin/env python3
"""lhg-bp 硬门②：写入 BP 草稿后提醒跑投资人体检。

触发：PostToolUse / Write|Edit。只在写入的 .md 内容看起来像 BP 草稿
（含"商业计划书"/"BP"/"融资需求"关键词）时才输出提醒；其余 0 开销放行。

逃生方式：LHG_BP_HOOKS_OFF=1（本次 hook 直接放行，不输出提醒）。

设计原则：只提醒、不拦截；内部出错 fail-open；零第三方依赖。
"""

import json
import os
import sys

BP_KW = ["商业计划书", "融资需求", "商业模式", "TAM"]


def main() -> int:
    if os.environ.get("LHG_BP_HOOKS_OFF") == "1":
        return 0
    try:
        raw = sys.stdin.read()
        payload = json.loads(raw) if raw.strip() else {}
    except Exception:
        return 0  # fail-open

    tool_input = payload.get("tool_input", {}) or {}
    file_path = tool_input.get("file_path", "") or ""
    content = tool_input.get("content", "") or ""
    if not file_path.lower().endswith(".md"):
        return 0
    if not any(k in content for k in BP_KW):
        return 0

    out = {
        "hookSpecificOutput": {
            "hookEventName": "PostToolUse",
            "additionalContext": (
                "刚写入的看起来像 BP 草稿。建议跑一遍投资人体检再往下走：\n"
                "python3 <插件目录>/scripts/audit/bp_audit.py --target %s --format text\n"
                "或 /lhg-bp:bp-audit（机器审计 + 投资人四问清单）。blocker不清零不许拿去见投资人。"
                % file_path
            ),
        }
    }
    sys.stdout.write(json.dumps(out, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
