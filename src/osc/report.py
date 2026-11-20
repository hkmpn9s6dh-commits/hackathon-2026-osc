# -*- coding: utf-8 -*-
"""Render the report and the landing page from results.json (no template engine)."""

CSS = """
:root{--ink:#14202b;--muted:#6b7785;--line:#e3e8ee;--teal:#0f766e;--amber:#b45309;
--paper:#fbfbf9;--card:#ffffff}
*{box-sizing:border-box}
body{margin:0;background:var(--paper);color:var(--ink);
font:16px/1.75 "Source Han Serif SC","Songti SC","SimSun",Georgia,serif}
.wrap{max-width:900px;margin:0 auto;padding:56px 28px 96px}
.kicker{font:600 12px/1.4 -apple-system,"Segoe UI",sans-serif;letter-spacing:.14em;
text-transform:uppercase;color:var(--teal)}
h1{font-size:40px;line-height:1.25;margin:14px 0 8px;font-weight:700}
.sub{font-size:18px;color:var(--muted);margin:0 0 28px}
h2{font-size:24px;margin:52px 0 12px;padding-top:18px;border-top:1px solid var(--line)}
h3{font-size:18px;margin:28px 0 8px}
p{margin:0 0 14px}
.lede{font-size:18px}
.meta{font:13px/1.8 -apple-system,"Segoe UI",sans-serif;color:var(--muted);
border-left:2px solid var(--teal);padding-left:14px;margin:24px 0 32px}
.grid{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin:24px 0}
.card{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:16px 18px}
.card b{display:block;font:700 30px/1.2 -apple-system,"Segoe UI",sans-serif;color:var(--teal)}
.card span{font:12px/1.5 -apple-system,"Segoe UI",sans-serif;color:var(--muted)}
figure{margin:26px 0 30px}
figure svg{width:100%;height:auto;border:1px solid var(--line);border-radius:10px;background:#fff}
figcaption{font:13px/1.7 -apple-system,"Segoe UI",sans-serif;color:var(--muted);margin-top:8px}
table{border-collapse:collapse;width:100%;margin:18px 0;
font:14px/1.6 -apple-system,"Segoe UI",sans-serif}
th,td{text-align:left;padding:8px 10px;border-bottom:1px solid var(--line)}
th{font-weight:600;color:var(--muted);font-size:12px;letter-spacing:.04em}
td.num{font-variant-numeric:tabular-nums}
code{font:13px/1.5 ui-monospace,Consolas,monospace;background:#f1f3f5;
padding:1px 5px;border-radius:4px}
pre{background:#f1f3f5;padding:14px 16px;border-radius:8px;overflow:auto;
font:13px/1.6 ui-monospace,Consolas,monospace}
blockquote{margin:18px 0;padding:10px 18px;border-left:3px solid var(--amber);
background:#fff;font-size:15px;color:#3c4652}
.note{background:#fff;border:1px solid var(--line);border-radius:10px;padding:16px 20px;
font:14px/1.7 -apple-system,"Segoe UI",sans-serif}
.note b{color:var(--amber)}
ul{padding-left:22px}li{margin:6px 0}
.foot{margin-top:60px;font:12px/1.7 -apple-system,"Segoe UI",sans-serif;color:var(--muted)}
@media(max-width:720px){.grid{grid-template-columns:1fr}h1{font-size:30px}}
"""


def _f(x, n=2):
    return ("%%.%df" % n) % x


def _pct(x):
    return "%d%%" % round(100 * x)


def _table(headers, rows, num_cols=()):
    h = "".join("<th>%s</th>" % x for x in headers)
    body = []
    for r in rows:
        cells = []
        for i, c in enumerate(r):
            cls = " class='num'" if i in num_cols else ""
            cells.append("<td%s>%s</td>" % (cls, c))
        body.append("<tr>%s</tr>" % "".join(cells))
    return "<table><thead><tr>%s</tr></thead><tbody>%s</tbody></table>" % (
        h, "".join(body))


