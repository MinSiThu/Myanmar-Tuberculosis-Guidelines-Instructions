"""
myanmar_tb_full_analyzer.py  (v2)
==================================
Unified NLP Analyzer — Myanmar TB NTP Bilingual Dataset (EN + Burmese)

Fixes vs v1:
  - Large-dataset charts: aggregated / summary views instead of per-row bars
  - Burmese text rendering via NotoSansMyanmar font (no glyph boxes)
  - Rolling-window smoothing for length/readability trend charts
  - Pagination-safe: works with any number of rows

Usage:
  python myanmar_tb_full_analyzer.py               # built-in sample
  python myanmar_tb_full_analyzer.py dataset.tsv   # your file
Outputs:
  myanmar_tb_nlp.log
  chart1_overview.png  chart2_en_lengths.png  chart3_en_vocab.png
  chart4_en_misc.png   chart5_my_lengths.png  chart6_my_chars.png
  chart7_my_syllables.png  chart8_bilingual_dashboard.png
"""

import re, sys, csv, io, math, os, logging, warnings
from collections import Counter
from datetime import datetime

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import matplotlib.gridspec as gridspec
import numpy as np

warnings.filterwarnings("ignore", category=UserWarning, module="matplotlib")

try:
    from pyidaungsu import tokenize as pids_tok
    HAVE_PIDS = True
except ImportError:
    HAVE_PIDS = False

# ── Myanmar font ───────────────────────────────────────────────────────────────
_MY_FONT_PATH = "/usr/share/fonts/truetype/noto/NotoSansMyanmar-Regular.ttf"
if os.path.exists(_MY_FONT_PATH):
    MY_FONT  = fm.FontProperties(fname=_MY_FONT_PATH, size=8)
    MY_FONT9 = fm.FontProperties(fname=_MY_FONT_PATH, size=9)
    MY_FONT7 = fm.FontProperties(fname=_MY_FONT_PATH, size=7)
    HAS_MY_FONT = True
else:
    MY_FONT = MY_FONT9 = MY_FONT7 = None
    HAS_MY_FONT = False

def my_label(ax_set_fn, labels):
    """Set axis labels using Myanmar font if available, else plain text."""
    ax_set_fn(labels)
    if HAS_MY_FONT:
        for lbl in (ax_set_fn.__self__.get_xticklabels()
                    if 'x' in ax_set_fn.__name__ else
                    ax_set_fn.__self__.get_yticklabels()):
            lbl.set_fontproperties(MY_FONT)

# ── Config ─────────────────────────────────────────────────────────────────────
LOG_PATH   = "myanmar_tb_nlp.log"
PALETTE    = ["#e94560","#0f3460","#2b9348","#533483","#e76f51","#457b9d","#a8dadc","#f4a261"]
FONT_COLOR = "#1a1a2e"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler(LOG_PATH, encoding="utf-8", mode="w"),
        logging.StreamHandler(),
    ],
)
log = logging.getLogger("TB-FULL")

# ══════════════════════════════════════════════════════════════════════════════
# SAMPLE DATA
# ══════════════════════════════════════════════════════════════════════════════
SAMPLE_TSV = """id\tinstruction_en\tinstruction_my\tresponse_en\tresponse_my\tcategory\tsource\tguideline_version\tnotes
TB-NTP-001\tWhat is the primary healthcare strategy used by Myanmar National TB Programme?\tမြန်မာနိုင်ငံ အမျိုးသား တီဘီရောဂါ တိုက်ဖျက်ရေး စီမံကိန်းသည် မည်သည့် ကျန်းမာရေး နည်းဗျူဟာကို အသုံးပြုသနည်း။\tMyanmar National TB Programme uses a primary healthcare strategy to accelerate TB control activities.\tမြန်မာနိုင်ငံအမျိုးသား တီဘီရောဂါ တိုက်ဖျက်ရေး စီမံကိန်း သည် ပဏာမ ကျန်းမာရေး စောင့်ရှောက်မှု နည်းဗျူဟာကို အသုံးပြု၍ တီဘီရောဂါ တိုက်ဖျက်ရေး လုပ်ငန်းများ ကို အရှိန်အဟုန်မြှင့် ဆောင်ရွက်ပါသည်။\tHealthcare worker training\tMyanmar NTP\t2024\tPrimary healthcare approach
TB-NTP-002\tWhat is the current status of tuberculosis in Myanmar?\tမြန်မာနိုင်ငံတွင် တီဘီရောဂါ၏ လက်ရှိ အခြေအနေမှာ မည်သို့နည်း။\tTuberculosis remains a major health problem in Myanmar.\tတီဘီရောဂါသည် မြန်မာနိုင်ငံ ၏ အဓိက ကျန်းမာရေး ပြဿနာ အဖြစ် တည်ရှိနေဆဲဖြစ်ပါသည်။\tPatient education\tMyanmar NTP\t2024\tCurrent TB situation in Myanmar
TB-NTP-003\tWhat is the general objective of Myanmar National TB Programme?\tမြန်မာနိုင်ငံ အမျိုးသား တီဘီရောဂါ တိုက်ဖျက်ရေး စီမံကိန်း၏ ယေဘုယျ ရည်မှန်းချက်မှာ အဘယ်နည်း။\tThe general objective is to eliminate TB as a major health problem in Myanmar and improve the health status of the population, using a primary healthcare approach to accelerate TB control activities.\tယေဘုယျ ရည်မှန်းချက်မှာ ပဏာမကျန်းမာရေး စောင့်ရှောက်မှု နည်းဗျူဟာကိုအသုံးပြု၍ တီဘီရောဂါတိုက်ဖျက်ရေး စီမံကိန်းလုပ်ငန်းများကို အရှိန်အဟုန်မြှင့်ဆောင်ရွက်ခြင်းဖြင့် တီဘီရောဂါသည် မြန်မာနိုင်ငံ၏ အဓိကကျန်းမာရေးပြဿနာအဖြစ် မတည်ရှိတော့ပဲ ပြည်သူလူထူ၏ ကျန်းမာရေးအဆင့်အတန်း တိုးတက်မြင့်မားလာစေရန် ဖြစ်ပါသည်။\tHealthcare worker training\tMyanmar NTP\t2024\tGeneral objective - TB elimination goal
TB-NTP-004\tHow many specific objectives does Myanmar National TB Programme have?\tမြန်မာနိုင်ငံ အမျိုးသား တီဘီရောဂါ တိုက်ဖျက်ရေး စီမံကိန်းတွင် တိကျသော ရည်ရွယ်ချက် ဘယ်နှစ်ခု ရှိသနည်း။\tMyanmar National TB Programme has three specific objectives.\tမြန်မာနိုင်ငံ အမျိုးသား တီဘီရောဂါ တိုက်ဖျက်ရေး စီမံကိန်းတွင် ရည်ရွယ်ချက် သုံးခု ရှိပါသည်။\tHealthcare worker training\tMyanmar NTP\t2024\tThree objectives total
TB-NTP-005\tWhat is the first objective of Myanmar National TB Programme?\tမြန်မာနိုင်ငံ အမျိုးသား တီဘီရောဂါ တိုက်ဖျက်ရေး စီမံကိန်း၏ ပထမ ရည်ရွယ်ချက်မှာ အဘယ်နည်း။\tThe first objective is to accelerate the reduction of TB and drug-resistant TB incidence.\tပထမ ရည်ရွယ်ချက်မှာ တီဘီရောဂါ နှင့် ဆေးယဉ်ပါး တီဘီရောဂါ ဖြစ်ပွားမှု လျော့ချနိုင်ရေး ကို အရှိန်အဟုန် မြှင့် ဆောင်ရွက်ရန် ဖြစ်ပါသည်။\tDrug-resistant TB (MDR-TB)\tMyanmar NTP\t2024\tFirst objective - reduce incidence
TB-NTP-006\tWhat is the second objective of Myanmar National TB Programme?\tမြန်မာနိုင်ငံ အမျိုးသား တီဘီရောဂါ တိုက်ဖျက်ရေး စီမံကိန်း၏ ဒုတိယ ရည်ရွယ်ချက်မှာ အဘယ်နည်း။\tThe second objective is to integrate TB prevention and treatment as universal health coverage accessible to all people.\tဒုတိယ ရည်ရွယ်ချက်မှာ တီဘီရောဂါ ကာကွယ် ကုသခြင်း လုပ်ငန်းကို ပြည်သူ တစ်ရပ်လုံး လက်လှမ်း မီသော ကျန်းမာရေး စောင့်ရှောက်မှု အဖြစ် ထည့်သွင်း ဆောင်ရွက်ရန် ဖြစ်ပါသည်။\tTreatment guidelines\tMyanmar NTP\t2024\tSecond objective - universal health coverage"""

