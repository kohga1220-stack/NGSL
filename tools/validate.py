"""
Logi 辞書バリデータ
新音韻ルール:
  - 母音: a, e, i, o, u
  - 子音: p, t, k, m, n, s, l, w, j (rは廃止)
  - 音節構造: (C)V のみ。子音連続(CCV)・音節末子音(CVC)は禁止。
  - 語末は母音必須。
  - 形態: 品詞語尾 名詞-a 動詞-o 形容詞-e 副詞-i 前置詞-de
"""

import csv
import re
from collections import defaultdict
from pathlib import Path

VOWELS = set("aeiou")
CONSONANTS_NEW = set("ptkmnslwj")          # 新ルール 9音
CONSONANTS_OLD = set("ptkmnslrwj")         # 旧ルール 10音
ALLOWED_NEW = VOWELS | CONSONANTS_NEW
ALLOWED_OLD = VOWELS | CONSONANTS_OLD

POS_SUFFIX = {
    "noun": "a",
    "verb": "o",
    "adj": "e",
    "adv": "i",
    "prep": "te",   # 旧 -de は d が新ルール子音外のため -te に変更
}

def strip_disambig(word: str) -> str:
    """同音識別の末尾数字を取り除く (例 kosa2 -> kosa)"""
    return re.sub(r"\d+$", "", word)

def syllabify(word: str):
    """単純CV音節分解。違反は例外として返す"""
    syllables = []
    i = 0
    n = len(word)
    while i < n:
        c = word[i]
        if c in VOWELS:
            syllables.append(c)          # 単独母音音節 V
            i += 1
        elif c in CONSONANTS_OLD:
            if i + 1 < n and word[i+1] in VOWELS:
                syllables.append(word[i:i+2])  # CV
                i += 2
            else:
                # 子音連続 or 語末子音
                return syllables, ("cluster_or_coda", i, word[i:i+2] if i+1 < n else c)
        else:
            return syllables, ("invalid_char", i, c)
    return syllables, None

def check_word(word: str, pos: str):
    """単語1つの違反を列挙して返す"""
    violations = []
    base = strip_disambig(word)

    # 使用不可文字
    for ch in base:
        if ch not in ALLOWED_OLD:
            violations.append(f"invalid_char:{ch}")
    if violations:
        return violations  # まず明らかな違反だけ返す

    # 子音 r の使用 (新ルールで廃止)
    if "r" in base:
        violations.append("uses_r")

    # 音節分解で子音連続・末子音を検出
    syls, err = syllabify(base)
    if err:
        kind, pos_idx, segment = err
        violations.append(f"{kind}@{pos_idx}:{segment}")

    # 語末が母音か (品詞語尾を考慮)
    suffix = POS_SUFFIX.get(pos, "")
    if suffix:
        if not base.endswith(suffix):
            violations.append(f"missing_suffix:expected_{suffix}")
    else:
        if base and base[-1] not in VOWELS:
            violations.append("non_vowel_ending")

    # 語幹長 (語尾を除いた母音数)
    stem = base[:-len(suffix)] if suffix and base.endswith(suffix) else base
    stem_syls, _ = syllabify(stem) if stem else ([], None)
    syl_count = len([s for s in stem_syls if any(c in VOWELS for c in s)])
    if syl_count > 3:
        violations.append(f"stem_too_long:{syl_count}_syllables")

    return violations

def main():
    raw = Path(__file__).resolve().parent.parent / "dictionary" / "raw.csv"
    rows = list(csv.DictReader(raw.open()))

    issues = defaultdict(list)        # violation_type -> [(word, pos, meaning)]
    homophones = defaultdict(list)    # base_word -> [(word, pos, meaning)]
    pos_count = defaultdict(int)

    for row in rows:
        w, pos, meaning = row["word"], row["pos"], row["meaning_ja"]
        pos_count[pos] += 1
        base = strip_disambig(w)
        homophones[base].append((w, pos, meaning))
        for v in check_word(w, pos):
            issues[v].append((w, pos, meaning))

    print("=" * 60)
    print(f"辞書総数: {len(rows)}語")
    print("品詞別:", dict(pos_count))
    print("=" * 60)

    # 違反タイプ別集計
    print("\n[違反タイプ別件数]")
    type_summary = defaultdict(int)
    for k, v in issues.items():
        # 個別座標を集約
        key = k.split("@")[0].split(":")[0]
        type_summary[key] += len(v)
    for k in sorted(type_summary, key=lambda x: -type_summary[x]):
        print(f"  {k}: {type_summary[k]}件")

    # 同音異義語
    collisions = {k: v for k, v in homophones.items() if len(v) > 1}
    print(f"\n[同音異義語] {len(collisions)}グループ, 該当語 {sum(len(v) for v in collisions.values())}語")
    for base, entries in sorted(collisions.items(), key=lambda x: -len(x[1])):
        meanings = " / ".join(f"{m}({p})" for _, p, m in entries)
        print(f"  {base} x{len(entries)}: {meanings}")

    # rを使う語
    r_words = [(w, p, m) for w, p, m in [(r["word"], r["pos"], r["meaning_ja"]) for r in rows] if "r" in strip_disambig(w)]
    print(f"\n[r使用語] {len(r_words)}語")
    print("  例:", ", ".join(w for w, _, _ in r_words[:15]), "..." if len(r_words) > 15 else "")

    # 子音連続/末子音
    cluster = issues.get("cluster_or_coda", [])
    # @つきキーも回収
    cluster_all = []
    for k, v in issues.items():
        if k.startswith("cluster_or_coda"):
            cluster_all.extend(v)
    print(f"\n[子音連続または音節末子音] {len(cluster_all)}語")
    print("  例:", ", ".join(w for w, _, _ in cluster_all[:20]), "..." if len(cluster_all) > 20 else "")

    # 品詞語尾違反
    suffix_viol = []
    for k, v in issues.items():
        if k.startswith("missing_suffix"):
            suffix_viol.extend([(w, p, m, k) for w, p, m in v])
    print(f"\n[品詞語尾違反] {len(suffix_viol)}語")
    for w, p, m, k in suffix_viol[:20]:
        print(f"  {w} (品詞={p}, 意味={m}) -> {k}")
    if len(suffix_viol) > 20:
        print(f"  ... 他 {len(suffix_viol) - 20}語")

    # 語幹長違反
    stem_viol = []
    for k, v in issues.items():
        if k.startswith("stem_too_long"):
            stem_viol.extend(v)
    print(f"\n[語幹長違反 (>3音節)] {len(stem_viol)}語")
    for w, p, m in stem_viol[:10]:
        print(f"  {w} ({p}, {m})")

    # 完全適合語
    valid_words = []
    for row in rows:
        if not check_word(row["word"], row["pos"]):
            valid_words.append(row["word"])
    print(f"\n[新ルールに完全適合] {len(valid_words)}語 ({len(valid_words)/len(rows)*100:.1f}%)")

    print("\n" + "=" * 60)
    print("要約: 既存辞書のうち")
    print(f"  全 {len(rows)} 語中、新ルール完全適合は {len(valid_words)} 語 ({len(valid_words)/len(rows)*100:.1f}%)")
    print(f"  リファクタ対象は {len(rows) - len(valid_words)} 語 ({(len(rows)-len(valid_words))/len(rows)*100:.1f}%)")
    print("=" * 60)

if __name__ == "__main__":
    main()
