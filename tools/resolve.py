"""
14衝突の手動解決を適用する。
判断基準:
  1. 食物・身体・自然・道具などの基本語を優先
  2. 元の語幹に近い形を保持
  3. 代替語は日本語・英語・仏語等から音訳
"""

import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from validate import check_word

# (original_word, current_regenerated) -> new_regenerated
# 判断ログをコメントで併記
RESOLUTIONS = {
    # 1. ato衝突: 傷つける保持(hurt音残る), 開ける→apeloに
    ("opo", "ato"): ("apelo", "openの音節展開"),

    # 2. eka衝突: 卵保持(食物), 帽子→kasa(日本「笠」)
    ("hata", "eka"): ("kasa", "日本『笠』由来"),

    # 3. lupa衝突: 石鹸保持(soap連想), ロープ→nawa(日本「縄」)
    ("ropa2", "lupa"): ("nawa", "日本『縄』由来"),

    # 4. pala衝突: 雲保持(自然), 部分→pata(part短形)
    ("para", "pala"): ("pata", "英part短形"),

    # 5. pelo衝突: 失敗する保持, 来る→komoに統合(既存)
    ("kuro2", "pelo"): ("komo", "既存komo(来る)に統合"),

    # 6. pulo衝突: 覆う保持, 約束する→pulomiso(promise音節)
    ("proo", "pulo"): ("pulomiso", "英promise音節展開"),

    # 7. sisa衝突: システム保持(元語一致), レストラン→sokuta(日本食卓風)
    ("resa", "sisa"): ("sokuta", "日本『食卓』風"),

    # 8. taka衝突: 税金保持, フォーク→puka(英pick由来、名詞-a)
    ("poka3", "taka"): ("poluka", "英fork音節展開(f→p,r→l,名詞-a)"),

    # 9. tesa衝突: テスト保持(元語一致), 平和→eiwa(日本「平和」)
    ("pasa2", "tesa"): ("eiwa", "日本『平和』由来"),

    # 10. teta衝突: 足保持(身体), 劇場→kekisa(日本「劇」)
    ("teta", "teta"): ("kekisa", "日本『劇』+sa(場)"),

    # 11. tisa衝突: チーズ保持(元語一致), ズボン→pasuna(pants音訳)
    ("pasa3", "tisa"): ("pasuna", "英pants音訳"),

    # 12. tola衝突: ドア保持, 恐怖→kowa(日本「こわい」)
    ("pira", "tola"): ("kowa", "日本『怖い』由来"),

    # 13. tosa衝突: 魚保持(食物), ポケット→pokita(pocket音訳)
    ("pasa4", "tosa"): ("pokita", "英pocket音訳"),

    # 14. tula衝突: 道具保持, ビール→pia(beer短音), 森→molia(日本「森」)
    ("pira2", "tula"): ("pia", "英beer短音(rなし)"),
    ("pora2", "tula"): ("molia", "日本『森』由来"),

    # 追加修正: pata(部分)とpato変換後のpata(鳥)衝突 → 部分をpatalaに
    ("para", "pala"): ("patala", "英part延長(pa-ta-la)"),
}

def main():
    master_path = Path(__file__).resolve().parent.parent / "dictionary" / "master.csv"
    rows = list(csv.DictReader(master_path.open()))

    applied = []
    for r in rows:
        key = (r["original"], r["regenerated"])
        if key in RESOLUTIONS:
            new_form, reason = RESOLUTIONS[key]
            old_form = r["regenerated"]
            r["regenerated"] = new_form
            r["violations_after"] = ";".join(check_word(new_form, r["pos"])) or "OK"
            r["notes"] = f"手動解決: {reason}"
            applied.append((r["original"], old_form, new_form, r["meaning_ja"], reason))

    # 検証
    from collections import defaultdict
    groups = defaultdict(list)
    for r in rows:
        groups[r["regenerated"]].append(r)
    remaining = {k: v for k, v in groups.items() if len(v) > 1}

    # 新ルール違反チェック
    new_violations = [r for r in rows if r["violations_after"] != "OK"]

    # 出力
    final_path = Path(__file__).resolve().parent.parent / "dictionary" / "final.csv"
    with final_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    print("=" * 60)
    print(f"手動解決適用: {len(applied)}件")
    print("=" * 60)
    for orig, old, new, meaning, reason in applied:
        print(f"  {orig:<8} ({meaning}): {old:<10} -> {new:<10} | {reason}")

    print("\n" + "=" * 60)
    print(f"残同音衝突: {len(remaining)}グループ")
    for k, v in remaining.items():
        print(f"  {k}: " + " / ".join(f"{m['meaning_ja']}({m['pos']})" for m in v))

    print(f"\n残新ルール違反: {len(new_violations)}件")
    for r in new_violations:
        print(f"  {r['regenerated']} ({r['pos']}, {r['meaning_ja']}): {r['violations_after']}")

    ok_count = sum(1 for r in rows if r["violations_after"] == "OK")
    print(f"\n最終適合: {ok_count}/{len(rows)} ({ok_count/len(rows)*100:.1f}%)")
    print(f"最終ユニーク語数: {len(groups)} (元603から重複消去後)")
    print(f"\n結果: {final_path}")

if __name__ == "__main__":
    main()
