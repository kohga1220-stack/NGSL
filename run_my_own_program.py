#!/usr/bin/env python3
"""
My Own NGSL Program - 実行環境
my_own_program.ngsl を編集して実行！
"""

from ngsl import Parser, SemanticAnalyzer, NGSLInterpreter
import sys

def print_header(text):
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}\n")

# プログラムを読み込む
try:
    with open('my_own_program.ngsl', 'r') as f:
        source = f.read()
except FileNotFoundError:
    print("❌ my_own_program.ngsl が見つかりません")
    sys.exit(1)

print_header("📝 実行するコード")
print(source)

print_header("⚙️ コンパイルと実行")

try:
    # コンパイル
    print("✓ 字句解析・構文解析中...")
    program = Parser(source).parse()
    
    print("✓ 型チェック中...")
    analyzer = SemanticAnalyzer()
    analyzer.analyze(program)
    
    # 実行
    print("✓ 実行中...\n")
    interpreter = NGSLInterpreter()
    interpreter.interpret(program)
    
    print_header("✅ 実行成功！")
    
    # 定義された変数を表示
    print("📊 計算結果:\n")
    
    for var_name, ngsl_value in sorted(interpreter.env.items()):
        # コメント行は表示しない
        if var_name.startswith('_'):
            continue
        
        value = ngsl_value.data
        value_type = ngsl_value.type_name
        
        # 値の整えた表示
        if isinstance(value, (list, tuple)):
            value_str = f"[{', '.join(str(v) for v in value[:5])}{'...' if len(value) > 5 else ''}]"
        elif isinstance(value, float):
            value_str = f"{value:.6f}" if abs(value) < 1e6 else f"{value:.2e}"
        else:
            value_str = str(value)
        
        print(f"  {var_name:15} ({value_type:10}): {value_str}")
    
    print_header("💡 次のステップ")
    print("""
✓ my_own_program.ngsl を編集して、自分のコードを書く
✓ python3 run_my_own_program.py を実行して結果を確認
✓ 各種関数を試す: c(), mean(), var(), cor(), matrix(), etc.

困ったときは README_FULL.md を参照してください！
    """)
    
except Exception as e:
    print_header("❌ エラーが発生しました")
    print(f"{type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
