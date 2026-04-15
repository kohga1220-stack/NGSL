#!/usr/bin/env python3
"""
Lesson 3: 行列と線形代数 - インタラクティブ実行
"""

from ngsl import Parser, SemanticAnalyzer, NGSLInterpreter
import numpy as np

def print_section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

with open('lesson_matrices.ngsl', 'r') as f:
    source = f.read()

print_section("📝 実行するコード")
print(source)

print_section("⚙️ コンパイルと実行")

try:
    program = Parser(source).parse()
    analyzer = SemanticAnalyzer()
    analyzer.analyze(program)
    interpreter = NGSLInterpreter()
    interpreter.interpret(program)
    
    print("✅ 実行成功！\n")
    
    print_section("📊 結果分析")
    
    # 結果取得
    A = interpreter.env['A'].data
    B = interpreter.env['B'].data
    C = interpreter.env['C'].data
    At = interpreter.env['At'].data
    det_A = interpreter.env['det_A'].data
    A_inv = interpreter.env['A_inv'].data
    x = interpreter.env['x'].data
    n_rows = interpreter.env['n_rows'].data
    n_cols = interpreter.env['n_cols'].data
    d = interpreter.env['d'].data
    
    print("🔹 入力行列")
    print(f"  A =\n{A}\n")
    print(f"  B =\n{B}\n")
    
    print("🔹 行列乗法 (BLAS)")
    print(f"  C = A * B =\n{C}\n")
    
    print("🔹 転置")
    print(f"  A^T =\n{At}\n")
    
    print("🔹 行列式 (LAPACK)")
    print(f"  det(A) = {det_A}\n")
    
    print("🔹 逆行列 (LAPACK)")
    print(f"  A^(-1) =\n{A_inv}\n")
    
    print("🔹 線形方程式 (LAPACK)")
    print(f"  Ax = b を解く")
    print(f"  x = {x}\n")
    
    # 検証
    b_computed = np.dot(A, x)
    print(f"  検証: A * x = {b_computed}")
    print(f"  期待値: b = [3, 7]\n")
    
    print("🔹 次元情報")
    print(f"  nrow(A) = {n_rows}")
    print(f"  ncol(A) = {n_cols}")
    print(f"  dim(A) = {d}\n")
    
    print_section("💡 学習ポイント")
    print("""
✓ matrix(data, nrow, ncol) - 行列を作成
✓ A * B - 行列乗法（BLAS使用で高速）
✓ t(A) - 転置
✓ det(A) - 行列式（LAPACK）
✓ inv(A) - 逆行列（LAPACK）
✓ solve(A, b) - 線形方程式を解く（LAPACK）

BLAS/LAPACK は高度に最適化された線形代数ライブラリです。
NumPy を通じてこれらを利用できます！
    """)
    
except Exception as e:
    print(f"❌ エラーが発生しました: {type(e).__name__}: {e}")