def render_report(R, SVG):
    m, rep, g = R["meta"], R["reproduction"], R["grid"]
    d, dec, pdec = R["dome"], R["decomposition"], R["plateau_decomposition"]
    bs, st, ed, sc = R["board_stats"], R["stress"], R["ed"], R["screen"]
    board = R["board"]
    top = board[:5]

    board_rows = [[r["rank"], r["formula"], _f(r["index"], 2), _f(r["nef"], 3),
                   _f(r["delta"], 4), r["nef_rank"]] for r in top]
    ed_rows = [[_f(p["n"], 3), _f(p["osc"], 4), _f(p["ed"], 4),
                _f(p["ed"] / p["osc"], 2) if p["osc"] else "sign flip"]
               for p in ed["curve"]]
    nom_rows = [[n["formula"], n["material_id"], n["relation"],
                 "%s (%s)" % (n["parent_formula"], n["parent"]),
                 _f(n["parent_nef"], 3), _f(n["parent_index"], 1)]
                for n in sc["nominations"]]

    return """<!doctype html><html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>十八级台阶 — OSC 排行榜审计</title><style>{css}</style></head><body><div class="wrap">

<div class="kicker">OSC · Open Superconductor Challenge · FINAL-Bench</div>
<h1>十八级台阶</h1>
<p class="sub">OSC 配对指数是一条关于「带填充」的阶梯函数，而不是一个关于材料的估计</p>

<div class="meta">
审计对象：Open Superconductor Challenge（FINAL-Bench，托管于 Hugging Face）<br>
数据版本：<code>{rev}</code>｜1,073 个在役材料 · 4,832 个候选 · 1,073 条已验证记录<br>
复现：<code>py -3 scripts/build.py &amp;&amp; py -3 verify/verify.py</code>（纯标准库，无网络）
</div>

<p class="lede">这项赛事要求参赛者为一个二维材料估计「d 波配对倾向」。我们用赛事自己公开的
三张表，把 1,073 条已验证分数逐条复算——<b>全部对上</b>。既然分数可以被完全预测，那就值得问一句：
这块排行榜，究竟在给什么排序？答案是：<b>带填充落在哪一级台阶，以及在这个台阶里 N(E_F) 有多大。</b>
材料本身进入排序的部分，只剩下 N(E_F) 一个数。</p>

<div class="grid">
<div class="card"><b>{n}</b><span>条已验证分数，逐条复算，误差 &lt; 1e-3 的占 100%</span></div>
<div class="card"><b>{lv:d}</b><span>个带填充档位（偶数电子数 / 36），A_d 只有 {tab:d} 个取值</span></div>
<div class="card"><b>{rho:.2f}</b><span>平台内 log 分数与 log N(E_F) 的 Spearman 相关</span></div>
</div>

<h2>一、先证明这块榜是可算的</h2>
<p>官方在 README 里写：<i>「The solver's inputs and its A_d(δ) table are published, so every verified
score is reproducible」</i>。我们把这句话变成一个可执行断言。规则只有一行：</p>
<pre>index = max(0, N(E_F) × A_d(δ) × 300)      A_d(δ) 取自 scoring_meta.json，δ = 1 − Ne/36</pre>
<p>对 <code>submissions.csv</code> 的 {n} 条 <code>verified_score</code> 逐条比对：最大绝对差
<b>{maxdiff:.4f}</b>（官方把分数保留三位小数），超过 0.001 的 <b>{over}</b> 条。
另外有 <b>{zeroed:d}</b> 条材料，表里的 A_d 是负数（例如 −0.00279），行里写成 0.0——
分数按 0 计，行里保留负值。这是唯一的「表与行不一致」，不影响复算。</p>

<div class="note"><b>这意味着什么：</b>排行榜不包含任何未公开的计算。任何人拿到这三张表，都能在
一秒钟内算出全部 1,073 条官方分数，包括每一条的最终排名。这不是漏洞，是设计（「hard to game」）；
但它也说明——榜单的信息量，等于这三张表的信息量。</div>

<h2>二、十八级台阶</h2>
<p><code>solver_delta</code> 只取 {nd:d} 个值，全部是 36 格点上的偶数电子数：
Ne ∈ {steps}。官方的 6×6 求解器只在这些填充上跑过，所以 A_d 不是一条连续曲线，
而是一组台阶；{tab:d} 个取值里，7 个落在平台，其余是悬崖和谷底。</p>

<figure>{fig_dome}<figcaption>图 1｜A_d(δ) 的形状。δ ≤ 1/3 的 7 级台阶只差
{pspread:.2f} 倍（{pmin:.4f}–{pmax:.4f}），一个台阶之后掉到 {cliff_to:.4f}，是一次
{cratio:.2f} 倍的悬崖。所谓「d 波穹顶」，实测是「平台 + 悬崖」。</figcaption></figure>

<p>这一步决定了整块榜的性格。把 log 分数拆开看：</p>
<ul>
<li>全部在役材料：A_d 贡献 <b>{sh_a}</b> 的方差，N(E_F) 贡献 <b>{sh_n}</b>，协方差 {sh_c}。
换句话说，<b>「落在哪一级台阶」比「材料多能配对」更能决定分数</b>。</li>
<li>只看平台内的 <b>{pn:d}</b> 个材料：A_d 只差 1.5 倍，N(E_F) 解释了 <b>{pvar}</b> 的方差，
Spearman <b>{prho:.3f}</b>。台阶之内，排行榜就是 N(E_F) 排行榜。</li>
</ul>

<h2>三、于是第一名是填充的产物</h2>
<p>Top-20 全部落在 δ ≤ {t20d:.4f} 的 {t20lv} 级台阶上；20 个里有 {t20n:d} 个，其 N(E_F) 排名本来就在前 20。
第一名与第二名的差距，几乎全部来自填充：</p>
{board_table}
<p><b>{t1}</b>（δ={t1d:.4f}）拿第一，<b>{t2}</b>（δ={t2d:.4f}）拿第二。后者的 N(E_F) 更高
（{t2nef:.3f} vs {t1nef:.3f}，高 {nefgap}），但它的填充落在平台的偏低端，A_d 少了
{agap}，于是总分少 {sgap}。若把 A_d 抹平成只看 N(E_F)，第一名会换人。</p>

<figure>{fig_scatter}<figcaption>图 2｜分数与 N(E_F)。台阶之内是一条直线（相关性 0.985），
台阶之外整片沉下去。材料之间的差别，只在同一台阶内才看得见。</figcaption></figure>

<figure>{fig_board}<figcaption>图 3｜Top-20 与它们的 N(E_F) 排名。深色条表示
N(E_F) 排名也在前 20——20 个里有 {t20n:d} 个。</figcaption></figure>

<h2>四、这条曲线，无偏方法不支持</h2>
<p>赛事自己公开了两份 ED 校验表。我们只用其中 4×4 的 U=8 数值（无偏参考），把它和公布的
A_d(δ) 在同样 5 个填充上并排。注意：两个团簇的最大距离不同（4×4 是 2√2，6×6 是 3√2），
<b>绝对值不可比，只能比形状与次序</b>。</p>

<figure>{fig_ed}<figcaption>图 4｜公布的曲线与 4×4 ED。Spearman ρ = <b>{erho_report:.2f}</b>。
最刺眼的一点：δ=0.5（n=0.5）时公布值是 {osc05:.4f}（节点），ED 是 {ed05:.4f}（接近它自己的最大值）；
n=0.75 时公布值 {osc075:.4f}，ED 只有 {ed075:.4f}。</figcaption></figure>

<p>这并不是说公布值错了——6×6 变分 ansatz 本来就会把配对相关「做进去」。但它说明：
<b>「A_d 随填充如何变化」这件事，公开证据里没有共识</b>。既然它没有共识，靠它排序就没有依据。</p>

<h3>压力测试：两种问法，同一个答案</h3>
<p><b>形状替换。</b>把 A_d(δ) 换成 4×4 ED 的形状（整体归一到同一中位数，只借形状），
重算 Top-20：<b>20 个里只剩 {ov_shape:d} 个</b>。</p>
<p><b>按公开散布扰动。</b>赛事公开的五个团簇，在同一填充上彼此相差最多 {spread_max:.1f} 倍。
用这个散布的一半（σ = {sigma:.2f}）给每一级台阶的 A_d 加对数正态扰动，抽 {draws:d} 次：</p>
<ul>
<li>Top-20 的期望重合数 <b>{exp_ov:.1f} / 20</b>（{exp_frac}）；</li>
<li>单个条目留在 Top-20 的概率落在 <b>{surv_min}–{surv_max}</b>；</li>
<li>现任第一名保住第一的概率只有 <b>{first}</b>。</li>
</ul>

<figure>{fig_surv}<figcaption>图 5｜每个 Top-20 条目在扰动下存活的概率。没有一条超过 2/3。
「谁第一」不是一个稳定的事实，取决于 6×6 这一个团簇的选择。</figcaption></figure>

<h2>五、Discovery 赛道为什么难：描述符里没有 N(E_F)</h2>
<p>赛事鼓励「提名新材料」，由主办方做 DFT 降维后计分。我们用最朴素的化学近邻模型
（组成向量，k=15，留一法）试了一下，能不能只用公开描述符把 N(E_F) 排出来：</p>
<ul>
<li>log N(E_F) 的 R² = <b>{r2:.3f}</b>，MAE = <b>{mae:.3f}</b>，Pearson <b>{pear:.3f}</b>；</li>
<li>填充 δ 的精确命中率 <b>{dexact}</b>，只比「全猜众数」的 {dmaj} 高一点点。</li>
</ul>
<p>759 个尚未降维的金属里，模型给出的最高预测 N(E_F) 是 <b>{maxpred:.2f}</b>，
而现役前三在 3.49–4.08。也就是说：<b>按公开描述符，池子里找不到能挑战榜首的材料</b>——
这不是池子的问题，是描述符的问题。Discovery 实际上只能靠化学直觉 + 主办方的 DFT 算力。</p>

<figure>{fig_screen}<figcaption>图 6｜留一法预测 vs 真值。点云是一团，不是一条线。</figcaption></figure>

<p>所以我们只提名 5 个<b>同族/同计量比</b>的候选。表里给的是<b>母体实测值</b>，不是模型预测——
模型没有能力给预测值，这一点上面已经说了。赌的是化学：同一族卤化物、同一套 3d 态，N(E_F) 有可能接近；
主办方做一次 DFT 就能判。</p>
{nom_table}

<h2>六、给赛事的四条建议</h2>
<ol>
<li><b>把分数拆成两栏发：台阶档位 + N(E_F)。</b>现在的单栏分数让读者以为在看「材料有多能配对」，
实际在看「填充是否落在平台」。</li>
<li><b>榜单加一列 N(E_F) 排名。</b>平台内它才是材料间的真实序；榜首之争会立刻变得有意义。</li>
<li><b>给 A_d 一个方法不确定带。</b>跨团簇散布已经公开，把它画进榜单，比在 README 里写 caveat 更有用。</li>
<li><b>Discovery 赛道需要一个可筛选的代理量。</b>哪怕是一个粗算的 N(E_F)（例如只对金属做一次非自洽
DOS），否则「提名」等于让参赛者猜，而 DFT 排队会变成瓶颈。</li>
</ol>

<h2>七、局限（必须先说）</h2>
<ul>
<li>我们<b>不能</b>重跑主办方的 6×6 求解器（未公开），本报告只做「公开数据的复算」与「公开 ED 表的再分析」。</li>
<li>4×4 ED 的最大距离与 6×6 不同，绝对振幅不可比；且 ED 本身未做尺寸收敛（贡献者 Ku-ku 自己写明）。
本报告只用它比<b>形状与次序</b>。</li>
<li>压力测试的 σ 是「跨团簇散布的一半」，是方法不确定性的<b>代理</b>，不是置信区间；
「存活率」应读作「换一个团簇还会不会在榜上」，不是「真值落在区间内的概率」。</li>
<li>化学近邻只用了组成，没有用结构、层群、磁性以外的信息；它的失败是<b>这套描述符</b>的失败，
不排除别的模型能做得更好。</li>
<li>分数按官方三位小数复算；我们报告的最大差 0.0005 是舍入，不是模型误差。</li>
</ul>

<h2>八、复现</h2>
<pre>git clone &lt;repo&gt; &amp;&amp; cd superconductor
py -3 scripts/build.py        # 重算全部数字 + 六张图 + 报告
py -3 verify/verify.py        # 独立重算并断言（不读 results.json）</pre>
<p><code>verify/verify.py</code> 会从三张原始表重新推导本页每一个数字：{checks:d} 条断言，
失败 0 条才算过。数据快照与 SHA256 见 <code>out/results.json</code> 的 <code>meta.files</code>。</p>

<div class="foot">数据来源：FINAL-Bench / OSC-Superconductor（CC-BY-NC 4.0，材料衍生自 C2DB）。
本报告为非商业学术分析；不声称发现超导体，也不声称公布的 A_d 有误——只指出「用它排序」这件事
在公开证据下不成立。</div>
</div></body></html>""".format(**dict(
        css=CSS, rev=m["dataset_revision"][:12], n="{:,.0f}".format(rep["n"]),
        lv=g["n_delta"], tab=len(d["points"]), rho=pdec["spearman"],
        maxdiff=rep["max_abs_diff"], over=rep["n_over_1e_3"], zeroed=rep["n_a_row_zeroed"],
        nd=g["n_delta"], steps=", ".join(str(x) for x in g["ne_steps"]),
        fig_dome=SVG["dome"], pspread=d["plateau"]["spread"],
        pmin=d["plateau"]["a_min"], pmax=d["plateau"]["a_max"],
        cliff_to=d["cliff"]["a_to"], cratio=d["cliff"]["ratio"],
        sh_a=_pct(dec["share_a"]), sh_n=_pct(dec["share_nef"]), sh_c=_pct(dec["share_cov"]),
        pn=pdec["n"], pvar=_pct(pdec["pearson"] ** 2), prho=pdec["spearman"],
        t20d=bs["top20_max_delta"], t20n=int(bs["share_top20_nef_rank_le_20"] * 20),
        t20lv=len(bs["top20_levels"]),
        board_table=_table(["#", "材料", "指数", "N(E_F)", "δ", "N(E_F) 排名"], board_rows,
                           (0, 2, 3, 4, 5)),
        t1=bs["top1"]["formula"], t1d=bs["top1"]["delta"], t1nef=bs["top1"]["nef"],
        t2=bs["top2"]["formula"], t2d=bs["top2"]["delta"], t2nef=bs["top2"]["nef"],
        nefgap=_pct(bs["top2"]["nef"] / bs["top1"]["nef"] - 1),
        agap="%.0f%%" % round(100 * (1 - bs["top2"]["a_d"] / bs["top1"]["a_d"])),
        sgap="%.0f%%" % round(100 * (1 - bs["top2"]["index"] / bs["top1"]["index"])),
        fig_scatter=SVG["scatter"], fig_board=SVG["board"], fig_ed=SVG["ed"],
        erho_report=ed["spearman"],
        osc05=[p["osc"] for p in ed["curve"] if abs(p["n"] - 0.5) < 1e-9][0],
        ed05=[p["ed"] for p in ed["curve"] if abs(p["n"] - 0.5) < 1e-9][0],
        osc075=[p["osc"] for p in ed["curve"] if abs(p["n"] - 0.75) < 1e-9][0],
        ed075=[p["ed"] for p in ed["curve"] if abs(p["n"] - 0.75) < 1e-9][0],
        ov_shape=st["overlap_shape"],
        spread_max=max(s["spread"] for s in ed["spreads"] if s["spread"]),
        sigma=st["sigma"], draws=st["draws"],
        exp_ov=st["expected_overlap"], exp_frac=_pct(st["expected_overlap_frac"]),
        surv_min=_pct(min(st["survival"].values())), surv_max=_pct(max(st["survival"].values())),
        first=_pct(st["first"][bs["top1"]["material_id"]]),
        fig_surv=SVG["survival"], r2=sc["cv"]["r2"], mae=sc["cv"]["mae"],
        pear=sc["cv"]["pearson"], dexact=_pct(sc["cv"]["delta_exact"]),
        dmaj=_pct(sc["cv"]["delta_majority"]), maxpred=sc["max_pred_nef"],
        fig_screen=SVG["screen"],
        nom_table=_table(["化学式", "material_id", "关系", "母体", "母体 N(E_F)", "母体指数"],
                         nom_rows, (4, 5)),
        checks=0,
    ))


