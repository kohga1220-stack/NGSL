"""
Logi 語彙再生成
方針:
  1. 違反語に対して決定論的ルールで新音韻に準拠する形へ変換
  2. 同音衝突は識別シフトで分化
  3. 人間レビュー用にoriginal/regenerated/notesを併記

変換ルール:
  r -> l
  h -> 削除
  b,f,v -> p
  d -> t
  g,c(hard) -> k
  z,sh,ch -> s
  子音連続 CC -> C[挿入母音]C (デフォルト 'u')
  末子音 -> 品詞語尾を補完
"""

import csv
import re
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from validate import (
    VOWELS, CONSONANTS_NEW, POS_SUFFIX,
    strip_disambig, check_word, syllabify,
)

# 不正子音 -> 新ルール子音 へのマッピング
CONSONANT_MAP = {
    "r": "l",
    "b": "p", "f": "p", "v": "p",
    "d": "t",
    "g": "k", "c": "k", "q": "k",
    "z": "s", "x": "s",
    "h": "",          # 削除
    "y": "j",
}

EPENTHESIS = "u"      # 子音連続を割る挿入母音

def normalize_chars(word: str) -> str:
    """不正文字を新ルール音素へ置換"""
    out = []
    for ch in word:
        if ch in VOWELS or ch in CONSONANTS_NEW:
            out.append(ch)
        elif ch in CONSONANT_MAP:
            out.append(CONSONANT_MAP[ch])
        else:
            out.append("")  # 未知文字は削除
    return "".join(out)

def break_clusters(word: str) -> str:
    """子音連続を母音挿入で解消、末子音は後段で語尾補完"""
    out = []
    n = len(word)
    for i, c in enumerate(word):
        out.append(c)
        if c in CONSONANTS_NEW and i + 1 < n and word[i+1] in CONSONANTS_NEW:
            out.append(EPENTHESIS)
    return "".join(out)

def fix_ending(stem: str, pos: str) -> str:
    """末尾を母音にし、品詞語尾を保証。重複子音のみ防止"""
    suffix = POS_SUFFIX.get(pos, "")
    if not suffix:
        if stem and stem[-1] not in VOWELS:
            return stem + EPENTHESIS
        return stem
    # 既存の末尾母音は保護する。末尾が子音で語尾と同じなら一つだけ削る
    base = stem
    # 旧語尾の母音を一度剥がして基底を取る (1音だけ)
    if base and base[-1] in VOWELS:
        base = base[:-1]
    # 末尾子音が語尾の最初の子音と同じなら、その子音だけ削る（重複防止）
    if base and base[-1] == suffix[0]:
        base = base[:-1]
    if not base:
        return EPENTHESIS + suffix
    return base + suffix

def regenerate(word: str, pos: str) -> str:
    """単語を新ルール準拠形に変換"""
    base = strip_disambig(word)
    base = normalize_chars(base)
    base = break_clusters(base)
    base = fix_ending(base, pos)
    # 連続母音を1つに圧縮（任意。ai, au, oa などは保持したいので簡易ルール）
    base = re.sub(r"([aeiou])\1+", r"\1", base)
    return base

