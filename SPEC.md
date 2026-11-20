# SPEC — OSC《十八级台阶》闸 A

来源：挑战官方数据集 `FINAL-Bench/OSC-Superconductor`（revision `4585236f24ff…`，CC-BY-NC 4.0）。
本机直连 huggingface.co 不通，全部文件经 `hf-mirror.com` 取得，SHA256 见 `data/SHA256SUMS`。

## 一、官方规则（原文摘录）

| 条款 | 原文 | 出处 |
|---|---|---|
| 计分 | `Pairing Index = N(E_F) × A_d(δ_material) × 300` | README「Scoring: the OSC Pairing Index」 |
| 抗作弊 | 「A claimed value is recorded (as `claimed`) but never ranked as-is.」 | README「Why top scores cluster near the baseline」 |
| 可复现 | 「The solver's inputs and its A_d(δ) table are published, so every verified score is reproducible」 | README FAQ「How are winners verified?」 |
| 两条正路 | ① Discovery：提名 active set 之外的新材料；② Method：可复现、且与独立 ED 一致的方法 | README「the only two ways to exceed it」 |
| Method 判据 | 「Method standing is judged by reproducibility and agreement with the independent reference (exact diagonalization) — **not** by the raw size of a claimed A_d」 | README「How the Method rank is decided」 |
| 资格 | 「Who can join: anyone — researchers, students, and AI coding agents.」 | README TL;DR |
| 截止 | 「Season 1 closes 31 December 2026 (23:59 KST).」 | README FAQ |
| 费用 | free, open-science；非商业学术挑战 | README / PROVENANCE |

## 二、黄金路径（我按这条走）

1. 取三张表 + 两份公开 ED 校验表（`data/`，含哈希）。
2. 用 `scoring_meta.json` 的 A_d 表复算 1,073 条 `verified_score`，误差必须 < 1e-3。
3. 描述 A_d(δ) 的形状（平台/悬崖），并做方差分解（填充 vs N(E_F)）。
4. 用公开的 4×4 ED 做形状对比（Spearman），再做两种压力测试（形状替换、跨团簇散布扰动）。
5. 用组成近邻模型做 Discovery 可行性检验（留一法），给出诚实结论。
6. 若可行，产出可提交的 Method 包与 Discovery 提名；若不可行，如实记录。

## 三、验收标准（AC）

| 编号 | 断言 | 判据 |
|---|---|---|
| AC-01 | 数据快照可校验 | `data/SHA256SUMS` 全部匹配 |
| AC-02 | 分数完全可复算 | 1,073 条，`max abs diff ≤ 1e-3`，超差 0 条 |
| AC-03 | 夹零规则明确 | 85 条负 A_d 行记 0，且分数仍对上 |
| AC-04 | 填充格点 | 18 个 δ，Ne 全为偶数，2..36 |
| AC-05 | 平台/悬崖 | 平台 7 级、1.52 倍；悬崖 3.39 倍 |
| AC-06 | 方差分解 | A_d 57% / N(E_F) 25% / 协方差 18%，三者相加为 1 |
| AC-07 | 平台内排序 | Spearman(index, N(E_F)) = 0.968 ± 0.002 |
| AC-08 | 榜单事实 | top-1 = I2Mn2S 64.02；top-20 全在 δ ≤ 0.2778；19/20 的 N(E_F) 排名 ≤ 20 |
| AC-09 | ED 对比 | 5 个填充，Spearman = −0.60；n=0.5 公布值为节点而 ED 为正 |
| AC-10 | 压力测试 | 形状替换后 top-20 只剩 1 个；扰动下重合率 35–55%；单条存活 ≤ 2/3；第一名保住第一 < 1/3 |
| AC-11 | 筛选器诚实 | R² 0.08–0.16、MAE 0.42–0.48、δ 命中 15–20% |
| AC-12 | 产物齐备 | results.json、6 张图、report.html、site/index.html 存在且引用同一批数字 |
| AC-13 | 全新 clone 可跑 | 空目录 clone → `build.py` → `verify.py` 全绿 |

## 四、明确不做

- 不重跑主办方未公开的 6×6 求解器；不声称公布值有误。
- 不向 Hugging Face 写入（无凭据；本机不通 huggingface.co）。
- 不代用户报名或提交；提交动作与回执由用户完成。

## 五、停手线

需要付费、实名证件、或向第三方写入凭据时停手，记录并交回。
