# Logi

**Logi** is a minimalist constructed language designed for logical clarity and cross-linguistic accessibility.

**Logi**（ロジ）は、論理的な明快さと言語的な公平性を目指して設計された人工言語です。

> "logical → logi" — log(1) = 0, the origin point.

---

## Design Principles / 設計原則

- **SVO-fixed word order** — Subject → Verb → Object, no exceptions
- **15-phoneme system** — 5 vowels + 9 consonants (no r/l confusion)
- **(C)V syllable structure** — every syllable ends in a vowel; no consonant clusters
- **Suffix-based part-of-speech** — noun `-a`, verb `-o`, adjective `-e`, adverb `-i`, preposition `-te`
- **No passive voice** — always active SVO
- **No plural suffix** — plurality expressed via `mene` (many)
- **602-word core dictionary** — machine-validated, zero homophone collisions

---

## Phonology / 音韻論

| | Sounds |
|---|---|
| Vowels（母音）| a, e, i, o, u |
| Consonants（子音）| p, t, k, m, n, s, l, w, j |

Syllable structure: **(C)V only**
No consonant clusters. No word-final consonants.

---

## Quick Grammar / 文法早見表

| Feature | Rule | Example |
|---|---|---|
| Word order | S-V-O | mi toko tu. |
| Past tense | pas + V | mi pas toko tu. |
| Future | fut + V | mi fut toko tu. |
| Negation | no + V | mi no toko tu. |
| Question | V … ka? | tu pio kute ka? |
| Progressive | kon + V | mi kon toko tu. |
| Perfective | pin + V | mi pin toko tu. |
| Gerund | V-stem + na | piona（being）, tikona（teaching）|
| Comparative | mor … tante | mi pio mor kute tante tu. |
| Superlative | mosi + adj | mi mosi laiko apa. |
| Relative clause | N + ta + clause | mana ta li rano（the person who runs）|

---

## Sample Text / 例文

**Japanese / 日本語**
こんにちは。私は20歳で、大学生です。好きな食べ物はリンゴです。私はあなたと友達になりたいと思います。あなたの名前はなんですか？好きな食べ物はなんですか？いろいろ私に教えてください。

**Logi**
mi toko tu. mi oto tu pulu ila e mi pio sutua. mi mosi laiko apa. mi wonuto piona pulena witute tu. tu nema pio wata ka? tu laiko wata puta ka? tituso mene sina tote mi.

**English gloss**
I greet you. I have 20 years and I am a student. I most like apple. I want the being-friend with you. Your name is what? You like what food? Teach many things to me.

---

## Numbers / 数詞

| 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 |
|---|---|---|---|---|---|---|---|---|---|
| ni | pa | tu | te | ka | li | so | se | wa | ja |

Units: `pulu`（×10）, `kupulu`（×100）, `mipulu`（×1000）

Examples: 20 = `tu pulu` / 25 = `tu pulu li` / 2025 = `tu mipulu ni kupulu tu pulu li`

---

## Pronouns / 代名詞

| | Singular | Plural (inclusive) | Plural (exclusive) |
|---|---|---|---|
| 1st | mi | mis | mip |
| 2nd | tu | tus | — |
| 3rd | li | lis | — |
| Reflexive | so | — | — |

---

## Repository Structure / リポジトリ構成

```
logi/
├── README.md
├── docs/
│   └── grammar.md          Full grammar specification / 文法仕様書（完全版）
├── dictionary/
│   ├── final.csv           602-word validated dictionary / 検証済み辞書602語
│   └── raw.csv             Original pre-validation entries / 変換前原典
└── tools/
    ├── validate.py         Phonology rule checker / 音韻ルール検証
    ├── regenerate.py       Auto-conversion to new phonology / 自動音韻変換
    └── resolve.py          Homophone collision resolver / 同音衝突解決
```

---

## Version History / 変更履歴

| Version | Changes |
|---|---|
| v0.1 | Initial release as SVO-Logi / NGSL |
| v0.2 | Removed `r`, fixed syllable structure to (C)V |
| v0.3 | Preposition suffix `-de` → `-te`; gerund `-ina` → `-na`; plural `-s` abolished; `ka?` question rule; 602-word dictionary, 100% rule-compliant |

---

## License

Creative Commons Attribution 4.0 International (CC BY 4.0)

---

*Designed and developed by [@kohga1220-stack](https://github.com/kohga1220-stack)*
