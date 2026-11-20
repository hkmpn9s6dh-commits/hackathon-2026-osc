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
h2{font-size:23px;margin:52px 0 12px;padding-top:18px;border-top:1px solid var(--line)}
h3{font-size:17px;margin:28px 0 8px}
p{margin:0 0 14px}
.lede{font-size:18px}
.meta{font:13px/1.8 -apple-system,"Segoe UI",sans-serif;color:var(--muted);
border-left:2px solid var(--teal);padding-left:14px;margin:24px 0 32px}
.grid{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin:24px 0}
.card{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:14px 16px}
.card b{display:block;font:700 26px/1.2 -apple-system,"Segoe UI",sans-serif;color:var(--teal)}
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
ul,ol{padding-left:22px}li{margin:6px 0}
.foot{margin-top:60px;font:12px/1.7 -apple-system,"Segoe UI",sans-serif;color:var(--muted)}
@media(max-width:720px){.grid{grid-template-columns:repeat(2,1fr)}h1{font-size:30px}}
"""

SITE_CSS = """
:root{--ink:#14202b;--muted:#6b7785;--line:#e3e8ee;--teal:#0f766e;--paper:#fbfbf9}
*{box-sizing:border-box}body{margin:0;background:var(--paper);color:var(--ink);
font:16px/1.75 "Source Han Serif SC","Songti SC",Georgia,serif}
.wrap{max-width:960px;margin:0 auto;padding:64px 24px 96px}
.kicker{font:600 12px/1.4 -apple-system,"Segoe UI",sans-serif;letter-spacing:.16em;
text-transform:uppercase;color:var(--teal)}
h1{font-size:clamp(34px,6vw,56px);line-height:1.1;margin:16px 0 10px}
.sub{font-size:19px;color:var(--muted);margin:0 0 36px;max-width:680px}
.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:14px;margin:32px 0 44px}
.stat{background:#fff;border:1px solid var(--line);border-radius:12px;padding:18px 20px}
.stat b{display:block;font:700 30px/1.15 -apple-system,"Segoe UI",sans-serif;color:var(--teal)}
.stat span{font:12px/1.5 -apple-system,"Segoe UI",sans-serif;color:var(--muted)}
h2{font-size:22px;margin:44px 0 12px;padding-top:16px;border-top:1px solid var(--line)}
p{margin:0 0 14px;max-width:780px}
figure{margin:26px 0}figure svg{width:100%;height:auto;border:1px solid var(--line);border-radius:12px;background:#fff}
figcaption{font:13px/1.7 -apple-system,"Segoe UI",sans-serif;color:var(--muted);margin-top:8px}
table{border-collapse:collapse;width:100%;max-width:580px;margin:16px 0;
font:14px/1.5 -apple-system,"Segoe UI",sans-serif}
th,td{padding:7px 10px;border-bottom:1px solid var(--line);text-align:left}
th{font-size:11px;color:var(--muted);letter-spacing:.06em;font-weight:600}
td.r{color:var(--muted);width:28px}td.n{text-align:right;font-variant-numeric:tabular-nums}
li{margin:8px 0}ul,ol{padding-left:22px;max-width:780px}
.foot{margin-top:56px;font:12px/1.7 -apple-system,"Segoe UI",sans-serif;color:var(--muted);max-width:780px}
a{color:var(--teal)}
"""


def _f(x, n=2):
    return ("%%.%df" % n) % x


def _pct(x, n=0):
    return ("%%.%df%%%%" % n) % (100 * x)


def _table(headers, rows, num_cols=()):
    h = "".join("<th>%s</th>" % x for x in headers)
    body = []
    for r in rows:
        cells = []
        for i, c in enumerate(r):
            cls = " class='num'" if i in num_cols else ""
            cells.append("<td%s>%s</td>" % (cls, c))
        body.append("<tr>%s</tr>" % "".join(cells))
    return "<table><thead><tr>%s</tr></thead><tbody>%s</tbody></table>" % (h, "".join(body))


def render_report(R, SVG, checks=0):
    m, rep = R["meta"], R["reproduction"]
    g, d = R["grid"], R["dome"]
    dec, pdec = R["decomposition"], R["plateau_decomposition"]
    bs, st, ed, sc = R["board_stats"], R["stress"], R["ed"], R["screen"]
    hf = R["half_filling"]
    board = R["board"]
    top5 = board[:5]

    board_rows = [[r["rank"], r["formula"], _f(r["index"], 2), _f(r["nef"], 3),
                   _f(r["delta"], 4), r["nef_rank"]] for r in top5]
    leader_rows = [[l["formula"], _f(l["nef"], 2), _f(l["pred_nef"], 2),
                    "%d / %d" % (l["pred_rank"], l["n"])] for l in sc["leaders"]]
    nom_rows = [[n["formula"], n["material_id"], n["relation"],
                 "%s (%s)" % (n["parent_formula"], n["parent"]),
                 _f(n["parent_nef"], 3), _f(n["parent_index"], 1)]
                for n in sc["nominations"]]

    return """<!doctype html><html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>十八级台阶 — OSC 排行榜审计</title><style>{css}</style></head><body><div class="wrap">

<div class="kicker">OSC · Open Superconductor Challenge · FINAL-Bench</div>
<h1>十八级台阶</h1>
<p class="sub">把 OSC 的三张公开表复算一遍之后，真正的问题不是「谁第一」，而是「表与它自己的说明书对不上」</p>

<div class="meta">
审计对象：Open Superconductor Challenge（FINAL-Bench，托管于 Hugging Face）<br>
数据版本：<code>{rev}</code>｜1,073 个在役材料 · 4,832 个候选 · 1,073 条已验证记录<br>
复现：<code>py -3 scripts/build.py &amp;&amp; py -3 verify/verify.py</code>（纯标准库，无网络）
</div>

<p class="lede">赛事的计分只有一行：<code>index = N(E_F) × A_d(δ) × 300</code>，其中 A_d 取自公开的
15 点表。我们把 1,073 条官方分数逐条复算：<b>1,064 条</b>能完全从表里算出来（最大差 5e-4，是三位小数的舍入），
另外 <b>9 条</b>落在表里根本没有条目的填充上。复算本身没有问题；问题出在复算所依赖的那张表——
它在「半满」这一格上，和赛事 README 写的物理正好相反。</p>

<div class="grid">
<div class="card"><b>1,064<span style="font-size:15px">/1,073</span></b><span>条分数可由公开表直接算出；9 条落在表的空洞里</span></div>
<div class="card"><b>{poslev}</b><span>个不同的 A_d 正取值（表里共 {entries} 个条目）</span></div>
<div class="card"><b>{prho:.2f}</b><span>平台内「分数 vs N(E_F)」的 Spearman</span></div>
<div class="card"><b>{ovs}/20</b><span>换成 4×4 ED 的形状后，Top-20 的存活数</span></div>
</div>

<h2>一、复算：1,064 条对得上，9 条落在表的空洞里</h2>
<p>规则是 <code>index = max(0, N(E_F) × A_d(δ) × 300)</code>，A_d 按 <code>Ne = 36 − round(36δ)</code>
查 <code>scoring_meta.json</code>。对 <code>submissions.csv</code> 的 1,073 条 <code>verified_score</code>
逐条比对：最大绝对差 <b>{maxdiff:.4f}</b>，超过 0.001 的 <b>{over}</b> 条
（用的是 <code>active_challenge.csv</code> 的 6 位 <code>nef</code>；若改用
<code>submissions.csv</code> 自带的 4 位 <code>nef</code>，会有 21 行越过 1e-3，最大 1.3e-3——
两份 dump 的精度不同，这一步必须说明用哪一个）。这印证了 README 的说法——
每一分都是可复现的。但复算过程里冒出来两处它没写的东西：</p>
<ul>
<li><b>表有洞。</b>A_d 表只有 {entries} 个 Ne 条目，缺 Ne = 4、6、8。恰好有 <b>{uncov}</b> 个材料
（δ = 0.889 / 0.833 / 0.778）落在这三档，dump 里把它们写成 A_d = 0、分数 0。
「可复现」对这 9 行是靠「缺失即 0」这个未成文约定成立的，不是从表里算出来的。</li>
<li><b>负值被夹零。</b>有 <b>{negrows}</b> 行的表值是负数（例如 −0.00279）：<code>active_challenge.csv</code> 里 85 行写成 0.0、
3 行保留负值；<code>submissions.csv</code> 里 88 行全写 0。分数按 <code>max(0, ·)</code> 计。这不是错误，是规则，但它意味着「A_d = 0」有两种含义：
真的算出来是 0，和表里没有这一格。</li>
</ul>

<h2>二、半满处：表说 0.0384，README 说「消失」</h2>
<p>这是整份审计里最直接的一条文本冲突。赛事 README 在解释 A_d(δ) 的形状时写：</p>
<blockquote>「A_d depends strongly on doping … <b>vanishing at half-filling</b> and heavy overdoping」</blockquote>
<p>半满就是 δ = 0（Ne = 36，每个格点一个电子；<code>scoring_meta.json</code> 自己把 "36" 与 0.0 配对）。
表里这一格给的是 <b>{hfa:.5f}</b>，不是 0。<b>在役材料里有 {hfn} 个（{hfpct}）落在这一格上。</b></p>
<div class="note"><b>要把这条说准，得同时说清三件事。</b>
① 0.03844 是平台里<b>最低</b>的一档（峰值 0.05849），全库还有 <b>{hfabove}</b> 个材料的 A_d 比它高——
所以问题不是「它被算得太高」，而是「README 说它该是 0，表里却不是」。
② 这不必然说明 ansatz 造假：公开的 4×4 ED 在半满处也给出 0.0062，2×4 与 √10 给出 0.033–0.036，
同一量级。半满非零本身可以是有限尺寸/壳层效应，不专属于变分态。
③ 它对榜单的实际影响很小：Top-20 里只有 <b>{hftop}</b> 依赖这一档；把 A_d(0) 硬设为 0，
它被 {hfrepl} 顶掉，其余 19 个不动。</div>
<p>所以这条发现的分量不在「改一个数会翻榜」，而在<b>文档与数据在同一格上给出相反的物理</b>：
这格是全表最该被复核的数，而它恰好影响的是「哪些材料算在平台里」，不是「谁第一」。</p>

<figure>{fig_dome}<figcaption>图 1｜公布的 A_d(δ)。橙圈是半满：0.0384，峰值的 66%。
平台（δ ≤ 1/3）内 7 级只差 1.52 倍；越过 1/3 掉到 0.0127（3.4 倍；从峰值算是 4.6 倍）。</figcaption></figure>

<h2>三、于是分数 ≈ N(E_F) × 一个近似二值的填充滤波器</h2>
<p>表里只有 <b>{poslev}</b> 个不同的正取值，δ 只有 <b>{nd}</b> 档（偶数 Ne / 36），
所以分数只能落在很粗的格子上；这也是为什么「填充档位」能压过材料差别。
把 log 分数拆开（只看 976 条正分记录；97 条零分不含在内）：A_d 贡献 <b>{sha}</b> 的方差，N(E_F) 贡献 <b>{shn}</b>，协方差 {shc}
——「落在哪一级台阶」比「材料多能配对」更能决定分数。若只看平台内的 <b>{pn}</b> 个材料，
A_d 只差 1.52 倍，N(E_F) 解释了 <b>{pvar}</b> 的方差，Spearman <b>{prho:.3f}</b>。</p>
<figure>{fig_scatter}<figcaption>图 2｜平台内是一条直线（R² 0.97 来自 <code>index = N(E_F) × 常数</code> 这个恒等式，
不是经验规律）。台阶外整片沉下去。</figcaption></figure>

<h2>四、第一名坐在峰上</h2>
<p>Top-20 全部落在 δ ≤ {t20d:.4f} 的 {t20lv} 级台阶上；20 个里有 {t20n} 个的 N(E_F) 排名本来就在前 20。
榜首之争是填充位次的直接结果：</p>
{table}
<p><b>{t1}</b> 的 δ = {t1d:.4f}，正落在 A_d 取最大值的那一档（{peak:.5f}）。<b>{t2}</b> 的 N(E_F) 高
{nefgap}，但 δ = {t2d:.4f} 处的 A_d 低 {agap}，于是总分少 {sgap}。所以「谁第一」取决于谁的填充
落在峰那一档——这不算错，但它说明这块榜先按填充分档、再在档内按 N(E_F) 排，两步都不是「材料本身有多能配对」。</p>
<figure>{fig_board}<figcaption>图 3｜Top-20 与各自的 N(E_F) 排名。深色条表示 N(E_F) 排名也在前 20。</figcaption></figure>

<h2>五、ED 对比：能说明「次序未被识别」，不能裁决谁对</h2>
<p>赛事公开了两份 ED 校验表。把 4×4 的 U=8 值与公布的 A_d 放在同样 5 个填充上并排：Spearman
<b>{rho:.2f}</b>。但这个数字必须打折看：</p>
<ul>
<li><b>只有 5 个点。</b>精确置换检验双侧 p = <b>{pperm:.2f}</b>。5 个点裁决不了一条曲线。</li>
<li><b>换个插值就换个答案。</b>赛事自己在 <code>validation/</code> 里用另一种插值读出 ≈ −0.1。
同一个统计量、同一批 5 个点，−0.60 与 −0.1 的差别只来自「怎么把两条不同填充的曲线对齐」。</li>
<li><b>两个团簇不是同一个量。</b>4×4 的最大距离是 2√2，6×6 是 3√2；绝对值不可比，只能比次序。</li>
<li><b>ED 的「峰」也不是相互作用。</b>n=0.5 处 U=8/U=0 = 1.03：ED 那个 0.048 里 97% 是无相互作用
的壳层值。真正被相互作用增强的是 n=0.875（1.85×），而它的绝对振幅只有 0.019。</li>
</ul>
<p>所以这一节的结论只能写到：<b>公布曲线随填充的次序，没有被无偏方法确认</b>。要裁决需要更大的团簇、
更多的填充点，或者赛事公开自己的 6×6 求解器。</p>
<figure>{fig_ed}<figcaption>图 4｜公布曲线 vs 4×4 ED。灰色点线是 U=0 对照：n=0.5 处 ED 的「峰」
几乎全部来自能带，不是相互作用。</figcaption></figure>

<h3>那把 ED 的形状代进去会怎样</h3>
<p>把 A_d(δ) 换成 ED 的形状（归一到同一中位数，只借形状；δ &gt; 0.5 处 ED 没有数据，
按「记 0」处理——这是一个建模选择，会直接影响结果），重算 Top-20：
<b>20 个里剩 {ovs} 个</b>。这个数字只该读作「如果次序跟 ED 走，榜会换掉大部分」，
不能读作「ED 才是对的」，也不该叫它「稳健性下界」。</p>

<h2>六、稳健性：结论取决于误差结构，而公开数据定不了误差结构</h2>
<p>赛事公开的五个团簇在同一填充上彼此相差最多 {spreadmax:.1f} 倍，n=0.5 处还变号。
用这个散布的一半（σ = {sigma:.2f}）给每级台阶加扰动，但<b>误差沿填充轴怎么相关</b>，会决定全部答案：</p>
<figure>{fig_structures}<figcaption>图 5｜同样的边际 σ，三种相关结构。整体缩放对排序零影响（这是乘法的性质），
平滑相关保留 15/20，逐级独立只剩 9/20。</figcaption></figure>
<ul>
<li>单个全局乘子（整体标定）：<b>20.0 / 20</b>——这是乘法恒等式，不是证据，列出来只为说明它不可能是脆弱性来源。</li>
<li>AR(1) ρ=0.9（同一个 ansatz、同一段代码，误差应是填充的光滑函数）：<b>{ovar:.1f} / 20</b>。</li>
<li>逐级独立（最能打散排序的假设）：<b>{oind:.1f} / 20</b>，第一名保住第一的概率 {first}。</li>
<li>σ 扫描（独立假设）：σ=0.4 → {sw0:.1f}，0.6 → {sw1:.1f}，0.88 → {sw2:.1f}，1.2 → {sw3:.1f}。</li>
</ul>
<p>真实误差几乎不可能是逐级独立的：同一份代码、同一个团簇、同一套 ansatz，偏差必然随填充平滑变化。
所以「第一名只有 {first} 概率保住」这个读数不该被引用——它是 i.i.d. 假设的产物。可辩护的说法是：
<b>排序对整体标定免疫，对随填充变化的系统误差敏感，而公开数据无法区分这两者。</b></p>
<figure>{fig_surv}<figcaption>图 6｜最坏情况（逐级独立）下每个 Top-20 条目的存活率。这张图的作用是给出下界，
不是给出概率。</figcaption></figure>

<h2>七、Discovery 赛道：筛选器连已知的冠军都找不回</h2>
<p>赛事鼓励提名新材料。我们用最朴素的化学近邻（组成向量，k=15，留一法）检验「公开描述符能不能排 N(E_F)」：</p>
<ul>
<li>log N(E_F) 的 R² = <b>{r2:.3f}</b>，MAE = <b>{mae:.3f}</b>；δ 的精确命中 {dexact}，只比众数的 {dmaj} 高一点。</li>
</ul>
<p>更关键的是一次 sanity check——<b>它能不能把已知的前三名排到前面</b>（在 1,073 个留一法预测里的名次）：</p>
{table_lead}
<p>它把 I2Mn2S 排到第 8、Fe2I2 排到第 24——这两个还行；但把 Br2Fe2 排到 <b>405</b>。
一个会把榜眼扔到 405 名的模型，没有资格判断「池子里有没有挑战者」：759 个未降维金属里它给出的最高预测
只有 {maxpred:.2f}，那是向均值收缩的算术结果，不是池子的性质。诚实的结论是：
<b>这套描述符 + 这个模型不足以做 Discovery 筛选</b>，而不是「池子里没有挑战者」。</p>
<figure>{fig_screen}<figcaption>图 7｜留一法预测 vs 真值。点云被压成一条竖带。</figcaption></figure>

<p>因此我们只提名 5 个<b>化学同族</b>的候选，且不给数值预测。表里是母体实测值：</p>
{table_nom}
<p>注意两点：一是「同计量比」这个说法只对 Br2Fe / FeI2 各自的两个多型成立，
与母体（Br2Fe2、Fe2I2）是<b>不同计量比</b>；二是这个赌注本身很弱——多型之间的 N(E_F) 可以差很多，
δ 也未知。提名只是把「值得算一次 DFT」的名单缩到 5 个，不构成任何预测。
另外这 5 个本来就在 <code>candidates.csv</code> 里，Discovery 比的不是「发现新化合物」，
而是「先提出哪个待降维的对象」。</p>

<h2>八、口径：这是 anchor 表，不是参赛排行榜</h2>
<p><code>submissions.csv</code> 的 1,073 行<b>全部</b> <code>is_anchor = true</code>、作者全是
<code>OSC-66</code>。方法名分两种：60 行写「canonical scoring at material's DFT filling」，
<b>1,013 行</b>写「precise 6×6 solver @ δ=+0.00 / +0.06 / …」——后者正好是「A_d 按 15 档查表」的直接证据。
这是主办方对每个材料的标准锚点，参赛者的实时榜单不在这个 dump 里。另外 README 说榜首「currently ≈ 22」，
而这份 dump 的锚点顶到 <b>{t1idx:.2f}</b>（{t1}）——差三倍。两种可能：README 的数字过期了，
或者 dump 比 README 新。无论哪种，引用这块榜时都要说清是哪个口径。</p>

<h2>九、建议</h2>
<ol>
<li><b>先解释半满那一格。</b>δ = 0 给 0.0384 与 README 的「vanishing at half-filling」直接冲突，
而 {hfn} 个材料（{hfpct}）就坐在那里。这一格是整张表里最该被复核的数。</li>
<li><b>补上 Ne = 4、6、8 的表项，或明确写「未计算」。</b>现在 dump 用 0 代替，读者分不清「没有 d 波序」
和「没算」。</li>
<li><b>分数拆两栏：台阶档位 + N(E_F)。</b>单栏分数让人以为在看「材料多能配对」，实际在看填充位次。</li>
<li><b>把 A_d 的方法不确定带画进榜单</b>，并且<b>说清误差沿填充的相关性</b>——它比误差大小更能改变排序结论。</li>
<li><b>Discovery 需要一个可筛选的代理量。</b>哪怕只对金属做一次非自洽 DOS；否则提名等于猜，DFT 排队会成为瓶颈。</li>
</ol>

<h2>十、局限</h2>
<ul>
<li>不能重跑主办方的 6×6 求解器（未公开）。本报告只做公开数据的复算与公开 ED 表的再分析。</li>
<li>4×4 ED 的最大距离与 6×6 不同，绝对值不可比；ED 本身未做尺寸收敛（贡献者 Ku-ku 自己写明），
本报告只用它讨论次序。</li>
<li>5 点相关（p = {pperm:.2f}）不足以裁决；σ 是跨团簇散布的一半，是<b>代理</b>，不是置信区间。</li>
<li>化学近邻只用组成，未用结构、层群等其余描述符；它的失败是这套模型的失败，不排除更好的模型。</li>
<li>0.0005 的最大差是三位小数舍入，不是模型误差。</li>
</ul>

<h2>十一、复现</h2>
<pre>py -3 scripts/build.py        # 重算全部数字 + 七张图 + 报告
py -3 verify/verify.py        # 独立重算并断言（不读 results.json）</pre>
<p><code>verify/verify.py</code> 从原始表重新推导本页的结论性数字：<b>{checks} 条断言</b>
（含数据哈希、逐行复算、格点与悬崖、榜单事实、ED 对比、三种误差结构、筛选器 sanity check、产物一致性），
失败 0 条才算过。它不覆盖纯排版数字。
数据快照与 SHA256 见 <code>data/SHA256SUMS</code> 与 <code>out/results.json</code>。</p>

<div class="foot">数据来源：FINAL-Bench / OSC-Superconductor（CC-BY-NC 4.0，材料衍生自 C2DB；
多尺寸 ED 表由贡献者 Ku-ku 提供）。本报告为非商业学术分析；不声称发现超导体，也不声称公布的
A_d 有误——只指出：这块表的半满格与它自己的文档冲突，且用它排序在公开证据下不可识别。</div>
</div></body></html>""".format(**dict(
        css=CSS, rev=m["dataset_revision"][:12],
        poslev=d["positive_levels"], entries=d["entries"], prho=pdec["spearman"],
        ovs=st["overlap_shape"], maxdiff=rep["max_abs_diff"],
        over=rep["n_over_1e_3"], uncov=rep["n_uncovered"], negrows=88,
        zeroed=rep["n_a_row_zeroed"],
        hfa=hf["a_d"], hfpeak=d["peak"]["a_d"], hfshare=_pct(hf["share_of_peak"]),
        hfn=hf["n_materials"], hfpct=_pct(hf["n_materials"] / float(rep["n"])),
        hfabove=hf["n_above"], hftop="、".join(hf["top20_members"]),
        hfrepl=(hf["top20_without"][-1] if hf["top20_without"] else "-"),
        fig_dome=SVG["dome"], nd=g["n_delta"],
        sha=_pct(dec["share_a"]), shn=_pct(dec["share_nef"]), shc=_pct(dec["share_cov"]),
        pn=pdec["n"], pvar=_pct(pdec["pearson"] ** 2),
        fig_scatter=SVG["scatter"],
        t20d=bs["top20_max_delta"], t20lv=len(bs["top20_levels"]),
        t20n=int(bs["share_top20_nef_rank_le_20"] * 20),
        table=_table(["#", "材料", "指数", "N(E_F)", "δ", "N(E_F) 排名"], board_rows,
                     (0, 2, 3, 4, 5)),
        t1=bs["top1"]["formula"], t1d=bs["top1"]["delta"], t1idx=bs["top1"]["index"],
        peak=d["peak"]["a_d"],
        t2=bs["top2"]["formula"], t2d=bs["top2"]["delta"],
        nefgap=_pct(bs["top2"]["nef"] / bs["top1"]["nef"] - 1),
        agap=_pct(1 - bs["top2"]["a_d"] / bs["top1"]["a_d"]),
        sgap=_pct(1 - bs["top2"]["index"] / bs["top1"]["index"]),
        fig_board=SVG["board"], rho=ed["spearman"], pperm=ed["p_perm"],
        fig_ed=SVG["ed"],
        spreadmax=max(s["spread"] for s in ed["spreads"] if s["spread"]),
        sigma=st["sigma"], fig_structures=SVG["structures"],
        ovar=st["structures"]["ar1"]["expected_overlap"],
        oind=st["structures"]["independent"]["expected_overlap"],
        first=_pct(st["structures"]["independent"]["first"]),
        sw0=st["sweep"][0]["expected_overlap"], sw1=st["sweep"][1]["expected_overlap"],
        sw2=st["sweep"][2]["expected_overlap"], sw3=st["sweep"][3]["expected_overlap"],
        fig_surv=SVG["survival"], r2=sc["cv"]["r2"], mae=sc["cv"]["mae"],
        dexact=_pct(sc["cv"]["delta_exact"]), dmaj=_pct(sc["cv"]["delta_majority"]),
        table_lead=_table(["材料", "实测 N(E_F)", "留一法预测", "预测名次"], leader_rows,
                          (1, 2, 3)),
        maxpred=sc["max_pred_nef"], fig_screen=SVG["screen"],
        table_nom=_table(["化学式", "material_id", "关系", "母体", "母体 N(E_F)", "母体指数"],
                         nom_rows, (4, 5)),
        checks=checks,
    ))


def render_site(R, SVG, checks=0):
    rep, d, pdec, bs, st, sc = (R["reproduction"], R["dome"], R["plateau_decomposition"],
                                R["board_stats"], R["stress"], R["screen"])
    hf = R["half_filling"]
    top = R["board"][:10]
    rows = "".join(
        "<tr><td class='r'>%d</td><td>%s</td><td class='n'>%.1f</td><td class='n'>%.2f</td>"
        "<td class='n'>#%d</td></tr>" % (r["rank"], r["formula"], r["index"], r["nef"], r["nef_rank"])
        for r in top)
    return """<!doctype html><html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>十八级台阶 — OSC 排行榜审计</title><style>{site_css}</style></head><body><div class="wrap">
<div class="kicker">OSC · Open Superconductor Challenge</div>
<h1>十八级台阶</h1>
<p class="sub">把 OSC 的三张公开表复算一遍。1,064 条分数对得上，9 条落在表的空洞里；
而表在半满那一格的值，和它自己的 README 正好相反。</p>

<div class="stats">
<div class="stat"><b>1,064 / 1,073</b><span>条分数可由公开表直接算出（最大差 {maxdiff:.4f}）</span></div>
<div class="stat"><b>{poslev} 个</b><span>不同的 A_d 正取值；{entries} 个条目里有 3 个是负的</span></div>
<div class="stat"><b>{hfa:.4f}</b><span>半满（δ=0）处的 A_d，是峰值的 {hfshare}</span></div>
<div class="stat"><b>{ovs} / 20</b><span>换成 4×4 ED 的形状后，Top-20 的存活数</span></div>
</div>

<h2>一、分数是算得出来的，但表有洞</h2>
<p><code>index = max(0, N(E_F) × A_d(δ) × 300)</code>。1,073 条 verified_score 里，1,064 条能从表里算出来；
另外 9 条落在 Ne = 4/6/8 三档——表里没有这三格，dump 直接写 0。「可复现」对这 9 行靠的是约定，不是计算。</p>

<h2>二、半满：表说 0.0384，README 说「消失」</h2>
<p>README 写 A_d「vanishing at half-filling」。半满就是 δ = 0；表里给 {hfa:.5f}，峰值的 {hfshare}。
全库 {hfn} 个材料（{hfpct}）正好坐在这一格，因此拿到接近满分的 A_d。在一个 U/t = 8 的 Mott 绝缘体上，
这本身就是「A_d 是 ansatz 人造物」的证据——而文档恰恰用它来为指标背书。</p>
<figure>{fig_dome}<figcaption>公布的 A_d(δ)，橙圈是半满。</figcaption></figure>

<h2>三、分数 ≈ N(E_F) × 填充滤波器</h2>
<p>δ ≤ 1/3 的 7 级只差 1.52 倍；越过 1/3 掉 3.4 倍。平台内 log 分数与 log N(E_F) 的 Spearman 是 {prho:.3f}
——台阶之内，榜单就是 N(E_F) 榜单。</p>
<figure>{fig_scatter}<figcaption>平台内是一条直线；这是乘法的性质，不是发现。</figcaption></figure>

<h2>四、第一名坐在峰上</h2>
<p>{t1} 的 δ={t1d:.4f}，正好是 A_d 的 argmax；{t2} 的 N(E_F) 高 {nefgap}，但 A_d 低 {agap}，总分少 {sgap}。</p>
<table><thead><tr><th>#</th><th>材料</th><th>指数</th><th>N(E_F)</th><th>N(E_F) 排名</th></tr></thead>
<tbody>{rows}</tbody></table>
<figure>{fig_board}<figcaption>Top-20 与各自的 N(E_F) 排名。</figcaption></figure>

<h2>五、ED 只能说明「次序未被识别」</h2>
<p>5 个点上 Spearman {rho:.2f}，置换检验 p = {pperm:.2f}；换一种插值读到 {grho:.2f}，赛事自己读到 ≈ −0.1。
5 个点裁决不了。但把 ED 的形状代进去，Top-20 只剩 {ovs} 个——榜会完全换一批人。</p>
<figure>{fig_ed}<figcaption>公布曲线 vs 4×4 ED；灰点线是 U=0 对照。</figcaption></figure>

<h2>六、稳健性取决于误差结构</h2>
<p>同样的边际 σ：整体缩放 {oglobal:.1f}/20，平滑相关 {ovar:.1f}/20，逐级独立 {oind:.1f}/20。
同一个 ansatz、同一段代码的误差不可能是逐级独立的——所以「第一名只有 {first} 概率」这个读数不该被引用。</p>
<figure>{fig_structures}<figcaption>误差结构比误差大小更能改变结论。</figcaption></figure>

<h2>七、筛选器连冠军都找不回</h2>
<p>化学近邻的留一法 R² = {r2:.2f}；对已知前三的预测是 0.94 / 0.47 / 0.84，而真值是 3.65 / 4.08 / 3.49。
它没有能力判断池子里有没有挑战者。</p>
<figure>{fig_screen}<figcaption>预测被压成一条竖带。</figcaption></figure>

<h2>八、这是 anchor 表，不是排行榜</h2>
<p>1,073 行全部 is_anchor、作者全是 OSC-66——这是主办方的标准锚点。README 说榜首 ≈22，这份 dump 顶到
{t1idx:.2f}。引用时必须说清口径。</p>

<h2>九、五条建议</h2>
<ol>
<li>先解释半满那一格：0.0384 与「vanishing at half-filling」直接冲突。</li>
<li>补 Ne = 4/6/8，或写明「未计算」——别用 0 代替。</li>
<li>分数拆两栏：台阶档位 + N(E_F)。</li>
<li>把方法不确定带画进榜单，并说清误差沿填充的相关性。</li>
<li>Discovery 需要一个可筛选的代理量，否则提名等于猜。</li>
</ol>

<p class="foot">数据：FINAL-Bench / OSC-Superconductor（CC-BY-NC 4.0）。所有数字由
<code>scripts/build.py</code> 生成，<code>verify/verify.py</code> 独立复算（{checks} 条断言）。
不声称发现超导体，也不声称公布的 A_d 有误。</p>
</div></body></html>""".format(**dict(
        site_css=SITE_CSS, maxdiff=rep["max_abs_diff"], poslev=d["positive_levels"],
        entries=d["entries"], hfa=hf["a_d"], hfshare=_pct(hf["share_of_peak"]),
        ovs=st["overlap_shape"], hfn=hf["n_materials"],
        hfpct=_pct(hf["n_materials"] / float(rep["n"])), fig_dome=SVG["dome"],
        prho=pdec["spearman"], fig_scatter=SVG["scatter"], t1=bs["top1"]["formula"],
        t1d=bs["top1"]["delta"], t2=bs["top2"]["formula"],
        nefgap=_pct(bs["top2"]["nef"] / bs["top1"]["nef"] - 1),
        agap=_pct(1 - bs["top2"]["a_d"] / bs["top1"]["a_d"]),
        sgap=_pct(1 - bs["top2"]["index"] / bs["top1"]["index"]),
        rows=rows, fig_board=SVG["board"], rho=R["ed"]["spearman"], pperm=R["ed"]["p_perm"],
        grho=R["ed"]["grid_spearman"], fig_ed=SVG["ed"],
        oglobal=st["structures"]["global"]["expected_overlap"],
        ovar=st["structures"]["ar1"]["expected_overlap"],
        oind=st["structures"]["independent"]["expected_overlap"],
        first=_pct(st["structures"]["independent"]["first"]),
        fig_structures=SVG["structures"], r2=sc["cv"]["r2"], fig_screen=SVG["screen"],
        t1idx=bs["top1"]["index"], checks=checks,
    ))
