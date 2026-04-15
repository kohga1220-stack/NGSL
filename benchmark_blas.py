#!/usr/bin/env python3
"""
NGSL with BLAS/LAPACK - Benchmark and Demo
Demonstrates high-speed numerical operations using NumPy/SciPy backend
"""

import time
import numpy as np
from ngsl import Parser, SemanticAnalyzer, NGSLInterpreter

def print_section(title):
    print(f"\n{'=' * 70}")
    print(f"  {title}")
    print(f"{'=' * 70}")

def benchmark_vector_operations():
    print_section("1. Vector Operations (NumPy Backend)")
    
    # Large vector creation and operations
    source = '''
    let x = seq(1, 10000, 1);
    let y = seq(2, 10001, 1);
    let z = x + y;
    let m = mean(z);
    let v = var(z);
    '''
    
    print(f"\n✓ Creating and operating on large vectors (n=10000)")
    print(f"  Operations: addition, mean, variance")
    
    program = Parser(source).parse()
    analyzer = SemanticAnalyzer()
    analyzer.analyze(program)
    
    start = time.time()
    interpreter = NGSLInterpreter()
    interpreter.interpret(program)
    elapsed = time.time() - start
    
    z = interpreter.env['z']
    m = interpreter.env['m']
    v = interpreter.env['v']
    
    print(f"  ✅ Completed in {elapsed*1000:.2f}ms")
    print(f"  Result: mean(z) = {m.data:.2f}, var(z) = {v.data:.2f}")
    print(f"  Vector size: {len(z.data)}")

def benchmark_matrix_operations():
    print_section("2. Matrix Operations (BLAS Backend)")
    
    # Matrix creation and operations
    source = '''
    let m1 = matrix(seq(1, 100, 1), 10, 10);
    let m2 = matrix(seq(101, 200, 1), 10, 10);
    let m3 = m1 * m2;
    let d = det(m1);
    '''
    
    print(f"\n✓ Matrix multiplication and determinant (10x10)")
    
    program = Parser(source).parse()
    analyzer = SemanticAnalyzer()
    analyzer.analyze(program)
    
    start = time.time()
    interpreter = NGSLInterpreter()
    interpreter.interpret(program)
    elapsed = time.time() - start
    
    m3 = interpreter.env['m3']
    d = interpreter.env['d']
    
    print(f"  ✅ Completed in {elapsed*1000:.2f}ms")
    print(f"  Matrix multiplication result shape: {m3.data.shape}")
    print(f"  Determinant: {d.data:.2f}")

def benchmark_linear_system():
    print_section("3. Linear System Solving (LAPACK Backend)")
    
    # Solve Ax = b using LAPACK
    source = '''
    let A = matrix(c(1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0), 3, 3);
    let b = c(1.0, 2.0, 3.0);
    let x = solve(A, b);
    '''
    
    print(f"\n✓ Solving linear system Ax=b (3x3)")
    
    program = Parser(source).parse()
    analyzer = SemanticAnalyzer()
    analyzer.analyze(program)
    
    start = time.time()
    interpreter = NGSLInterpreter()
    interpreter.interpret(program)
    elapsed = time.time() - start
    
    x = interpreter.env['x']
    
    print(f"  ✅ Completed in {elapsed*1000:.2f}ms")
    print(f"  Solution: x = {x.data}")
    print(f"  Solution size: {len(x.data)}")

def benchmark_statistical_analysis():
    print_section("4. Statistical Analysis")
    
    source = '''
    let data = rnorm(1000, 0, 1);
    let m = mean(data);
    let s = sd(data);
    let med = median(data);
    '''
    
    print(f"\n✓ Statistical analysis on random normal data (n=1000)")
    
    program = Parser(source).parse()
    analyzer = SemanticAnalyzer()
    analyzer.analyze(program)
    
    start = time.time()
    interpreter = NGSLInterpreter()
    interpreter.interpret(program)
    elapsed = time.time() - start
    
    m = interpreter.env['m']
    s = interpreter.env['s']
    med = interpreter.env['med']
    
    print(f"  ✅ Completed in {elapsed*1000:.2f}ms")
    print(f"  Sample mean: {m.data:.4f} (expected ~0)")
    print(f"  Sample std dev: {s.data:.4f} (expected ~1)")
    print(f"  Sample median: {med.data:.4f}")