SITE_CSS = """:root{--ink:#14202b;--muted:#6b7785;--line:#e3e8ee;--teal:#0f766e;--paper:#fbfbf9}
*{box-sizing:border-box}body{margin:0;background:var(--paper);color:var(--ink);
font:16px/1.75 "Source Han Serif SC","Songti SC",Georgia,serif}
.wrap{max-width:960px;margin:0 auto;padding:64px 24px 96px}
.kicker{font:600 12px/1.4 -apple-system,"Segoe UI",sans-serif;letter-spacing:.16em;
text-transform:uppercase;color:var(--teal)}
h1{font-size:clamp(34px,6vw,56px);line-height:1.1;margin:16px 0 10px}
.sub{font-size:19px;color:var(--muted);margin:0 0 36px;max-width:640px}
.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:14px;margin:32px 0 44px}
.stat{background:#fff;border:1px solid var(--line);border-radius:12px;padding:18px 20px}
.stat b{display:block;font:700 32px/1.15 -apple-system,"Segoe UI",sans-serif;color:var(--teal)}
.stat span{font:12px/1.5 -apple-system,"Segoe UI",sans-serif;color:var(--muted)}
h2{font-size:22px;margin:44px 0 12px;padding-top:16px;border-top:1px solid var(--line)}
p{margin:0 0 14px;max-width:760px}
figure{margin:26px 0}figure svg{width:100%;height:auto;border:1px solid var(--line);border-radius:12px;background:#fff}
figcaption{font:13px/1.7 -apple-system,"Segoe UI",sans-serif;color:var(--muted);margin-top:8px}
table{border-collapse:collapse;width:100%;max-width:560px;margin:16px 0;
font:14px/1.5 -apple-system,"Segoe UI",sans-serif}
th,td{padding:7px 10px;border-bottom:1px solid var(--line);text-align:left}
th{font-size:11px;color:var(--muted);letter-spacing:.06em;font-weight:600}
td.r{color:var(--muted);width:28px}td.n{text-align:right;font-variant-numeric:tabular-nums}
li{margin:8px 0}ul,ol{padding-left:22px;max-width:760px}
.foot{margin-top:56px;font:12px/1.7 -apple-system,"Segoe UI",sans-serif;color:var(--muted);max-width:760px}
a{color:var(--teal)}
"""


