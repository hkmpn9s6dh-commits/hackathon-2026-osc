"""Can the published descriptors rank materials that have not been downfolded?

This is the question the Discovery track depends on. We answer it with the simplest
defensible model (chemical nearest neighbours in composition space) and report the
out-of-sample error honestly, including the negative result.
"""
import collections
import math
import re

ELEM = re.compile(r"([A-Z][a-z]?)(\d*)")


def composition(formula):
    d = {}
    for e, n in ELEM.findall(formula):
        d[e] = d.get(e, 0) + (int(n) if n else 1)
    return d


def vector(formula):
    c = composition(formula)
    tot = float(sum(c.values())) or 1.0
    return {e: n / tot for e, n in c.items()}


def cosine(a, b):
    if len(a) > len(b):
        a, b = b, a
    num = sum(v * b.get(k, 0.0) for k, v in a.items())
    na = math.sqrt(sum(v * v for v in a.values()))
    nb = math.sqrt(sum(v * v for v in b.values()))
    return num / (na * nb) if na and nb else 0.0


def knn(active, cand, k=15):
    """For every active material, the k most similar *other* actives (leave-one-out)."""
    vecs = {m["material_id"]: vector(m["formula"]) for m in active}
    ids = [m["material_id"] for m in active]
    s = {mid: [] for mid in ids}
    for i, a in enumerate(ids):
        va = vecs[a]
        for b in ids[i + 1:]:
            sim = cosine(va, vecs[b])
            s[a].append((sim, b))
            s[b].append((sim, a))
    out = {}
    for mid in ids:
        s[mid].sort(reverse=True)
        out[mid] = s[mid][:k]
    return out


def loo_cv(active, k=15):
    """Leave-one-out error of the composition-only screener."""
    nb = knn(active, None, k)
    amap = {m["material_id"]: m for m in active}
    log_nef = [math.log(m["nef"]) for m in active]
    mean_log = sum(log_nef) / len(log_nef)
    preds, dels, dtrue = [], [], []
    for m in active:
        ns = nb[m["material_id"]]
        w = [max(0.0, s) + 1e-6 for s, _ in ns]
        z = sum(wi * math.log(amap[mid]["nef"]) for wi, (_, mid) in zip(w, ns)) / sum(w)
        preds.append(z)
        dtrue.append(m["delta"])
        votes = collections.Counter()
        for wi, (_, mid) in zip(w, ns):
            votes[round(amap[mid]["delta"], 4)] += wi
        dels.append(votes.most_common(1)[0][0])
    n = len(preds)
    resid = [p - t for p, t in zip(preds, log_nef)]
    ss_res = sum(r * r for r in resid)
    ss_tot = sum((t - mean_log) ** 2 for t in log_nef)
    exact = sum(1 for a, b in zip(dels, dtrue) if abs(a - b) < 1e-6) / float(n)
    within = sum(1 for a, b in zip(dels, dtrue) if abs(a - b) <= 1 / 36.0 + 1e-6) / float(n)
    maj = collections.Counter(round(x, 4) for x in dtrue).most_common(1)[0][1] / float(n)
    rho = _pearson(preds, log_nef)
    return dict(k=k, n=n, mae=sum(abs(r) for r in resid) / n,
                r2=1 - ss_res / ss_tot, pearson=rho,
                delta_exact=exact, delta_within_one_step=within,
                delta_majority=maj)


def _pearson(a, b):
    n = len(a)
    ma, mb = sum(a) / n, sum(b) / n
    num = sum((x - ma) * (y - mb) for x, y in zip(a, b))
    den = math.sqrt(sum((x - ma) ** 2 for x in a) * sum((y - mb) ** 2 for y in b))
    return num / den if den else 0.0


def screen_pool(active, pool, k=15):
    """Predict nef and delta for the un-downfolded pool, with a neighbour-based range."""
    amap = {m["material_id"]: m for m in active}
    av = {m["material_id"]: vector(m["formula"]) for m in active}
    out = []
    for p in pool:
        v = vector(p["formula"])
        sims = sorted(((cosine(v, av[mid]), mid) for mid in av), reverse=True)[:k]
        w = [max(0.0, s) + 1e-6 for s, _ in sims]
        z = sum(wi * math.log(amap[mid]["nef"]) for wi, (_, mid) in zip(w, sims)) / sum(w)
        votes = collections.Counter()
        for wi, (_, mid) in zip(w, sims):
            votes[round(amap[mid]["delta"], 4)] += wi
        delta = votes.most_common(1)[0][0]
        nb_idx = sorted(max(0.0, m["nef"] * m["a_d"] * 300.0) for m in
                        (amap[mid] for _, mid in sims))
        out.append(dict(
            material_id=p["material_id"], osc_id=p["osc_id"], formula=p["formula"],
            family=p["family"],
            gap=p["gap"], sc_relevance=p["sc_relevance"],
            pred_nef=math.exp(z), pred_delta=delta,
            nb_index_p10=nb_idx[int(0.1 * len(nb_idx))],
            nb_index_p50=nb_idx[len(nb_idx) // 2],
            nb_index_p90=nb_idx[min(len(nb_idx) - 1, int(0.9 * len(nb_idx)))],
            neighbours=[mid for _, mid in sims[:5]],
            sim_top=sims[0][0],
        ))
    return out


def loo_pairs(active, k=15):
    """(true log N(E_F), predicted log N(E_F)) for every material, leave-one-out."""
    nb = knn(active, None, k)
    amap = {m["material_id"]: m for m in active}
    out = []
    for m in active:
        ns = nb[m["material_id"]]
        w = [max(0.0, s) + 1e-6 for s, _ in ns]
        z = sum(wi * math.log(amap[mid]["nef"]) for wi, (_, mid) in zip(w, ns)) / sum(w)
        out.append((math.log(m["nef"]), z))
    return out
