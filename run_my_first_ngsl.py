#!/usr/bin/env python3
"""
My First NGSL Program - インタラクティブ実行
"""

from ngsl import Parser, SemanticAnalyzer, NGSLInterpreter

def print_header(section):
    print(f"\n{'='*60}")
    print(f"  {section}")
    print(f"{'='*60}\n")

# NGSLコード（my_first_ngsl.ngsl）を実行
with open('my_first_ngsl.ngsl', 'r') as f:
    source = f.read()

print_header("📝 実行するコード")
print(source)

# コンパイル & 実行
print_header("⚙️ コンパイルと実行")

try:
    # 字句解析 + 構文解析
    print("✓ 字句解析・構文解析中...")
    program = Parser(source).parse()
    
    # 語義分析（型チェック）
    print("✓ 型チェック中...")
    analyzer = SemanticAnalyzer()
    analyzer.analyze(program)
    
    # 解釈実行
    print("✓ 実行中...")
    interpreter = NGSLInterpreter()
    interpreter.interpret(program)
    
    print("\n✅ 実行成功！\n")
    
    # 結果表示
    print_header("📊 結果")
    
    results = {
        'x': 'ベクトル x',
        'y': 'ベクトル y',
        'z': 'ベクトル z (x + y)',
        'mean_x': '平均値',
        'var_x': '分散',
        'sd_x': '標準偏差',
        'sum_x': '合計',
        'min_x': '最小値',
        'max_x': '最大値',
        'med_x': '中央値',
    }
    
    for var_name, description in results.items():
        if var_name in interpreter.env:
            value = interpreter.env[var_name]
            print(f"{var_name:12} ({description:20}): {value.data}")
    
    print_header("🎯 解説")
    print("""
1️⃣ ベクトル作成: c(1, 2, 3, 4, 5)
   → NumPy配列に変換: [1, 2, 3, 4, 5]

2️⃣ ベクトル演算: x + y
   → 要素ごとの加算（NumPy broadcasting）
   → [1+10, 2+20, 3+30, ...] = [11, 22, 33, ...]

3️⃣ 統計関数: mean(), var(), sd(), など
   → NumPyとSciPyを使用した高速計算
   → コンパイル時に型チェック済み

✨ これがNGSLの基本的な使い方です！
    """)
    
except Exception as e:
    print(f"❌ エラーが発生しました:")
    print(f"   {type(e).__name__}: {e}")
