#!/usr/bin/env python3
"""
NGSL Demo - Next-Generation Statistical Language 実行例
"""

from ngsl import Lexer, Parser, SemanticAnalyzer

def demo_simple_arithmetic():
    print("=" * 60)
    print("デモ1: 簡単な算術演算")
    print("=" * 60)
    source = 'let x = 3 + 2.5; let y = x * 2;'
    print(f"ソースコード: {source}")
    
    program = Parser(source).parse()
    analyzer = SemanticAnalyzer()
    analyzer.analyze(program)
    print("✓ 解析成功")
    print()

def demo_ownership():
    print("=" * 60)
    print("デモ2: 所有権検証（移動）")
    print("=" * 60)
    source = 'let a: String = "hello"; let b = a; let c = a;'
    print(f"ソースコード: {source}")
    
    try:
        program = Parser(source).parse()
        analyzer = SemanticAnalyzer()
        analyzer.analyze(program)
    except Exception as e:
        print(f"✓ エラー検出: {e}")
    print()

def demo_borrowing():
    print("=" * 60)
    print("デモ3: 借用検証（不変参照の複数読み取り）")
    print("=" * 60)
    source = 'let x = 5; let y = &x; let z = &x;'
    print(f"ソースコード: {source}")
    
    program = Parser(source).parse()
    analyzer = SemanticAnalyzer()
    analyzer.analyze(program)
    print("✓ 解析成功（複数の不変参照を許可）")
    print()

def demo_mutable_borrow_conflict():
    print("=" * 60)
    print("デモ4: 借用検証（可変参照と不変参照の競合）")
    print("=" * 60)
    source = 'let x = 5; let y = &x; let z = &mut x;'
    print(f"ソースコード: {source}")
    
    try:
        program = Parser(source).parse()
        analyzer = SemanticAnalyzer()
        analyzer.analyze(program)
    except Exception as e:
        print(f"✓ エラー検出: {e}")
    print()

def demo_scope_release():
    print("=" * 60)
    print("デモ5: ブロックスコープ内での借用解放")
    print("=" * 60)
    source = 'let x = 5; { let y = &x; } let z = &mut x;'
    print(f"ソースコード: {source}")
    
    program = Parser(source).parse()
    analyzer = SemanticAnalyzer()
    analyzer.analyze(program)
    print("✓ 解析成功（ブロック終了で借用が解放）")
    print()

def demo_explicit_drop():
    print("=" * 60)
    print("デモ6: 明示的なdrop による借用解放")
    print("=" * 60)
    source = 'let x = "hello"; let y = &x; drop(y); let z = &mut x;'
    print(f"ソースコード: {source}")
    
    program = Parser(source).parse()
    analyzer = SemanticAnalyzer()
    analyzer.analyze(program)
    print("✓ 解析成功（drop で借用参照を解放）")
    print()

def demo_type_inference():
    print("=" * 60)
    print("デモ7: 型推論と型昇格")
    print("=" * 60)
    source = 'let x = 3 + 2.5;'
    print(f"ソースコード: {source}")
    print("型推論: Int + Float → Float （自動昇格）")
    
    program = Parser(source).parse()
    analyzer = SemanticAnalyzer()
    analyzer.analyze(program)
    print("✓ 解析成功")
    print()

if __name__ == "__main__":
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " NGSL (Next-Generation Statistical Language) デモ ".center(58) + "║")
    print("╚" + "=" * 58 + "╝")
    print()
    
    demo_simple_arithmetic()
    demo_ownership()
    demo_borrowing()
    demo_mutable_borrow_conflict()
    demo_scope_release()
    demo_explicit_drop()
    demo_type_inference()
    
    print("=" * 60)
    print("全デモが完了しました！")
    print("=" * 60)