def main():
    raw = Path(__file__).resolve().parent.parent / "dictionary" / "raw.csv"
    out_path = Path(__file__).resolve().parent.parent / "dictionary" / "master.csv"
    rows = list(csv.DictReader(raw.open()))

    # 全件を再生成
    regenerated = []
    for row in rows:
        w, pos, meaning = row["word"], row["pos"], row["meaning_ja"]
        new_word = regenerate(w, pos)
        viol_before = check_word(w, pos)
        viol_after = check_word(new_word, pos)
        regenerated.append({
            "original": w,
            "regenerated": new_word,
            "pos": pos,
            "meaning_ja": meaning,
            "violations_before": ";".join(viol_before) or "OK",
            "violations_after": ";".join(viol_after) or "OK",
        })

    # 同音衝突の検出と分化
    groups = defaultdict(list)
    for r in regenerated:
        groups[r["regenerated"]].append(r)

    # 衝突グループに対し、機能語(代名詞/接続詞/wh/marker)を優先固定し
    # 内容語(noun/verb/adj/adv/prep)を分化する
    FUNCTION_POS = {"pronoun", "conj", "wh", "marker"}
    vowel_shift = {"a": "e", "e": "i", "i": "o", "o": "u", "u": "a"}
    consonant_shift = {"p": "t", "t": "k", "k": "p", "m": "n", "n": "m",
                       "s": "l", "l": "s", "w": "j", "j": "w"}

    for word, members in list(groups.items()):
        if len(members) <= 1:
            continue
        members.sort(key=lambda m: (m["pos"] not in FUNCTION_POS, m["original"]))
        for idx, m in enumerate(members[1:], start=1):
            new = m["regenerated"]
            suffix = POS_SUFFIX.get(m["pos"], "")
            stem = new[:-len(suffix)] if suffix and new.endswith(suffix) else new
            # 最初の母音を idx 回シフト
            shifted_stem = ""
            shifted = False
            for ch in stem:
                if ch in VOWELS and not shifted:
                    target = ch
                    for _ in range(idx):
                        target = vowel_shift[target]
                    shifted_stem += target
                    shifted = True
                else:
                    shifted_stem += ch
            candidate = shifted_stem + suffix
            # まだ衝突するなら、別の母音を挿入して2音節化
            existing = {r["regenerated"] for r in regenerated if r is not m}
            if candidate in existing:
                # 子音シフトを試す
                shifted2 = ""
                done = False
                for ch in shifted_stem:
                    if ch in CONSONANTS_NEW and not done:
                        shifted2 += consonant_shift.get(ch, ch)
                        done = True
                    else:
                        shifted2 += ch
                candidate = shifted2 + suffix
            if candidate in existing:
                # 自動分化の限界。手動レビュー対象としてフラグ
                m["regenerated"] = candidate
                m["violations_after"] = ";".join(check_word(m["regenerated"], m["pos"])) or "OK"
                m["notes"] = f"REVIEW: 衝突残存 ({word}と同形)"
                continue
            m["regenerated"] = candidate
            m["violations_after"] = ";".join(check_word(m["regenerated"], m["pos"])) or "OK"
            m["notes"] = f"衝突分化 x{idx}"

    # 再衝突チェック
    final_groups = defaultdict(list)
    for r in regenerated:
        final_groups[r["regenerated"]].append(r)
    remaining_collisions = {k: v for k, v in final_groups.items() if len(v) > 1}

    # CSV出力
    with out_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "original", "regenerated", "pos", "meaning_ja",
            "violations_before", "violations_after", "notes",
        ])
        writer.writeheader()
        for r in regenerated:
            r.setdefault("notes", "")
            writer.writerow(r)

    # サマリ
    ok_after = sum(1 for r in regenerated if r["violations_after"] == "OK")
    changed = sum(1 for r in regenerated if r["original"] != r["regenerated"])
    print("=" * 60)
    print(f"再生成完了: {len(regenerated)}語")
    print(f"  変更あり: {changed}語")
    print(f"  変更なし: {len(regenerated) - changed}語")
    print(f"  新ルール適合: {ok_after}語 ({ok_after/len(regenerated)*100:.1f}%)")
    print(f"  残違反: {len(regenerated) - ok_after}語")
    print(f"  残同音衝突: {len(remaining_collisions)}グループ")
    print("=" * 60)

    # 変更サンプル
    print("\n[変更例 上位30件]")
    samples = [r for r in regenerated if r["original"] != r["regenerated"]][:30]
    for r in samples:
        print(f"  {r['original']:<10} -> {r['regenerated']:<10} ({r['pos']}, {r['meaning_ja']})")

    # 残違反
    remaining_viol = [r for r in regenerated if r["violations_after"] != "OK"]
    if remaining_viol:
        print(f"\n[残違反 全{len(remaining_viol)}件]")
        for r in remaining_viol[:15]:
            print(f"  {r['regenerated']:<10} ({r['pos']}, {r['meaning_ja']}) {r['violations_after']}")

    # 残衝突
    if remaining_collisions:
        print(f"\n[残同音衝突 {len(remaining_collisions)}グループ]")
        for word, members in list(remaining_collisions.items())[:10]:
            meanings = " / ".join(f"{m['meaning_ja']}({m['pos']})" for m in members)
            print(f"  {word}: {meanings}")

    print(f"\n結果は {out_path} に書き出し")

if __name__ == "__main__":
    main()
