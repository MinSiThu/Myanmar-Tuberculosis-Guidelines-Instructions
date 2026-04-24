"""
temporal_stats.py
─────────────────────────────────────────────────────────
Simple stats-based temporal evolution checker for the
Myanmar-TB instruction dataset.

No embeddings. No ML. Just counts, overlaps, and diffs.

Usage
-----
  python temporal_stats.py --file data.tsv
  python temporal_stats.py --file data.tsv --col-date year --top 20
  python temporal_stats.py --file data.tsv --group category

The script expects one of:
  A) A 'year' / 'version' / 'date' column in the TSV  →  groups by that
  B) A 'category' column                               →  groups by that
  C) No grouping column                                →  splits first/last half

What it shows
-------------
  1. Per-group vocabulary size & unique terms
  2. Jaccard overlap between consecutive groups
  3. New terms introduced  /  terms dropped
  4. Top-K term frequency shift (TF ratio new/old)
  5. Avg instruction & response length trend
  6. Category distribution shift (if applicable)
"""

import re
import sys
import csv
import argparse
import math
from pathlib import Path
from collections import Counter
from typing import Optional


# ─────────────────────────────────────────────────────────
# 1. LOAD
# ─────────────────────────────────────────────────────────

STOPWORDS = {
    # English
    "the","a","an","is","are","was","were","be","been","being",
    "have","has","had","do","does","did","will","would","could",
    "should","may","might","shall","to","of","in","on","at","for",
    "with","by","from","as","that","this","it","its","and","or",
    "not","but","if","so","then","there","their","they","we","you",
    "he","she","i","my","your","our","what","how","when","which",
    "all","any","can","also","than","more","no","yes","per","about",
    # Common Burmese particles (transliterated approximation)
    "သည်","သာ","ကို","မှ","နှင့်","တွင်","တော့","လည်း","ကြောင့်",
    "ဖြင့်","အတွက်","မည်","ရမည်","ရန်","သော","ဟု","ပြု","ခြင်း",
}

def tokenize(text: str) -> list[str]:
    """Simple whitespace + punctuation tokenizer, lowercased."""
    tokens = re.findall(r'[\u1000-\u109F\uA9E0-\uA9FF]+|[a-zA-Z0-9]+', text.lower())
    return [t for t in tokens if len(t) > 1 and t not in STOPWORDS]


def load_tsv(path: str) -> tuple[list[str], list[dict]]:
    p = Path(path)
    sep = "\t" if p.suffix in (".tsv", ".txt") else ","
    with open(path, encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=sep)
        rows = [dict(r) for r in reader]
    headers = list(rows[0].keys()) if rows else []
    return headers, rows


def find_col(headers: list[str], aliases: list[str]) -> Optional[str]:
    for a in aliases:
        for h in headers:
            if h.strip().lower() == a:
                return h
    return None


# ─────────────────────────────────────────────────────────
# 2. GROUP ROWS
# ─────────────────────────────────────────────────────────

def group_rows(rows: list[dict], headers: list[str], group_by: Optional[str]) -> dict[str, list[dict]]:
    """Return OrderedDict-like groups, sorted by key."""

    # auto-detect group column
    if group_by:
        col = find_col(headers, [group_by])
    else:
        col = (
            find_col(headers, ["year","version","date","period","era"]) or
            find_col(headers, ["category","label","type","domain"])
        )

    if col:
        groups: dict[str, list] = {}
        for r in rows:
            key = r.get(col, "unknown").strip()
            groups.setdefault(key, []).append(r)
        # sort keys (works for years or alphabetical categories)
        try:
            return dict(sorted(groups.items(), key=lambda x: int(re.sub(r'\D','',x[0]) or 0)))
        except Exception:
            return dict(sorted(groups.items()))
    else:
        # fallback: split into halves labelled "first_half" / "second_half"
        mid = len(rows) // 2
        return {"first_half": rows[:mid], "second_half": rows[mid:]}


# ─────────────────────────────────────────────────────────
# 3. PER-GROUP STATS
# ─────────────────────────────────────────────────────────

def group_stats(rows: list[dict], instr_col: str, resp_col: str) -> dict:
    all_tokens: list[str] = []
    instr_lens, resp_lens = [], []

    for r in rows:
        instr = r.get(instr_col, "")
        resp  = r.get(resp_col,  "")
        toks  = tokenize(instr + " " + resp)
        all_tokens.extend(toks)
        instr_lens.append(len(instr.split()))
        resp_lens.append(len(resp.split()))

    freq   = Counter(all_tokens)
    vocab  = set(all_tokens)
    n      = len(rows)

    def avg(lst): return round(sum(lst)/len(lst), 1) if lst else 0

    return {
        "n":            n,
        "vocab_size":   len(vocab),
        "total_tokens": len(all_tokens),
        "ttr":          round(len(vocab) / len(all_tokens), 4) if all_tokens else 0,
        "freq":         freq,
        "vocab":        vocab,
        "avg_instr_words": avg(instr_lens),
        "avg_resp_words":  avg(resp_lens),
    }