def demo_correlation_analysis():
    print_section("5. Correlation Analysis")
    
    source = '''
    let x = rnorm(1000, 0, 1);
    let y = rnorm(1000, 0, 1);
    let r = cor(x, y);
    '''
    
    print(f"\n✓ Computing correlation between two random vectors (n=1000)")
    
    program = Parser(source).parse()
    analyzer = SemanticAnalyzer()
    analyzer.analyze(program)
    
    start = time.time()
    interpreter = NGSLInterpreter()
    interpreter.interpret(program)
    elapsed = time.time() - start
    
    r = interpreter.env['r']
    
    print(f"  ✅ Completed in {elapsed*1000:.2f}ms")
    print(f"  Correlation coefficient: {r.data:.4f} (expected ~0 for independent)")

def demo_matrix_inverse():
    print_section("6. Matrix Inversion (LAPACK)")
    
    source = '''
    let A = matrix(c(1.0, 2.0, 3.0, 5.0), 2, 2);
    let Ainv = inv(A);
    '''
    
    print(f"\n✓ Computing matrix inverse (2x2)")
    
    program = Parser(source).parse()
    analyzer = SemanticAnalyzer()
    analyzer.analyze(program)
    
    start = time.time()
    interpreter = NGSLInterpreter()
    interpreter.interpret(program)
    elapsed = time.time() - start
    
    Ainv = interpreter.env['Ainv']
    
    print(f"  ✅ Completed in {elapsed*1000:.2f}ms")
    print(f"  Inverse matrix:")
    print(f"    {Ainv.data}")

def comparison_python_vs_numpy():
    print_section("7. Performance Comparison: Python vs NumPy")
    
    N = 100000
    
    # Pure Python
    print(f"\n✓ Computing sum of {N:,} elements:")
    
    python_data = list(range(N))
    start = time.time()
    python_sum = sum(python_data)
    python_time = time.time() - start
    print(f"  Pure Python: {python_time*1000:.4f}ms")
    
    # NumPy (via NGSL)
    source = f'''
    let x = seq(1, {N}, 1);
    let total = sum(x);
    '''
    
    program = Parser(source).parse()
    analyzer = SemanticAnalyzer()
    analyzer.analyze(program)
    
    start = time.time()
    interpreter = NGSLInterpreter()
    interpreter.interpret(program)
    numpy_time = time.time() - start
    print(f"  NumPy (NGSL): {numpy_time*1000:.4f}ms")
    print(f"  Speedup: {python_time/numpy_time:.1f}x")

def demo_matrix_algebra_chain():
    print_section("8. Complex Matrix Algebra Chain")
    
    source = '''
    let X = matrix(seq(1, 25, 1), 5, 5);
    let Xt = t(X);
    let XtX = Xt * X;
    let det_XtX = det(XtX);
    '''
    
    print(f"\n✓ Computing X'X and its determinant (5x5 matrix)")
    print(f"  Operations: transpose, matrix multiply, determinant")
    
    program = Parser(source).parse()
    analyzer = SemanticAnalyzer()
    analyzer.analyze(program)
    
    start = time.time()
    interpreter = NGSLInterpreter()
    interpreter.interpret(program)
    elapsed = time.time() - start
    
    det_XtX = interpreter.env['det_XtX']
    
    print(f"  ✅ Completed in {elapsed*1000:.2f}ms")
    print(f"  det(X'X) = {det_XtX.data:.2f}")

if __name__ == "__main__":
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " NGSL with BLAS/LAPACK: High-Speed Numerical Operations ".center(68) + "║")
    print("╚" + "=" * 68 + "╝")
    
    benchmark_vector_operations()
    benchmark_matrix_operations()
    benchmark_linear_system()
    benchmark_statistical_analysis()
    demo_correlation_analysis()
    demo_matrix_inverse()
    comparison_python_vs_numpy()
    demo_matrix_algebra_chain()
    
    print_section("✨ All Benchmarks Complete")
    print("""
Key Features Demonstrated:
✅ Vector operations with NumPy (element-wise)
✅ Matrix operations with NumPy (broadcasting, multiplication)
✅ Matrix algebra with BLAS (multiplication, transpose)
✅ LAPACK operations (determinant, inverse, linear solve)
✅ Statistical functions with SciPy
✅ Significant speedups compared to pure Python

Technology Stack:
- NumPy for vector/matrix operations
- SciPy for statistical functions
- BLAS for matrix operations
- LAPACK for linear algebra

All operations are type-checked at compile time and executed
with the full power of NumPy/SciPy backends at runtime!
    """)
