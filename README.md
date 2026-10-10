<!-- About 简介（推送后填写到仓库 About 栏）：
商业计划书专家：信息输入→九章生成→投资人自检→10页路演版 ｜ 一键安装：/plugin marketplace add lhg-plugs/lhg-bp
-->
<!-- topics（推送后打）：claude-code, claude-plugin, agent-skills, business-plan, pitch, fundraising -->

# lhg-bp：商业计划书专家

> **一句话介绍**：给 AI 助手装上"融资组合拳"——项目信息输入→市场/产品/模式/财务九章生成→投资人视角自检→10 页路演版提炼，BP 一条龙。
>
> **一键安装**：在 Claude Code 里运行
> ```
> /plugin marketplace add lhg-plugs/lhg-bp
> /plugin install lhg-bp@lhg-plugs
> ```

## 它是什么

`lhg-bp` 是一个 Claude Code 插件（plugin 为主、skill 为辅）：

- **3 个命令**（小白入口）：`bp` 信息输入→九章生成→自检→路演版一条龙，`bp-pitch` 只提炼 10 页路演版，`bp-audit` 投资人视角体检
- **4 个平台中立 skill**（方法论，可移植到豆包/Workbuddy 等）：信息采集、九章结构、财务章节、投资人自检
- **3 个专家 agent**：BP 撰写专家、路演压缩专家、投资人评审
- **2 个硬门 hooks**：commit 前 BP 草稿审计拦截、写 BP 草稿提醒（均可一键豁免）
- **5 条确定性审计规则**：纯 Python、零第三方依赖，直接解析 Markdown 查章节完整性/数字一致性/空洞表述/财务勾稽/资金用途

差异化：**投资人视角贯穿始终**（每章回答投资人的一个疑问、四问自检清单）、
**数字纪律**（每个数字带来源+年份+口径，编造数据是红线）、**说人话的小白交互**（五问追问清单、信息卡）。

## 3 个命令用法

| 命令 | 作用 | 示例 |
|---|---|---|
| `/lhg-bp:bp` | 项目信息输入→九章 BP→投资人自检→10 页路演版，一条龙 | `/lhg-bp:bp "社区生鲜前置仓" --stage 天使` |
| `/lhg-bp:bp-pitch` | 把完整 BP 压缩成 10 页路演版 | `/lhg-bp:bp-pitch output/xxx-bp-20261011.md` |
| `/lhg-bp:bp-audit` | 投资人体检：5 条规则审计 + 四问自检清单 | `/lhg-bp:bp-audit output/xxx-bp-20261011.md` |

## 自查说明

自查 = 确定性脚本（机器）+ 投资人四问（人）：

1. 先跑 `scripts/audit/bp_audit.py --target <BP草稿.md>`，零成本；
2. 发现分两级：**blocker**（BP-SEC-001 必需章节缺失，必须补）、**warning**（市场规模数字矛盾/空洞表述/财务勾稽矛盾/缺资金用途，修或写豁免理由）；
3. 再按 `lhg-bp-review` 第 4 节过投资人四问：团队可信度/数据真实性/逻辑自洽/退出路径。

blocker 清零 + 四问有书面结论，才算"可发出"；为清零改脚本规则或阈值 → 作弊，不许。

## 目录结构

```
lhg-bp/
├── .claude-plugin/          # plugin.json（插件清单）+ marketplace.json（本仓即市场）
├── commands/                # 3 个命令：bp / bp-pitch / bp-audit
├── skills/                  # 4 个平台中立 skill（lhg-bp-input/structure/finance/review）
├── agents/                  # 3 个专家 agent（bp-drafter / pitch-slimmer / investor-reviewer）
├── hooks/                   # 2 个硬门（commit 前 BP 审计拦截 / 写 BP 草稿提醒）+ 豁免说明
├── scripts/audit/           # 5 条确定性审计规则（零第三方依赖，纯文本解析 Markdown）
├── fixtures/                # 冒烟测试用例（bad.md / good.md + make_fixtures.py 生成器）
├── smoke_test.py            # 一键冒烟测试
├── ATTRIBUTION.md            # 灵感来源与许可声明
└── LICENSE                  # MIT
```

## 什么时候用 / 什么时候不用（FAQ）

**什么时候用：**

- 你要融资，BP 还是空白 → 用 `/lhg-bp:bp`，一句话开始，信息卡填满后再写
- 你有一版 BP 草稿，心里没底 → `/lhg-bp:bp-audit` 先体检，5 条规则 10 秒出结果
- 完整 BP 有了，下周要路演 → `/lhg-bp:bp-pitch` 压缩成 10 页
- 你的 BP 总被投资人问住 → 按投资人四问清单提前自问

**什么时候不用：**

- 你要的是英文 BP / 面向美元基金的 deck → 本插件按中文融资语境调的，章节详略和话术不对味别硬套
- 你只想套个模板填空 → 本插件是"信息采集→写作→评审"的方法论，不是模板下载站
- 你的项目信息全是 [待补充] → 先回去找数据，信息太少写出的 BP 是空架子

**诚实声明：**

- 本插件的方法论为原创（2026-10-11 检索：组织内部百垂直调研 + 本地 skill 库均未找到商业计划书垂直 skill）。
- 插件不保证融资成功——它保证的是：结构完整、数字可追溯、逻辑自洽，不在低级问题上丢分。
- 财务预测数字是"假设的展开"不是"承诺"，见投资人时要能讲出每条假设的依据。

## lhg-plugs 插件矩阵

| 插件 | 一句话 | 安装 |
|---|---|---|
| [lhg-bp](https://github.com/lhg-plugs/lhg-bp) | 商业计划书专家：信息输入→九章生成→投资人自检→10页路演版 | `/plugin install lhg-bp@lhg-plugs` |
| *（后续插件在此追加，保持表格格式一致）* | | |

## 自检与反馈

本插件自带质检：每次使用后可跑 `python3 smoke_test.py` 一键验证（JSON 合法、skill/command/agent 完整性、5 条规则、fixtures 命中、hooks 行为）。

发现 bug 或有改进建议，以 `[QC] <一句话问题>` 为标题提交到 https://github.com/lhg-plugs/lhg-bp/issues，正文写清"复现步骤 → 实际表现 → 期望表现"。

## 出品：刘洪光

本插件由真人出镜 IP「刘洪光」（安徽合肥）出品，归属 [lhg-skills](https://github.com/lhg-skills)。

- GitHub 主页：https://github.com/lhg-skills —— 全部 skill 开源在此，欢迎 star
- 视频号：搜「刘洪光实名上网」
- 微信：lhgsmsw