# ══════════════════════════════════════════════════════════════════════════════
# LOADER
# ══════════════════════════════════════════════════════════════════════════════
def load_dataset(path):
    if path and os.path.exists(path):
        log.info(f"Loading: {path}")
        with open(path, encoding="utf-8") as f:
            s = f.read(1024); f.seek(0)
            delim = "\t" if "\t" in s else ","
            rows = [r for r in csv.DictReader(f, delimiter=delim) if r.get("id","").strip()]
    else:
        log.info("Using built-in sample")
        rows = [r for r in csv.DictReader(io.StringIO(SAMPLE_TSV), delimiter="\t")
                if r.get("id","").strip()]
    log.info(f"Loaded {len(rows)} records")
    return rows

# ══════════════════════════════════════════════════════════════════════════════
# ENGLISH NLP HELPERS
# ══════════════════════════════════════════════════════════════════════════════
EN_STOP = {
    "a","an","the","is","are","was","were","be","been","being","have","has","had",
    "do","does","did","will","would","shall","should","may","might","must","can",
    "could","to","of","in","for","on","with","at","by","from","as","into","what",
    "how","many","which","that","this","it","its","and","or","not","no","so","if",
    "myanmar","national","tb","programme","ntp","using","use","uses",
}
MEDICAL_TERMS = ["tuberculosis","tb","drug","resistant","mdr","healthcare","treatment",
    "prevention","incidence","elimination","objective","programme","coverage",
    "control","strategy","accelerate","health","problem","population","integrate","primary"]

def tok_en(t): return [w.lower() for w in re.findall(r"[a-zA-Z]+", t)]
def sent_c(t):  return max(1, len(re.findall(r"[.!?]+", t)))
def ttr(tk):    return round(len(set(tk))/len(tk), 4) if tk else 0
def avg_wl(tk): return round(sum(len(t) for t in tk)/len(tk), 2) if tk else 0
def ent(tk):
    if not tk: return 0
    f = Counter(tk); n = len(tk)
    return round(-sum((c/n)*math.log2(c/n) for c in f.values()), 4)
def kw(tk, n=12):
    return Counter(t for t in tk if t not in EN_STOP and len(t)>2).most_common(n)
def q_type(t):
    s = t.lower().strip()
    for w in ["what is","what are","how many","how does","why","when","where","who","which"]:
        if s.startswith(w): return w.split()[0].upper()
    return "OTHER"
def fk(text):
    w = tok_en(text); s = sent_c(text)
    syl = sum(max(1, len(re.findall(r'[aeiouAEIOU]', x))) for x in w)
    return round(206.835 - 1.015*(len(w)/s) - 84.6*(syl/max(len(w),1)), 2) if w else 0
def overlap(a, b):
    s1 = set(tok_en(a))-EN_STOP; s2 = set(tok_en(b))-EN_STOP
    return round(len(s1&s2)/len(s1), 4) if s1 else 0