# ─────────────────────────────────────────────────────────
# 4. EVOLUTION METRICS BETWEEN TWO GROUPS
# ─────────────────────────────────────────────────────────

def jaccard(a: set, b: set) -> float:
    u = len(a | b)
    return round(len(a & b) / u, 4) if u else 0.0


def new_terms(old: set, new: set, old_freq: Counter, new_freq: Counter,
              top_k: int = 15) -> list[tuple[str,int]]:
    """Terms in new not in old, sorted by new frequency."""
    added = new - old
    return sorted([(t, new_freq[t]) for t in added], key=lambda x: -x[1])[:top_k]


def dropped_terms(old: set, new: set, old_freq: Counter,
                  top_k: int = 15) -> list[tuple[str,int]]:
    """Terms in old not in new, sorted by old frequency."""
    removed = old - new
    return sorted([(t, old_freq[t]) for t in removed], key=lambda x: -x[1])[:top_k]


def frequency_shift(old_freq: Counter, new_freq: Counter,
                    old_n: int, new_n: int,
                    top_k: int = 20) -> list[dict]:
    """
    Compute relative frequency shift for shared terms.
    rf_old = count/total_tokens_old
    shift  = rf_new / rf_old  (>1 = grew, <1 = shrank)
    """
    shared = set(old_freq) & set(new_freq)
    old_total = sum(old_freq.values()) or 1
    new_total = sum(new_freq.values()) or 1

    results = []
    for t in shared:
        rf_old = old_freq[t] / old_total
        rf_new = new_freq[t] / new_total
        ratio  = rf_new / rf_old if rf_old else 0
        results.append({
            "term":   t,
            "old_rf": round(rf_old * 1000, 2),  # per-mille
            "new_rf": round(rf_new * 1000, 2),
            "ratio":  round(ratio, 2),
        })

    # top movers: sort by abs log ratio
    results.sort(key=lambda x: abs(math.log(x["ratio"] + 1e-9)), reverse=True)
    return results[:top_k]


# ─────────────────────────────────────────────────────────
# 5. DISPLAY
# ─────────────────────────────────────────────────────────

SEP = "─" * 60

def _bar(value: float, max_val: float, width: int = 20) -> str:
    filled = int(width * value / max_val) if max_val else 0
    return "█" * filled + "░" * (width - filled)


def print_header(title: str):
    print(f"\n{'═'*60}")
    print(f"  {title}")
    print(f"{'═'*60}")


def print_group_overview(groups: dict, stats_map: dict):
    print_header("GROUP OVERVIEW")
    print(f"  {'Group':<25} {'N':>6} {'Vocab':>7} {'TTR':>6} {'AvgInstr':>9} {'AvgResp':>8}")
    print(f"  {SEP}")
    max_vocab = max(s["vocab_size"] for s in stats_map.values()) or 1
    for g, s in stats_map.items():
        bar = _bar(s["vocab_size"], max_vocab, 12)
        print(f"  {g:<25} {s['n']:>6} {s['vocab_size']:>7} {s['ttr']:>6.3f} "
              f"{s['avg_instr_words']:>9} {s['avg_resp_words']:>8}  {bar}")