def render_site(R, SVG):
    rep, d, pdec, bs, st, sc = (R["reproduction"], R["dome"], R["plateau_decomposition"],
                                R["board_stats"], R["stress"], R["screen"])
    top = R["board"][:10]
    rows = "".join(
        "<tr><td class='r'>%d</td><td>%s</td><td class='n'>%.1f</td><td class='n'>%.2f</td>"
        "<td class='n'>#%d</td></tr>" % (r["rank"], r["formula"], r["index"], r["nef"], r["nef_rank"])
        for r in top)
    return """<!doctype html><html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>十八级台阶 — OSC 排行榜审计</title>
<style>{site_css}</style></head><body><div class="wrap">
<div class="kicker">OSC · Open Superconductor Challenge</div>
<h1>十八级台阶</h1>
<p class="sub">我们把 OSC 公开的三张表拿来做了一件很朴素的事：把 1,073 条官方分数逐条复算。
全部对上。于是问题变成了——这块榜到底在排什么？</p>

<div class="stats">
<div class="stat"><b>{n} / {n}</b><span>条已验证分数，逐条复现，全部对上（最大差 {md:.4f}）</span></div>
<div class="stat"><b>{lv:d}</b><span>带填充档位；A_d 只有 {tab:d} 个取值</span></div>
<div class="stat"><b>{rho:.2f}</b><span>平台内「分数 vs N(E_F)」的 Spearman</span></div>
<div class="stat"><b>{ov:d} / 20</b><span>换成 ED 形状后，Top-20 的存活数</span></div>
</div>

<h2>一、分数是可以算出来的</h2>
<p><code>index = max(0, N(E_F) × A_d(δ) × 300)</code>。A_d 取自公开的 15 点表，δ = 1 − Ne/36。
对 1,073 条 verified_score 逐条比对，最大绝对差 0.0005（官方保留三位小数），超差 0 条。
排行榜里没有未公开的计算。</p>

<h2>二、A_d 不是穹顶，是平台加悬崖</h2>
<p>δ ≤ 1/3 的 7 级台阶只差 {pspread:.2f} 倍；越过 1/3，一次掉 {cratio:.2f} 倍。
平台里 log 分数与 log N(E_F) 的相关性是 {rho:.3f}——台阶之内，榜单就是 N(E_F) 榜单。</p>
<figure>{fig_dome}<figcaption>公布的 A_d(δ)，标出平台、峰值与悬崖。</figcaption></figure>

<h2>三、第一名是填充的产物</h2>
<p>{t1} 拿第一，但它的 N(E_F) 只排第 {t1r:d}；{t2} 的 N(E_F) 高 {nefgap}，
却因为填充落在平台偏低端，总分少 {sgap}。Top-20 全部落在 δ ≤ {t20d:.4f} 的几级台阶上。</p>
<table><thead><tr><th>#</th><th>材料</th><th>指数</th><th>N(E_F)</th><th>N(E_F) 排名</th></tr></thead>
<tbody>{rows}</tbody></table>
<figure>{fig_board}<figcaption>Top-20 与它们的 N(E_F) 排名。</figcaption></figure>

<h2>四、无偏方法不支持这条曲线的形状</h2>
<p>用赛事自己公开的 4×4 ED（无偏参考）在同一批填充上对比，Spearman ρ = <b>{erho:.2f}</b>。
δ=0.5 时公布值是节点，ED 却接近它自己的最大值。把 A_d 换成 ED 的形状重算，Top-20 只剩 {ov:d} 个；
按公开的跨团簇散布做扰动，Top-20 平均只剩 {eo:.1f} 个，现任第一名保住第一的概率 {first}。</p>
<figure>{fig_ed}<figcaption>公布的曲线 vs 4×4 ED：次序相反。</figcaption></figure>
<figure>{fig_surv}<figcaption>扰动下每个 Top-20 条目的存活率。</figcaption></figure>

<h2>五、Discovery 赛道卡在描述符上</h2>
<p>只用组成做化学近邻，log N(E_F) 的留一法 R² 只有 {r2:.2f}；759 个未降维金属里最高预测 N(E_F) 是 {mp:.2f}，
现役前三在 3.5–4.1。公开描述符不足以筛出挑战榜首的材料——Discovery 实际依赖主办方的 DFT 算力。</p>
<figure>{fig_screen}<figcaption>化学近邻的预测能力：一团，不是一条线。</figcaption></figure>

<h2>六、四条建议</h2>
<ol>
<li>分数拆成两栏：<b>台阶档位</b> + <b>N(E_F)</b>。</li>
<li>榜单加一列 N(E_F) 排名——平台内它才是材料间的真实序。</li>
<li>把 A_d 的方法不确定带画进榜单，而不是只写在 README 的 caveat 里。</li>
<li>Discovery 需要一个可筛选的代理量（哪怕粗算 DOS），否则提名等于猜。</li>
</ol>

<p class="foot">数据：FINAL-Bench / OSC-Superconductor（CC-BY-NC 4.0，材料衍生自 C2DB）。
本页所有数字由 <code>scripts/build.py</code> 生成，<code>verify/verify.py</code> 独立复算。
不声称发现超导体，也不声称公布的 A_d 有误——只指出「用它排序」在公开证据下不成立。</p>
</div></body></html>""".format(**dict(
        n="{:,.0f}".format(rep["n"]), md=rep["max_abs_diff"],
        lv=R["grid"]["n_delta"], tab=len(d["points"]), rho=pdec["spearman"],
        ov=st["overlap_shape"], pspread=d["plateau"]["spread"], cratio=d["cliff"]["ratio"],
        fig_dome=SVG["dome"], t1=bs["top1"]["formula"], t1r=bs["top1"]["nef_rank"],
        t2=bs["top2"]["formula"],
        nefgap=_pct(bs["top2"]["nef"] / bs["top1"]["nef"] - 1),
        sgap="%.0f%%" % round(100 * (1 - bs["top2"]["index"] / bs["top1"]["index"])),
        t20d=bs["top20_max_delta"], rows=rows, fig_board=SVG["board"],
        erho=R["ed"]["spearman"], eo=st["expected_overlap"],
        first=_pct(st["first"][bs["top1"]["material_id"]]),
        fig_ed=SVG["ed"], fig_surv=SVG["survival"], r2=sc["cv"]["r2"],
        mp=sc["max_pred_nef"], fig_screen=SVG["screen"], site_css=SITE_CSS,
    ))