def smooth(arr, w=5):
    """Rolling mean with min_periods=1."""
    out = []
    for i in range(len(arr)):
        sl = arr[max(0,i-w//2):i+w//2+1]
        out.append(sum(sl)/len(sl))
    return out

# ══════════════════════════════════════════════════════════════════════════════
# BURMESE NLP HELPERS
# ══════════════════════════════════════════════════════════════════════════════
MY_CONSONANTS = set(chr(c) for c in range(0x1000,0x1022))
MY_VOWELS     = {chr(c) for c in [0x102B,0x102C,0x102D,0x102E,0x102F,0x1030,0x1031,0x1032,0x1036,0x1038]}
MY_DIACRITICS = {chr(c) for c in [0x103A,0x103B,0x103C,0x103D,0x103E,0x1039,0x1037]}
MY_PUNCT      = {"\u104A","\u104B","?","!",".",","}
MY_DIGITS     = set(chr(c) for c in range(0x1040,0x104A))
MY_PARTICLES  = {
    "သည်","သော","သည့်","ကို","မှ","မှာ","တွင်","တော့","၏","၍","ရဲ့",
    "နှင့်","ဖြင့်","အဖြစ်","ပါ","ပါသည်","သနည်း","လား","နည်း",
    "ဖြစ်","ရှိ","ကြ","လည်း","မ","မည်","မှု","နေ","ဆဲ","ခြင်း","ရန်","စေ",
}
DOMAIN_SW = MY_PARTICLES | {
    "မြန်မာနိုင်ငံ","မြန်မာ","နိုင်ငံ","တီဘီ","ရောဂါ","စီမံကိန်း","အမျိုးသား","တိုက်ဖျက်ရေး",
}
_SYL_RE = re.compile(
    r"[\u1000-\u1021\u1025\u1026\u103F\u1040-\u1049]"
    r"[\u1031\u103B-\u103E]*[\u102B-\u1032\u1036-\u1038\u103A\u1039\u1037]*"
    r"(?:\u1039[\u1000-\u1021])?[\u102B-\u1032\u1036-\u1038\u103A\u1039\u1037]*", re.UNICODE)

def tok_my_w(t):
    if HAVE_PIDS:
        try: return pids_tok(t, form="word")
        except: pass
    return [x for x in re.split(r"[\s။၊]+", t.strip()) if x]

def tok_my_s(t):
    if HAVE_PIDS:
        try: return pids_tok(t, form="syllable")
        except: pass
    return [x for x in _SYL_RE.findall(t) if x.strip()]

def char_cls(c):
    if c in MY_CONSONANTS: return "CONSONANT"
    if c in MY_VOWELS:     return "VOWEL"
    if c in MY_DIACRITICS: return "DIACRITIC"
    if c in MY_DIGITS:     return "MY_DIGIT"
    if c in MY_PUNCT:      return "PUNCT"
    if c == " ":           return "SPACE"
    if "\u1000"<=c<="\u109F": return "MY_OTHER"
    return "OTHER"

def my_ratio(t):
    return round(sum(1 for c in t if "\u1000"<=c<="\u109F")/len(t), 4) if t else 0

def rm_p(tk):  return [t for t in tk if not all(c in MY_PUNCT for c in t)]
def rm_sw(tk): return [t for t in tk if t not in MY_PARTICLES]
def rm_dw(tk): return [t for t in tk if t not in DOMAIN_SW]

# ══════════════════════════════════════════════════════════════════════════════
# COMPUTE ALL STATS
# ══════════════════════════════════════════════════════════════════════════════
def compute_all(records):
    en_rows, my_rows = [], []
    all_en_i, all_en_r = [], []
    all_my_w, all_my_s = [], []
    all_char_dist = Counter()

    for r in records:
        # ── English
        ei = tok_en(r.get("instruction_en",""))
        er = tok_en(r.get("response_en",""))
        all_en_i.extend(ei); all_en_r.extend(er)
        en_rows.append({
            "id": r["id"], "cat": r.get("category",""),
            "instr_wc": len(ei), "resp_wc": len(er),
            "instr_cc": len(r.get("instruction_en","")), "resp_cc": len(r.get("response_en","")),
            "instr_sents": sent_c(r.get("instruction_en","")),
            "resp_sents":  sent_c(r.get("response_en","")),
            "instr_ttr": ttr(ei), "resp_ttr": ttr(er),
            "instr_ent": ent(ei), "resp_ent": ent(er),
            "fk_instr":  fk(r.get("instruction_en","")),
            "fk_resp":   fk(r.get("response_en","")),
            "overlap":   overlap(r.get("instruction_en",""), r.get("response_en","")),
            "qtype":     q_type(r.get("instruction_en","")),
            "instr_awl": avg_wl(ei), "resp_awl": avg_wl(er),
        })
        # ── Burmese
        iw = tok_my_w(r.get("instruction_my",""))
        rw = tok_my_w(r.get("response_my",""))
        is_ = tok_my_s(r.get("instruction_my",""))
        rs  = tok_my_s(r.get("response_my",""))
        for txt in [r.get("instruction_my",""), r.get("response_my","")]:
            all_char_dist += Counter(char_cls(c) for c in txt)
        all_my_w.extend(iw); all_my_w.extend(rw)
        all_my_s.extend(is_); all_my_s.extend(rs)

        iw_c = rm_dw(rm_sw(rm_p(iw))); rw_c = rm_dw(rm_sw(rm_p(rw)))
        ip = round(sum(1 for t in iw if t in MY_PARTICLES)/max(len(iw),1), 4)
        rp = round(sum(1 for t in rw if t in MY_PARTICLES)/max(len(rw),1), 4)
        my_rows.append({
            "id": r["id"], "cat": r.get("category",""),
            "instr_wc": len(iw), "resp_wc": len(rw),
            "instr_sc": len(is_), "resp_sc": len(rs),
            "instr_cc": len(r.get("instruction_my","")),
            "resp_cc":  len(r.get("response_my","")),
            "instr_my_ratio": my_ratio(r.get("instruction_my","")),
            "resp_my_ratio":  my_ratio(r.get("response_my","")),
            "instr_pr": ip, "resp_pr": rp,
            "instr_asw": round(len(is_)/max(len(iw),1),2),
            "resp_asw":  round(len(rs)/max(len(rw),1),2),
            "instr_content": iw_c, "resp_content": rw_c,
            "instr_ttr": ttr(rm_p(iw)), "resp_ttr": ttr(rm_p(rw)),
            "instr_ent": ent(iw), "resp_ent": ent(rw),
        })

    syl_per_word = [len(tok_my_s(w)) for w in all_my_w if w.strip()]
    sc_dist  = Counter(syl_per_word)
    p_counts = Counter(t for t in all_my_w if t in MY_PARTICLES)
    return en_rows, my_rows, all_en_i, all_en_r, all_my_w, all_my_s, all_char_dist, sc_dist, p_counts

# ══════════════════════════════════════════════════════════════════════════════
# LOGGING
# ══════════════════════════════════════════════════════════════════════════════
def sec(title):
    log.info(""); log.info("="*70); log.info(f"  {title}"); log.info("="*70)

def log_all(records, en_rows, my_rows, all_en_i, all_en_r, all_my_w, all_my_s,
            all_char_dist, sc_dist, p_counts):
    cats = Counter(r.get("category","") for r in records)
    sec("DATASET DESCRIPTION & SUMMARY")
    log.info(f"  Records   : {len(records)}")
    log.info(f"  Languages : English + Burmese")
    log.info(f"  Source    : {records[0].get('source','')}  v{records[0].get('guideline_version','')}")
    log.info(f"  Categories:")
    for c, n in cats.most_common(): log.info(f"    [{n}] {c}")

    def st(arr): return f"min={min(arr)} max={max(arr)} avg={round(sum(arr)/len(arr),1)}"
    log.info(f"\n  Word counts — EN instruction : {st([p['instr_wc'] for p in en_rows])}")
    log.info(f"  Word counts — EN response    : {st([p['resp_wc']  for p in en_rows])}")
    log.info(f"  Word counts — MY instruction : {st([p['instr_wc'] for p in my_rows])}")
    log.info(f"  Word counts — MY response    : {st([p['resp_wc']  for p in my_rows])}")

    sec("ENGLISH NLP")
    log.info(f"  Corpus vocab (instr) : {len(set(all_en_i))} unique / {len(all_en_i)} total  TTR={ttr(all_en_i)}")
    log.info(f"  Corpus vocab (resp)  : {len(set(all_en_r))} unique / {len(all_en_r)} total  TTR={ttr(all_en_r)}")
    log.info(f"  Top instr keywords   : {kw(all_en_i, 8)}")
    log.info(f"  Top resp  keywords   : {kw(all_en_r, 8)}")
    log.info(f"\n  {'ID':<12} {'Q':>5} {'IWC':>4} {'RWC':>4} {'ITTR':>6} {'RTTR':>6} {'FK-I':>6} {'FK-R':>6} {'OVL':>6}")
    log.info(f"  {'-'*65}")
    for p in en_rows:
        log.info(f"  {p['id']:<12} {p['qtype']:>5} {p['instr_wc']:>4} {p['resp_wc']:>4} "
                 f"{p['instr_ttr']:>6} {p['resp_ttr']:>6} {p['fk_instr']:>6} {p['fk_resp']:>6} {p['overlap']:>6}")
    log.info(f"\n  Medical term frequency:")
    freq = Counter(all_en_i + all_en_r)
    for t in MEDICAL_TERMS:
        log.info(f"    {t:<22} {freq.get(t,0):3d}  {'█'*freq.get(t,0)}")

    sec("BURMESE NLP")
    log.info(f"  Tokenizer : {'pyidaungsu (neural)' if HAVE_PIDS else 'rule-based'}")
    log.info(f"  Corpus word vocab   : {len(set(all_my_w))} unique / {len(all_my_w)} total  TTR={ttr(all_my_w)}")
    log.info(f"  Corpus syl vocab    : {len(set(all_my_s))} unique / {len(all_my_s)} total  TTR={ttr(all_my_s)}")
    log.info(f"  Avg syl/word        : {round(len(all_my_s)/max(len(all_my_w),1),2)}")
    log.info(f"  Corpus particle rate: {round(sum(1 for t in all_my_w if t in MY_PARTICLES)/max(len(all_my_w),1),4)}")
    log.info(f"  Char distribution   : {dict(all_char_dist.most_common())}")
    log.info(f"\n  Syllables/word distribution:")
    for n in sorted(sc_dist): log.info(f"    {n} syl : {sc_dist[n]:3d}  {'▒'*min(sc_dist[n],50)}")
    log.info(f"\n  Top particles:")
    for p, c in p_counts.most_common(15): log.info(f"    {p:<20} {c:3d}  {'█'*c}")
    log.info(f"\n  {'ID':<12} {'FLD':>5} {'WC':>4} {'SC':>4} {'MY%':>6} {'PR%':>6} {'TTR':>6} {'ENT':>6}")
    log.info(f"  {'-'*60}")
    for p in my_rows:
        for fld, fl in [("instr","INSTR"),("resp","RESP")]:
            log.info(f"  {p['id']:<12} {fl:>5} {p[fld+'_wc']:>4} {p[fld+'_sc']:>4} "
                     f"{p[fld+'_my_ratio']:>6} {p[fld+'_pr']:>6} {p[fld+'_ttr']:>6} {p[fld+'_ent']:>6}")

# ══════════════════════════════════════════════════════════════════════════════
# CHART UTILITIES
# ══════════════════════════════════════════════════════════════════════════════
def sax(ax, title, xlabel="", ylabel=""):
    ax.set_title(title, fontsize=10, fontweight="bold", color=FONT_COLOR, pad=7)
    ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
    ax.tick_params(colors=FONT_COLOR, labelsize=8)
    if xlabel: ax.set_xlabel(xlabel, fontsize=8, color=FONT_COLOR)
    if ylabel: ax.set_ylabel(ylabel, fontsize=8, color=FONT_COLOR)

def save(fig, name):
    path = name
    fig.savefig(path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    log.info(f"  [IMG] {path}")
    return path

def smart_x(ax, records_or_pr, max_ticks=30):
    """
    For large datasets: show only every N-th tick label and rotate.
    """
    n = len(records_or_pr)
    step = max(1, n // max_ticks)
    ids = [p["id"].replace("TB-NTP-","#") for p in records_or_pr]
    ax.set_xticks(range(n))
    ax.set_xticklabels(
        [ids[i] if i % step == 0 else "" for i in range(n)],
        rotation=45, ha="right", fontsize=7
    )

# ══════════════════════════════════════════════════════════════════════════════
# CHART 1: Dataset Overview
# ══════════════════════════════════════════════════════════════════════════════
def chart1(records, en_rows, my_rows):
    cats = Counter(r.get("category","") for r in records)
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.5))
    fig.suptitle("Myanmar TB NTP — Dataset Overview", fontsize=13, fontweight="bold", color=FONT_COLOR)

    # Pie
    ax = axes[0]
    ax.pie(cats.values(), labels=[c[:28] for c in cats.keys()],
           autopct="%1.0f%%", colors=PALETTE[:len(cats)], startangle=90,
           textprops={"fontsize":7,"color":FONT_COLOR},
           wedgeprops={"linewidth":1.5,"edgecolor":"white"})
    sax(ax, "Category Distribution")

    # EN avg word count per category
    ax = axes[1]
    cat_en = {}
    for p, r in zip(en_rows, records):
        c = r.get("category","")
        cat_en.setdefault(c, {"i":[],"r":[]})
        cat_en[c]["i"].append(p["instr_wc"]); cat_en[c]["r"].append(p["resp_wc"])
    clabels = [c[:20] for c in cat_en]
    i_means = [sum(v["i"])/len(v["i"]) for v in cat_en.values()]
    r_means = [sum(v["r"])/len(v["r"]) for v in cat_en.values()]
    x = np.arange(len(clabels)); w = 0.35
    ax.bar(x-w/2, i_means, w, label="Instruction", color=PALETTE[0], alpha=0.85, edgecolor="white")
    ax.bar(x+w/2, r_means, w, label="Response",    color=PALETTE[1], alpha=0.85, edgecolor="white")
    ax.set_xticks(x); ax.set_xticklabels(clabels, rotation=20, ha="right", fontsize=7)
    ax.legend(fontsize=8); sax(ax, "Avg EN Word Count by Category", ylabel="Words")

    # 4-field summary box plot
    ax = axes[2]
    data = [
        [p["instr_wc"] for p in en_rows],
        [p["resp_wc"]  for p in en_rows],
        [p["instr_wc"] for p in my_rows],
        [p["resp_wc"]  for p in my_rows],
    ]
    bp = ax.boxplot(data, patch_artist=True, widths=0.5,
                    medianprops={"color":"white","linewidth":2})
    for patch, color in zip(bp["boxes"], PALETTE[:4]):
        patch.set_facecolor(color); patch.set_alpha(0.8)
    ax.set_xticklabels(["EN Instr","EN Resp","MY Instr","MY Resp"], fontsize=8)
    sax(ax, "Word Count Distribution (All Records)", ylabel="Words")

    fig.tight_layout()
    return save(fig, "chart1_overview.png")

# ══════════════════════════════════════════════════════════════════════════════
# CHART 2: EN Length trend (handles large datasets)
# ══════════════════════════════════════════════════════════════════════════════
def chart2(en_rows):
    n = len(en_rows)
    use_trend = n > 20     # switch to line/trend for large datasets
    ids  = list(range(n))

    fig, axes = plt.subplots(1, 2, figsize=(14, 4.5))
    fig.suptitle("English NLP — Length & Readability", fontsize=13, fontweight="bold", color=FONT_COLOR)

    ax = axes[0]
    iw = [p["instr_wc"] for p in en_rows]
    rw = [p["resp_wc"]  for p in en_rows]
    if use_trend:
        ax.fill_between(ids, iw, alpha=0.3, color=PALETTE[0], label="Instruction")
        ax.fill_between(ids, rw, alpha=0.3, color=PALETTE[1], label="Response")
        ax.plot(ids, smooth(iw, 7), color=PALETTE[0], linewidth=1.8)
        ax.plot(ids, smooth(rw, 7), color=PALETTE[1], linewidth=1.8)
        ax.set_xlabel("Record index"); smart_x(ax, en_rows)
    else:
        x = np.arange(n); w = 0.35
        ax.bar(x-w/2, iw, w, label="Instruction", color=PALETTE[0], alpha=0.85, edgecolor="white")
        ax.bar(x+w/2, rw, w, label="Response",    color=PALETTE[1], alpha=0.85, edgecolor="white")
        ax.set_xticks(x); ax.set_xticklabels([p["id"].replace("TB-NTP-","#") for p in en_rows],
                                              rotation=45, ha="right", fontsize=7)
    ax.legend(fontsize=8); sax(ax, "EN Word Count: Instruction vs Response", ylabel="Words")

    ax = axes[1]
    fki = [p["fk_instr"] for p in en_rows]
    fkr = [p["fk_resp"]  for p in en_rows]
    if use_trend:
        ax.plot(ids, smooth(fki,7), color=PALETTE[2], linewidth=1.8, label="Instruction")
        ax.plot(ids, smooth(fkr,7), color=PALETTE[3], linewidth=1.8, label="Response")
        ax.fill_between(ids, smooth(fki,7), smooth(fkr,7), alpha=0.15, color=PALETTE[3])
        smart_x(ax, en_rows)
    else:
        x = np.arange(n); w = 0.35
        ax.bar(x-w/2, fki, w, label="Instruction", color=PALETTE[2], alpha=0.85, edgecolor="white")
        ax.bar(x+w/2, fkr, w, label="Response",    color=PALETTE[3], alpha=0.85, edgecolor="white")
        ax.set_xticks(x); ax.set_xticklabels([p["id"].replace("TB-NTP-","#") for p in en_rows],
                                              rotation=45, ha="right", fontsize=7)
    ax.axhline(60, color="gray", linestyle="--", linewidth=0.8, alpha=0.6)
    ax.text(n*0.02, 62, "FK=60 standard", fontsize=7, color="gray")
    ax.legend(fontsize=8); sax(ax, "Flesch-Kincaid Readability", ylabel="Score")

    fig.tight_layout()
    return save(fig, "chart2_en_lengths.png")

# ══════════════════════════════════════════════════════════════════════════════
# CHART 3: EN Vocabulary
# ══════════════════════════════════════════════════════════════════════════════
def chart3(all_en_i, all_en_r):
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    fig.suptitle("English NLP — Top Keywords", fontsize=13, fontweight="bold", color=FONT_COLOR)
    for ax, tokens, label, col in [
        (axes[0], all_en_i, "Instructions", PALETTE[0]),
        (axes[1], all_en_r, "Responses",    PALETTE[1]),
    ]:
        pairs = kw(tokens, 14)
        if not pairs: continue
        terms, freqs = zip(*pairs)
        bars = ax.barh(list(terms)[::-1], list(freqs)[::-1], color=col, alpha=0.85, edgecolor="white")
        for b in bars:
            ax.text(b.get_width()+0.05, b.get_y()+b.get_height()/2,
                    str(int(b.get_width())), va="center", fontsize=7, color=FONT_COLOR)
        sax(ax, f"Top Keywords — {label}", xlabel="Frequency")
    fig.tight_layout()
    return save(fig, "chart3_en_vocab.png")

# ══════════════════════════════════════════════════════════════════════════════
# CHART 4: EN Misc (Q-types, TTR, Overlap)
# ══════════════════════════════════════════════════════════════════════════════
def chart4(en_rows):
    fig, axes = plt.subplots(1, 3, figsize=(14, 4.5))
    fig.suptitle("English NLP — Question Types, TTR & Overlap", fontsize=13, fontweight="bold", color=FONT_COLOR)

    # Q-type
    qt = Counter(p["qtype"] for p in en_rows)
    axes[0].pie(qt.values(), labels=qt.keys(), autopct="%1.0f%%",
                colors=PALETTE[:len(qt)], startangle=90,
                textprops={"fontsize":8,"color":FONT_COLOR},
                wedgeprops={"linewidth":1.5,"edgecolor":"white"})
    sax(axes[0], "Question Type Distribution")

    # TTR histogram (handles large datasets well)
    ax = axes[1]
    ax.hist([p["instr_ttr"] for p in en_rows], bins=10, alpha=0.7, color=PALETTE[0], label="Instruction", edgecolor="white")
    ax.hist([p["resp_ttr"]  for p in en_rows], bins=10, alpha=0.7, color=PALETTE[1], label="Response",    edgecolor="white")
    ax.legend(fontsize=8); sax(ax, "TTR Distribution", xlabel="TTR", ylabel="Count")

    # Overlap histogram
    ax = axes[2]
    ax.hist([p["overlap"] for p in en_rows], bins=10, color=PALETTE[2], alpha=0.85, edgecolor="white")
    ax.axvline(sum(p["overlap"] for p in en_rows)/len(en_rows), color="red",
               linestyle="--", linewidth=1.5, label=f"mean={round(sum(p['overlap'] for p in en_rows)/len(en_rows),2)}")
    ax.legend(fontsize=8); sax(ax, "Instr–Response Token Overlap", xlabel="Overlap Ratio", ylabel="Count")

    fig.tight_layout()
    return save(fig, "chart4_en_misc.png")

# ══════════════════════════════════════════════════════════════════════════════
# CHART 5: Burmese Lengths & Particle Rate
# ══════════════════════════════════════════════════════════════════════════════
def chart5(my_rows):
    n = len(my_rows); use_trend = n > 20; ids = list(range(n))
    fig, axes = plt.subplots(1, 2, figsize=(14, 4.5))
    fig.suptitle("Burmese NLP — Word Counts & Particle Rate", fontsize=13, fontweight="bold", color=FONT_COLOR)

    ax = axes[0]
    iw = [p["instr_wc"] for p in my_rows]
    rw = [p["resp_wc"]  for p in my_rows]
    if use_trend:
        ax.fill_between(ids, iw, alpha=0.3, color=PALETTE[4], label="Instruction")
        ax.fill_between(ids, rw, alpha=0.3, color=PALETTE[5], label="Response")
        ax.plot(ids, smooth(iw,7), color=PALETTE[4], linewidth=1.8)
        ax.plot(ids, smooth(rw,7), color=PALETTE[5], linewidth=1.8)
        smart_x(ax, my_rows)
    else:
        x = np.arange(n); w = 0.35
        ax.bar(x-w/2, iw, w, label="Instruction", color=PALETTE[4], alpha=0.85, edgecolor="white")
        ax.bar(x+w/2, rw, w, label="Response",    color=PALETTE[5], alpha=0.85, edgecolor="white")
        ax.set_xticks(x); ax.set_xticklabels([p["id"].replace("TB-NTP-","#") for p in my_rows],
                                              rotation=45, ha="right", fontsize=7)
    ax.legend(fontsize=8); sax(ax, "Burmese Word Count per Record", ylabel="Words")

    ax = axes[1]
    ip = [p["instr_pr"] for p in my_rows]
    rp = [p["resp_pr"]  for p in my_rows]
    corpus_avg = sum(ip+rp) / len(ip+rp)
    if use_trend:
        ax.plot(ids, smooth(ip,7), color=PALETTE[6], linewidth=1.8, label="Instruction")
        ax.plot(ids, smooth(rp,7), color=PALETTE[7], linewidth=1.8, label="Response")
        smart_x(ax, my_rows)
    else:
        x = np.arange(n); w = 0.35
        ax.bar(x-w/2, ip, w, label="Instruction", color=PALETTE[6], alpha=0.85, edgecolor="white")
        ax.bar(x+w/2, rp, w, label="Response",    color=PALETTE[7], alpha=0.85, edgecolor="white")
        ax.set_xticks(x); ax.set_xticklabels([p["id"].replace("TB-NTP-","#") for p in my_rows],
                                              rotation=45, ha="right", fontsize=7)
    ax.axhline(corpus_avg, color="red", linestyle="--", linewidth=1.2,
               label=f"corpus avg={corpus_avg:.2f}")
    ax.legend(fontsize=8); sax(ax, "Burmese Particle Rate", ylabel="Rate")

    fig.tight_layout()
    return save(fig, "chart5_my_lengths.png")

# ══════════════════════════════════════════════════════════════════════════════
# CHART 6: Burmese Char Distribution (NO Myanmar text on axes)
# ══════════════════════════════════════════════════════════════════════════════
def chart6(all_char_dist):
    cls_order = ["CONSONANT","VOWEL","DIACRITIC","SPACE","PUNCT","MY_DIGIT","MY_OTHER","OTHER"]
    vals = [all_char_dist.get(c, 0) for c in cls_order]
    fig, axes = plt.subplots(1, 2, figsize=(13, 4.5))
    fig.suptitle("Burmese NLP — Character Class Analysis", fontsize=13, fontweight="bold", color=FONT_COLOR)

    ax = axes[0]
    bars = ax.bar(cls_order, vals, color=PALETTE, alpha=0.9, edgecolor="white")
    for b in bars:
        if b.get_height() > 0:
            ax.text(b.get_x()+b.get_width()/2, b.get_height()+1,
                    str(int(b.get_height())), ha="center", va="bottom", fontsize=7, color=FONT_COLOR)
    ax.set_xticklabels(cls_order, rotation=30, ha="right")
    sax(ax, "Char Class Frequency", ylabel="Count")

    ax = axes[1]
    nz = [(c, v) for c, v in zip(cls_order, vals) if v > 0]
    labels, sizes = zip(*nz)
    pcts = [s/sum(sizes)*100 for s in sizes]
    bars2 = ax.barh(labels, pcts, color=PALETTE[:len(labels)], alpha=0.9, edgecolor="white")
    for b, pct in zip(bars2, pcts):
        ax.text(b.get_width()+0.3, b.get_y()+b.get_height()/2,
                f"{pct:.1f}%", va="center", fontsize=8, color=FONT_COLOR)
    sax(ax, "Char Class Proportion (%)", xlabel="Percentage")

    fig.tight_layout()
    return save(fig, "chart6_my_chars.png")

# ══════════════════════════════════════════════════════════════════════════════
# CHART 7: Syllables + Particles (with Myanmar font)
# ══════════════════════════════════════════════════════════════════════════════
def chart7(sc_dist, p_counts):
    fig, ax = plt.subplots(figsize=(8, 5))
    fig.suptitle("Burmese NLP — Syllable Structure", fontsize=13, fontweight="bold", color=FONT_COLOR)
    ns   = sorted(sc_dist.keys())
    vals = [sc_dist[n] for n in ns]
    bars = ax.bar([str(n) for n in ns], vals, color=PALETTE[0], alpha=0.85, edgecolor="white")
    for b in bars:
        h = b.get_height()
        ax.text(b.get_x() + b.get_width()/2, h + max(vals)*0.005,
                f"{int(h):,}", ha="center", va="bottom", fontsize=8, color=FONT_COLOR)
    sax(ax, "Syllables-per-Word Distribution", xlabel="Syllables per Word", ylabel="Word Count")
    fig.tight_layout(pad=2.0)
    return save(fig, "chart7_my_syllables.png")

# ══════════════════════════════════════════════════════════════════════════════
# CHART 8: Bilingual Dashboard
# ══════════════════════════════════════════════════════════════════════════════
def chart8(records, en_rows, my_rows):
    """
    Clean bilingual summary dashboard — aggregated views, no per-record noise.
    6 panels:
      [0,0] EN vs MY avg word count grouped bar (by category)
      [0,1] Readability distribution (FK score histogram)
      [0,2] TTR boxplot EN instr / EN resp / MY instr / MY resp
      [1,0] Particle rate by category (MY)
      [1,1] Instruction-Response overlap distribution (EN)
      [1,2] MY/EN word ratio boxplot (instr vs resp)
    """
    fig = plt.figure(figsize=(16, 8))
    fig.suptitle("Myanmar TB NTP — Bilingual Summary Dashboard",
                 fontsize=14, fontweight="bold", color=FONT_COLOR, y=1.01)
    gs = gridspec.GridSpec(2, 3, figure=fig, hspace=0.52, wspace=0.38)

    cats     = sorted(set(r.get("category","") for r in records))
    cat_abbr = {c: c[:18] for c in cats}

    # ── [0,0] Avg word count by category — EN vs MY
    ax = fig.add_subplot(gs[0, 0])
    cat_en_i, cat_en_r, cat_my_i, cat_my_r = {}, {}, {}, {}
    for p, q, r in zip(en_rows, my_rows, records):
        c = r.get("category","")
        cat_en_i.setdefault(c, []).append(p["instr_wc"])
        cat_en_r.setdefault(c, []).append(p["resp_wc"])
        cat_my_i.setdefault(c, []).append(q["instr_wc"])
        cat_my_r.setdefault(c, []).append(q["resp_wc"])

    xlabels = [cat_abbr[c] for c in cats]
    x = np.arange(len(cats)); w = 0.2
    def cmean(d): return [sum(d.get(c,[0]))/max(len(d.get(c,[1])),1) for c in cats]
    ax.bar(x - 1.5*w, cmean(cat_en_i), w, label="EN Instr", color=PALETTE[0], alpha=0.85, edgecolor="white")
    ax.bar(x - 0.5*w, cmean(cat_en_r), w, label="EN Resp",  color=PALETTE[1], alpha=0.85, edgecolor="white")
    ax.bar(x + 0.5*w, cmean(cat_my_i), w, label="MY Instr", color=PALETTE[4], alpha=0.85, edgecolor="white")
    ax.bar(x + 1.5*w, cmean(cat_my_r), w, label="MY Resp",  color=PALETTE[5], alpha=0.85, edgecolor="white")
    ax.set_xticks(x)
    ax.set_xticklabels(xlabels, rotation=22, ha="right", fontsize=7)
    ax.legend(fontsize=7, ncol=2)
    sax(ax, "Avg Word Count by Category", ylabel="Words")

    # ── [0,1] FK readability histogram
    ax = fig.add_subplot(gs[0, 1])
    fki = [p["fk_instr"] for p in en_rows]
    fkr = [p["fk_resp"]  for p in en_rows]
    all_fk = fki + fkr
    bins = np.linspace(min(all_fk)-5, max(all_fk)+5, 18)
    ax.hist(fki, bins=bins, alpha=0.7, color=PALETTE[0], label="Instruction", edgecolor="white")
    ax.hist(fkr, bins=bins, alpha=0.7, color=PALETTE[2], label="Response",    edgecolor="white")
    ax.axvline(60, color="gray", linestyle="--", linewidth=1.2, label="FK=60")
    ax.axvline(np.mean(fki), color=PALETTE[0], linestyle=":", linewidth=1.5)
    ax.axvline(np.mean(fkr), color=PALETTE[2], linestyle=":", linewidth=1.5)
    ax.legend(fontsize=8)
    sax(ax, "Flesch-Kincaid Readability (EN)", xlabel="FK Score", ylabel="Count")

    # ── [0,2] TTR boxplot across 4 fields
    ax = fig.add_subplot(gs[0, 2])
    ttr_data = [
        [p["instr_ttr"] for p in en_rows],
        [p["resp_ttr"]  for p in en_rows],
        [p["instr_ttr"] for p in my_rows],
        [p["resp_ttr"]  for p in my_rows],
    ]
    bp = ax.boxplot(ttr_data, patch_artist=True, widths=0.5,
                    medianprops={"color":"white","linewidth":2.5},
                    flierprops={"marker":"o","markersize":4,"alpha":0.5})
    for patch, col in zip(bp["boxes"], [PALETTE[0], PALETTE[1], PALETTE[4], PALETTE[5]]):
        patch.set_facecolor(col); patch.set_alpha(0.8)
    ax.set_xticklabels(["EN\nInstr","EN\nResp","MY\nInstr","MY\nResp"], fontsize=8)
    ax.set_ylabel("TTR", fontsize=8)
    sax(ax, "Type-Token Ratio Distribution")

    # ── [1,0] Particle rate by category (MY)
    ax = fig.add_subplot(gs[1, 0])
    cat_ip, cat_rp = {}, {}
    for p, r in zip(my_rows, records):
        c = r.get("category","")
        cat_ip.setdefault(c, []).append(p["instr_pr"])
        cat_rp.setdefault(c, []).append(p["resp_pr"])
    x2 = np.arange(len(cats)); w2 = 0.35
    ax.bar(x2 - w2/2, [sum(cat_ip.get(c,[0]))/max(len(cat_ip.get(c,[1])),1) for c in cats],
           w2, label="Instruction", color=PALETTE[6], alpha=0.85, edgecolor="white")
    ax.bar(x2 + w2/2, [sum(cat_rp.get(c,[0]))/max(len(cat_rp.get(c,[1])),1) for c in cats],
           w2, label="Response",    color=PALETTE[7], alpha=0.85, edgecolor="white")
    global_pr = sum(p["instr_pr"]+p["resp_pr"] for p in my_rows)/(2*len(my_rows))
    ax.axhline(global_pr, color="red", linestyle="--", linewidth=1.2,
               label=f"corpus avg {global_pr:.2f}")
    ax.set_xticks(x2)
    ax.set_xticklabels(xlabels, rotation=22, ha="right", fontsize=7)
    ax.legend(fontsize=7)
    sax(ax, "Avg Particle Rate by Category (MY)", ylabel="Rate")

    # ── [1,1] EN instruction-response overlap histogram
    ax = fig.add_subplot(gs[1, 1])
    ovls = [p["overlap"] for p in en_rows]
    ax.hist(ovls, bins=14, color=PALETTE[3], alpha=0.85, edgecolor="white")
    ax.axvline(np.mean(ovls), color="red", linestyle="--", linewidth=1.5,
               label=f"mean={np.mean(ovls):.2f}")
    ax.axvline(np.median(ovls), color="orange", linestyle=":", linewidth=1.5,
               label=f"median={np.median(ovls):.2f}")
    ax.legend(fontsize=8)
    sax(ax, "EN Instr–Resp Token Overlap", xlabel="Overlap Ratio", ylabel="Count")

    # ── [1,2] MY÷EN word ratio boxplot (instr vs resp)
    ax = fig.add_subplot(gs[1, 2])
    ratio_i = [my_rows[i]["instr_wc"] / max(en_rows[i]["instr_wc"], 1) for i in range(len(records))]
    ratio_r = [my_rows[i]["resp_wc"]  / max(en_rows[i]["resp_wc"],  1) for i in range(len(records))]
    bp2 = ax.boxplot([ratio_i, ratio_r], patch_artist=True, widths=0.4,
                     medianprops={"color":"white","linewidth":2.5},
                     flierprops={"marker":"o","markersize":4,"alpha":0.5})
    bp2["boxes"][0].set_facecolor(PALETTE[4]); bp2["boxes"][0].set_alpha(0.8)
    bp2["boxes"][1].set_facecolor(PALETTE[5]); bp2["boxes"][1].set_alpha(0.8)
    ax.axhline(1.0, color="gray", linestyle="--", linewidth=1.2, label="ratio = 1")
    ax.set_xticklabels(["Instruction","Response"], fontsize=9)
    ax.legend(fontsize=8)
    sax(ax, "MY÷EN Word Count Ratio", ylabel="Ratio")

    fig.tight_layout(pad=2.0)
    return save(fig, "chart8_bilingual_dashboard.png")

# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════
def main():
    path = sys.argv[1] if len(sys.argv) > 1 else None
    log.info("╔══════════════════════════════════════════════════════════════════╗")
    log.info("║  Myanmar TB NTP — Bilingual NLP Analyzer v2 (EN + Burmese)     ║")
    log.info(f"║  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  Myanmar font: {HAS_MY_FONT}                    ║")
    log.info("╚══════════════════════════════════════════════════════════════════╝")

    records = load_dataset(path)
    en_rows, my_rows, all_en_i, all_en_r, all_my_w, all_my_s, \
        all_char_dist, sc_dist, p_counts = compute_all(records)

    log_all(records, en_rows, my_rows, all_en_i, all_en_r,
            all_my_w, all_my_s, all_char_dist, sc_dist, p_counts)

    sec("GENERATING CHARTS")
    imgs = []
    imgs.append(chart1(records, en_rows, my_rows))
    imgs.append(chart2(en_rows))
    imgs.append(chart3(all_en_i, all_en_r))
    imgs.append(chart4(en_rows))
    imgs.append(chart5(my_rows))
    imgs.append(chart6(all_char_dist))
    imgs.append(chart7(sc_dist, p_counts))
    imgs.append(chart8(records, en_rows, my_rows))

    sec("DONE")
    log.info(f"  Records : {len(records)}  |  Font: Myanmar={'✓' if HAS_MY_FONT else '✗ (fallback)'}")
    log.info(f"  Log     : {LOG_PATH}")
    log.info(f"  Charts  : {len(imgs)} images generated")
    for img in imgs: log.info(f"    {img}")

if __name__ == "__main__":
    main()