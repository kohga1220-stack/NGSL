#!/usr/bin/env python3
"""
Lesson 2: 確率分布 - インタラクティブ実行
"""

from ngsl import Parser, SemanticAnalyzer, NGSLInterpreter
import numpy as np

def print_section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

with open('lesson_distributions.ngsl', 'r') as f:
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
    samples = interpreter.env['samples'].data
    sample_mean = interpreter.env['sample_mean'].data
    sample_sd = interpreter.env['sample_sd'].data
    density_at_0 = interpreter.env['density_at_0'].data
    prob_less_than_1 = interpreter.env['prob_less_than_1'].data
    quantile_95 = interpreter.env['quantile_95'].data
    correlation = interpreter.env['correlation'].data
    
    # 統計量の表示
    print("🎲 正規分布サンプル（N=100, μ=0, σ=1）")
    print(f"  サンプル平均: {sample_mean:.4f}  (期待値: 0)")
    print(f"  サンプル標準偏差: {sample_sd:.4f}  (期待値: 1)")
    
    print("\n📈 確率分布関数")
    print(f"  dnorm(0): {density_at_0:.4f}  (標準正規分布の最頻値)")
    print(f"  pnorm(1): {prob_less_than_1:.4f}  (P(X ≤ 1) ≈ 0.8413)")
    print(f"  qnorm(0.95): {quantile_95:.4f}  (95パーセンタイル ≈ 1.645)")
    
    print("\n🔗 相関分析")
    print(f"  cor(x, y): {correlation:.4f}  (y = 2x + 誤差なので高い正相関)")
    
    print_section("💡 学習ポイント")
    print("""
✓ rnorm(n, μ, σ) - 正規分布から乱数生成
✓ dnorm(x, μ, σ) - 確率密度関数（Probability Density Function）
✓ pnorm(q, μ, σ) - 累積分布関数（Cumulative Distribution Function）
✓ qnorm(p, μ, σ) - 分位点関数（Quantile Function）
✓ cor(x, y) - ピアソン相関係数

これらは統計分析の基本的なツールです！
    """)
    
except Exception as e:
    print(f"❌ エラーが発生しました: {type(e).__name__}: {e}")
