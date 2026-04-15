#!/usr/bin/env python3
"""
NGSL コード実行ガイド
全てのチュートリアルと実行方法
"""

import subprocess
import sys

LESSONS = [
    {
        "num": 1,
        "title": "基礎：ベクトル・統計から始める",
        "file": "my_first_ngsl.ngsl",
        "runner": "run_my_first_ngsl.py",
        "description": "ベクトル作成、四則演算、基本統計関数（mean, var, sd等）",
        "difficulty": "⭐ 初級"
    },
    {
        "num": 2,
        "title": "確率分布を試す",
        "file": "lesson_distributions.ngsl",
        "runner": "run_lesson_distributions.py",
        "description": "正規分布、乱数生成、確率関数（dnorm, pnorm, qnorm）、相関分析",
        "difficulty": "⭐⭐ 初中級"
    },
    {
        "num": 3,
        "title": "行列と線形代数",
        "file": "lesson_matrices.ngsl",
        "runner": "run_lesson_matrices.py",
        "description": "行列操作、BLAS行列乗法、LAPACK（det, inv, solve）",
        "difficulty": "⭐⭐⭐ 中級"
    },
    {
        "num": 4,
        "title": "自分でコードを書く",
        "file": "my_own_program.ngsl",
        "runner": "run_my_own_program.py",
        "description": "自由にNGSLコードを書いて実行。テンプレートを参考に",
        "difficulty": "💪 自由"
    }
]

def print_banner():
    print("""
╔══════════════════════════════════════════════════════════╗
║        NGSL - Statistical Programming Language          ║
║          実行可能なチュートリアルガイド                 ║
╚══════════════════════════════════════════════════════════╝
    """)

def print_lessons():
    print("\n📚 利用可能なレッスン\n")
    
    for lesson in LESSONS:
        print(f"  {lesson['num']}️⃣  {lesson['title']}")
        print(f"      {lesson['difficulty']}")
        print(f"      📄 {lesson['file']}")
        print(f"      🎯 {lesson['description']}\n")

def print_usage():
    print("🚀 実行方法:\n")
    print("  # レッスン1を実行")
    print("  python3 run_my_first_ngsl.py\n")
    
    print("  # レッスン2を実行")
    print("  python3 run_lesson_distributions.py\n")
    
    print("  # レッスン3を実行")
    print("  python3 run_lesson_matrices.py\n")
    
    print("  # 自分のプログラムを実行")
    print("  python3 run_my_own_program.py\n")

def print_quick_reference():
    print("\n📖 関数リファレンス\n")
    
    categories = {
        "ベクトル作成": [
            "c(1, 2, 3, ...) - 値を結合してベクトルを作成",
            "seq(start, end, by) - 等差数列を生成",
            "range(start, end) - 整数列を生成",
            "rep(value, times) - 値を繰り返す"
        ],
        "基本統計": [
            "mean(x) - 平均値",
            "var(x) - 分散",
            "sd(x) - 標準偏差",
            "median(x) - 中央値",
            "min(x), max(x), sum(x) - 最小値、最大値、合計"
        ],
        "確率分布": [
            "rnorm(n, μ, σ) - 正規分布から乱数生成",
            "dnorm(x, μ, σ) - 確率密度関数",
            "pnorm(q, μ, σ) - 累積分布関数",
            "qnorm(p, μ, σ) - 分位点関数",
            "runif(n, min, max) - 均一分布から乱数生成"
        ],
        "行列操作": [
            "matrix(data, nrow, ncol) - 行列を作成",
            "t(M) - 転置",
            "nrow(M), ncol(M) - 行数、列数",
            "dim(M) - 次元"
        ],
        "行列代数 (BLAS/LAPACK)": [
            "A * B - 行列乗法（BLAS最適化）",
            "det(M) - 行列式（LAPACK）",
            "inv(M) - 逆行列（LAPACK）",
            "solve(A, b) - 線形方程式Ax=b を解く（LAPACK）"
        ],
        "相関・回帰": [
            "cor(x, y) - ピアソン相関係数",
            "cov(x, y) - 共分散",
            "lm(formula) - 線形回帰"
        ]
    }
    
    for category, functions in categories.items():
        print(f"  {category}")
        for func in functions:
            print(f"    • {func}")
        print()

def print_tips():
    print("\n💡 ヒント\n")
    print("""
  1️⃣  コメント: // でコメントを書く
       let x = c(1, 2, 3);  // これはコメント
  
  2️⃣  型推論: 型は自動推論される（型注釈不要）
       let x = c(1, 2, 3);  // xは Vector[Int] に推論
  
  3️⃣  ベクトル演算: 要素ごとの操作が自動
       let x = c(1, 2, 3);
       let y = c(4, 5, 6);
       let z = x + y;  // [5, 7, 9]
  
  4️⃣  スカラー倍数: ベクトル × スカラー操作をサポート
       let x = c(1, 2, 3);
       let y = x * 2;  // [2, 4, 6]
  
  5️⃣  パフォーマンス: NumPy/SciPy/BLAS/LAPACK バックエンド
       大規模な行列操作は自動的に最適化される
    """)

def print_examples():
    print("\n🎯 実践例\n")
    print("""
  統計分析:
    let data = rnorm(100, 0, 1);
    let m = mean(data);
    let s = sd(data);
    let d = dnorm(0, 0, 1);

  行列計算:
    let A = matrix(c(1, 2, 3, 4), 2, 2);
    let b = c(5, 6);
    let x = solve(A, b);

  相関分析:
    let x = seq(1, 100, 1);
    let y = x + rnorm(100, 0, 10);
    let r = cor(x, y);
    """)

if __name__ == "__main__":
    print_banner()
    print_lessons()
    print_usage()
    print_quick_reference()
    print_tips()
    print_examples()
    
    print("\n" + "="*60)
    print("  さあ、NGSLコードを書いてみましょう！")
    print("="*60 + "\n")
