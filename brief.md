# 赛道 AJ · OSC 开放超导挑战（FINAL-Bench / Hugging Face）

## 一句话

把「OSC 排行榜到底在排什么」做成可复现的结论，并交出一份能直接投递的 Discovery / Method 材料包。
作品暂名《十八级台阶》（Eighteen Steps）。

## 赛选（可核）

- 赛事：**Open Superconductor Challenge (OSC)**，主办 FINAL-Bench，托管在 Hugging Face。
- 数据与规则：`https://huggingface.co/datasets/FINAL-Bench/OSC-Superconductor`（本机直连 huggingface.co 不通，走 `hf-mirror.com` 取得同一 sha）。
- 资格：免费、任何人（含 AI agent）、个人可报；无国籍排除条款；非商业学术挑战。
- 截止：**2026-12-31 23:59 KST**（北京 12-31 22:59）。
- 交什么：轻赛道交 `submission.json`（material_id + 估算分数）；Gold/Method 另交可复现包（代码 + 冻结配置 + `run_*.sh` + SHA256 清单）。
- 去重：全库 1490 张单 + 实时检索 `超导 / Superconductor / FINAL-Bench / OSC` **0 命中**；v2 清单 G37 在列、无人开。

## 目标

1. 用公开数据把 **1,073 条已验证分数**逐条复算，证明排行榜是可完全预测的（可复现性审计）。
2. 量化排行榜实际在排什么：分数对「带填充 δ」与「N(E_F)」的依赖各自占多少；δ 的取值格点。
3. 用已发表的 4×4 ED 多尺寸表给出 A_d(δ) 的不确定带，测 **排名脆弱性**（top-K 在扰动下存活率）。
4. 建一个**只用 C2DB 描述符**的筛选器，预测 759 个尚未降维金属的 nef 与 δ，产出可提交的 Discovery 候选短名单（带预测区间）。
5. 产出：仓库（代码 + 数据快照 + 报告 + 站点 + verify）、可直接提交的 `submission.json`、给主办方的可复现包。

## 验收（能跑的命令）

- `verify.py` 全绿：数据哈希、1,073 条分数复算、δ 格点断言、排名脆弱性数字、筛选器交叉验证、报告/站点数字与 JSON 一致。
- 本机与全新 clone 均 `EXIT=0`。
- 线上页面可访问，数字与仓库一致。

## 不做什么

- 不改动、不覆盖任何他人提交；不向 HF 写入（无凭据，且本机不通 huggingface.co）。
- 不声称发现超导体；结论只到「筛选指标」与「排行榜性质」。
- 不代用户报名；提交动作留给用户。

## 停手线

遇到付费、需要实名/证件、需要向第三方平台写入凭据的环节，停手并记录，交回用户。