def print_pairwise(group_keys: list, stats_map: dict, top_k: int):
    print_header("PAIRWISE EVOLUTION  (consecutive groups)")

    pairs = list(zip(group_keys[:-1], group_keys[1:]))
    for old_key, new_key in pairs:
        old = stats_map[old_key]
        new = stats_map[new_key]

        jac = jaccard(old["vocab"], new["vocab"])
        drift = 1.0 - jac

        print(f"\n  {old_key}  →  {new_key}")
        print(f"  {SEP}")
        print(f"  Jaccard vocab overlap : {jac:.3f}  (drift = {drift:.3f})")

        # vocab size change
        delta_v = new["vocab_size"] - old["vocab_size"]
        sign = "+" if delta_v >= 0 else ""
        print(f"  Vocab size change     : {old['vocab_size']} → {new['vocab_size']}  ({sign}{delta_v})")

        # response length trend
        delta_r = new["avg_resp_words"] - old["avg_resp_words"]
        sign = "+" if delta_r >= 0 else ""
        print(f"  Avg response length   : {old['avg_resp_words']} → {new['avg_resp_words']} words  ({sign}{delta_r:.1f})")

        # new terms
        added = new_terms(old["vocab"], new["vocab"], old["freq"], new["freq"], top_k)
        if added:
            terms_str = "  ".join(f"{t}({c})" for t, c in added[:10])
            print(f"\n  🆕 New terms ({len(new['vocab'] - old['vocab'])} total, top shown):")
            print(f"     {terms_str}")

        # dropped terms
        dropped = dropped_terms(old["vocab"], new["vocab"], old["freq"], top_k)
        if dropped:
            terms_str = "  ".join(f"{t}({c})" for t, c in dropped[:10])
            print(f"\n  ❌ Dropped terms ({len(old['vocab'] - new['vocab'])} total, top shown):")
            print(f"     {terms_str}")

        # frequency shift
        shifts = frequency_shift(old["freq"], new["freq"],
                                  old["n"], new["n"], top_k)
        if shifts:
            print(f"\n  📈 Biggest frequency shifts (shared terms):")
            print(f"     {'Term':<20} {'Old‰':>6} {'New‰':>6} {'Ratio':>7}  Direction")
            print(f"     {'─'*55}")
            for s in shifts[:12]:
                arrow = "↑↑" if s["ratio"] > 2 else ("↑" if s["ratio"] > 1.1
                        else ("↓↓" if s["ratio"] < 0.5 else "↓"))
                print(f"     {s['term']:<20} {s['old_rf']:>6.2f} {s['new_rf']:>6.2f} "
                      f"{s['ratio']:>7.2f}x  {arrow}")


def print_drift_timeline(group_keys: list, stats_map: dict):
    """Show vocabulary overlap / drift as a simple timeline."""
    if len(group_keys) < 2:
        return
    print_header("DRIFT TIMELINE  (Jaccard overlap vs first group)")
    baseline_vocab = stats_map[group_keys[0]]["vocab"]
    baseline_key   = group_keys[0]
    print(f"\n  Baseline: {baseline_key}  (vocab={len(baseline_vocab)})\n")
    print(f"  {'Group':<25} {'Overlap':>8}  {'Drift':>6}  Bar")
    print(f"  {SEP}")
    for k in group_keys:
        v = stats_map[k]["vocab"]
        jac = jaccard(baseline_vocab, v)
        bar = _bar(jac, 1.0, 25)
        print(f"  {k:<25} {jac:>8.3f}  {1-jac:>6.3f}  {bar}")


def print_top_terms_per_group(group_keys: list, stats_map: dict, top_k: int = 10):
    print_header(f"TOP {top_k} TERMS PER GROUP")
    for k in group_keys:
        top = stats_map[k]["freq"].most_common(top_k)
        terms = "  ".join(f"{t}({c})" for t, c in top)
        print(f"\n  {k}:")
        print(f"    {terms}")


# ─────────────────────────────────────────────────────────
# 6. MAIN
# ─────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Simple stats-based temporal evolution for instruction datasets"
    )
    parser.add_argument("--file",     required=True, help="Path to .tsv or .csv")
    parser.add_argument("--group",    default=None,
                        help="Column to group by (default: auto-detect year/version/category)")
    parser.add_argument("--top",      type=int, default=15,
                        help="Top-K terms to show per diff (default: 15)")
    parser.add_argument("--no-drift", action="store_true",
                        help="Skip drift timeline")
    parser.add_argument("--no-top",   action="store_true",
                        help="Skip top terms per group")
    args = parser.parse_args()

    # load
    print(f"\nLoading: {args.file}")
    headers, rows = load_tsv(args.file)
    print(f"Loaded {len(rows)} rows  |  Columns: {headers}")

    instr_col = find_col(headers, ["instruction","input","question","prompt"]) or headers[0]
    resp_col  = find_col(headers, ["response","output","answer","completion"])  or headers[1]
    print(f"Using   instruction='{instr_col}'  response='{resp_col}'")

    # group
    groups = group_rows(rows, headers, args.group)
    print(f"\nGroups ({len(groups)}): {list(groups.keys())}")

    if len(groups) < 2:
        print("\n[!] Need at least 2 groups to compare. "
              "Check your --group column or add a version/year column.")
        sys.exit(1)

    # compute stats per group
    stats_map = {k: group_stats(v, instr_col, resp_col) for k, v in groups.items()}
    group_keys = list(groups.keys())

    # display
    print_group_overview(groups, stats_map)
    print_pairwise(group_keys, stats_map, args.top)
    if not args.no_drift:
        print_drift_timeline(group_keys, stats_map)
    if not args.no_top:
        print_top_terms_per_group(group_keys, stats_map, top_k=10)

    print(f"\n{'═'*60}")
    print("  Done.")
    print(f"{'═'*60}\n")


if __name__ == "__main__":
    main()