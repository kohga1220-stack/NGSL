# Logi 文法仕様書（確定版）

## 1. 基本理念

- 名称: **Logi**（ロジ）
- 旧称: SVO-Logi / NGSL
- 理念: 「すべての人類にわかりやすい」論理的人工言語
- 語源: logical → logi。log(1)=0 で「原点」の意も持つ

---

## 2. 音韻論（確定）

### 母音（5音）
a, e, i, o, u

### 子音（9音）
p, t, k, m, n, s, l, w, j

※ r は廃止。l に統一（l/r 区別が困難な言語話者への配慮）。
※ h, b, d, f, g, v, z 等は使用不可。

### 音節構造
- 許可: **(C)V のみ**（子音0〜1 + 母音1）
- 禁止: 子音連続（CCV）・音節末子音（CVC）
- 例: pa, ta, lo, ki, su ✓ / pra, stua, -n ✗

### アクセント
語末から2番目の音節に固定（規則アクセント）。

---

## 3. 品詞と語尾（確定）

| 品詞 | 語尾 | 例 |
|---|---|---|
| 名詞 | -a | mana（人）, puta（食べ物）|
| 動詞 | -o | toko（話す）, laiko（好む）|
| 形容詞 | -e | kute（良い）, nue（新しい）|
| 副詞 | -i | mosi（最も）, naui（今）|
| 前置詞 | **-te** | tote（〜へ）, wite（〜と） ※旧-deから変更 |
| 動名詞 | **-na** | piona（であること）, tikona（教えること）※旧-inaから変更 |

---

## 4. 文法マーカー

動詞の直前に置く。複数を組み合わせ可能。

| マーカー | 意味 | 例 |
|---|---|---|
| pas | 過去 | mi pas toko tu. |
| fut | 未来 | mi fut toko tu. |
| kon | 進行（〜している）| mi kon toko tu. |
| pin | 完了（〜してしまった）| mi pin toko tu. |
| no | 否定 | mi no toko tu. |
| ka + **?** | 疑問（文末）| tu nema pio wata ka? |

### 組み合わせ例
- 過去進行: mi pas kon toko tu.
- 過去否定: mi pas no toko tu.
- 未来完了: mi fut pin toko tu.

### 疑問文のルール（新規確定）
- 文末に **ka ?** を置く。
- ka は疑問マーカー、? は書記上の疑問符。両方必須。
- 例: tu laiko wata puta ka? （あなたは何の食べ物が好きですか？）

---

## 5. 数・複数（確定）

### 複数形語尾の廃止
旧来の名詞 + s（例: manas）は廃止。
複数概念は **mene（多くの）** で表現する。

| 旧 | 新 |
|---|---|
| manas（人々）| mene mana |
| sinas（物事）| mene sina |

### 数詞（確定）
0〜9は1音節語。

| 数 | Logi |
|---|---|
| 0 | ni |
| 1 | pa |
| 2 | tu |
| 3 | te |
| 4 | ka |
| 5 | li |
| 6 | so |
| 7 | se |
| 8 | wa |
| 9 | ja |

10以上は位取り合成。位の単位語: pulu（〜十）、kupulu（〜百）、mipulu（〜千）

| 数 | Logi |
|---|---|
| 10 | pa pulu |
| 20 | tu pulu |
| 25 | tu pulu li |
| 100 | pa kupulu |
| 2025 | tu mipulu ni kupulu tu pulu li |

---

## 6. 代名詞（確定）

| 人称 | 単数 | 複数（包括） | 複数（排他）|
|---|---|---|---|
| 1人称 | mi | mis | mip |
| 2人称 | tu | tus | — |
| 3人称 | li | lis | — |
| 再帰 | so | — | — |

※ 包括（inclusive）: 聞き手を含む「私たち」
※ 排他（exclusive）: 聞き手を含まない「私たち」

---

## 7. 構文規則

### 基本語順: 厳格 SVO
[S] [副詞] [マーカー] [V] [形容詞+O] [前置詞句]

### 受動態: 禁止
常に能動態で表現。能動主体不明の場合は so（不特定）を主語に置く。

### SVOO / SVOC: 禁止
SVO + 前置詞句で代替。
- 「私はあなたに本をあげた」→ mi pas kipo puka tote tu.

### 関係節
マーカー **ta** を名詞の直後に置く。
- mi sio mana ta li rano.（私は走っている人を見る）

### 比較
- 比較級: mor + tante（〜より）
- 最上級: mosi + 形容詞
- 同等: seme + tote（〜と同じ）

### 使役
動詞 koso（させる）+ 動名詞（-na）
- mi koso li tote koina.（私は彼をここへ来させる）

### 仮定法
接続詞 ip（もし）+ 仮定マーカー wut
- ip mi wut pio pata, mi wut palaio.（もし鳥なら、飛ぶのに）

---

## 8. 語彙生成アルゴリズム

### 音訳ルール（英語ベース）
| 英語音 | Logi音 |
|---|---|
| b, f, v | → p |
| d, th | → t |
| g, c(hard) | → k |
| z, sh, ch | → s |
| r | → l |
| h | → 削除 |
| y | → j |

### 語源優先順位
1. 音象徴（意味と音が対応）
2. 英語・日本語・スペイン語・中国語からの多言語投票（今後拡張）
3. 衝突回避（編集距離1以内の語幹を禁止）

---

## 9. 確定例文

### 自己紹介文
**日本語**
こんにちは。私は20歳で、大学生です。好きな食べ物はリンゴです。私はあなたと友達になりたいと思います。あなたの名前はなんですか？好きな食べ物はなんですか？いろいろ私に教えてください。

**Logi**
mi toko tu. mi oto tu pulu ila e mi pio sutua. mi mosi laiko apa. mi wonuto piona pulena witute tu. tu nema pio wata ka? tu laiko wata puta ka? tituso mene sina tote mi.

### 語注
| Logi | 意味 | 変更点 |
|---|---|---|
| toko | 話す | 変更なし |
| oto | 持つ | hoto → h削除 |
| tu pulu ila | 20歳 | iras → ila（r→l）|
| sutua | 学生 | stua → sutua（子音連続解消）|
| mosi | 最も | mos → mosi（副詞語尾統一）|
| laiko | 好む | raiko → laiko（r→l）|
| piona | 〜になること | pioina → piona（動名詞語尾-na）|
| pulena | 友達 | prena → pulena（r→l, pr→pul）|
| witute | 〜と | witde → witute（-de→-te）|
| tote | 〜へ | tode → tote（-de→-te）|
| tituso | 教える | titso → tituso（子音連続解消）|

---

## 10. 変更履歴

| 版 | 変更内容 |
|---|---|
| v0.1 | SVO-Logi / NGSL 初版 |
| v0.2 | r廃止、子音9音へ、音節構造(C)V限定 |
| v0.3 | 前置詞語尾 -de → -te、動名詞語尾 -ina → -na |
| v0.3 | 複数語尾 -s 廃止、meneで代替 |
| v0.3 | 疑問文 ka + ? 規則確定 |
| v0.3 | osujo廃止（titusoniに統合）|
| v0.3 | 辞書602語、新ルール100%適合 |
