# NGSL - Next-Generation Statistical Language

NGSL是一个带有**Rust风格的所有权系统**和**RStudio风格统计处理**的现代统计编程语言，使用**高速NumPy/SciPy/BLAS/LAPACK后端**。

## 🎯 项目概览

```
NGSL编译链:
源代码 → Lexer → Parser → Semantic Analyzer → Interpreter → NumPy/SciPy 执行
```

### 核心特性

#### 1️⃣ **类型系统和所有权**
- ✅ **静态类型检查** - 编译时确保类型安全
- ✅ **移动语义** - 防止use-after-move错误  
- ✅ **借用检查** - 类似Rust的&T和&mut T引用系统
- ✅ **生命周期管理** - 通过drop()进行显式资源释放
- ✅ **块作用域** - { } 块内自动清理变量

#### 2️⃣ **统计处理功能**
- ✅ **基本统计** - mean(), var(), sd(), median(), min(), max(), sum()
- ✅ **向量操作** - c(), seq(), range(), rep()
- ✅ **概率分布** - dnorm(), pnorm(), qnorm(), rnorm(), runif(), rbinom()
- ✅ **矩阵操作** - matrix(), data.frame(), t(), nrow(), ncol(), dim()
- ✅ **矩阵统计** - colMeans(), colSums(), rowMeans(), rowSums()
- ✅ **相关性** - cor(), cov()
- ✅ **线性回归** - lm(), summary(), predict()
- ✅ **矩阵代数** - det(), inv(), solve()

#### 3️⃣ **高速数值计算**
- ✅ **NumPy向量/矩阵** - 底层使用NumPy数组
- ✅ **BLAS矩阵乘法** - 优化的矩阵运算
- ✅ **LAPACK线性代数** - 高效的determinant、inverse、solve
- ✅ **SciPy统计函数** - 概率分布和统计分析
- ✅ **5.4x性能提升** - 相比纯Python (见基准)

## 📊 性能基准

```
向量操作 (10,000元素)
  添加、平均、方差计算: 0.12ms ✅

矩阵操作 (10×10)
  矩阵乘法和行列式: 0.28ms ✅

线性系统求解 (3×3, LAPACK)
  使用solve()求解Ax=b: 0.04ms ✅

统计分析 (1,000个样本)
  随机数生成、统计: 0.83ms ✅

性能对比
  纯Python (100,000元素求和): 0.3622ms
  NumPy/NGSL (100,000元素求和): 0.0670ms
  → 5.4倍加速 ✅
```

## 🏗️ 项目结构

```
/ngsl/
├── ngsl/
│   ├── __init__.py              # 公共API导出
│   ├── lexer.py                 # 词法分析器 (Lexer)
│   ├── parser.py                # 语法分析器 (Parser) 
│   ├── ast.py                   # 抽象语法树定义
│   ├── errors.py                # 异常类型
│   ├── semantics.py             # 语义分析和类型检查
│   └── interpreter.py           # NumPy/SciPy后端解释器 (NEW)
├── tests/
│   ├── test_lexer.py            # 词法分析器测试 (3个)
│   ├── test_parser.py           # 语法分析器测试 (4个)
│   ├── test_semantics.py        # 语义分析测试 (3个)
│   ├── test_semantics_inference.py  # 类型推理测试 (11个)
│   ├── test_statistics.py       # 统计功能测试 (35个)
│   └── test_interpreter.py      # 解释器测试 (22个) NEW
├── demo.py                      # 基本功能演示
├── demo_statistics.py           # 统计处理演示
├── benchmark_blas.py            # BLAS/LAPACK性能基准 NEW
└── README.md
```

**测试状态**: ✅ **78个测试全部通过**
- Lexer: 3个
- Parser: 4个  
- Semantics: 3个
- Type Inference: 11个
- Statistics: 35个
- Interpreter (新): 22个

## 🚀 快速开始

### 安装依赖

```bash
pip install numpy scipy pytest
```

### 基本使用

```bash
# 运行所有测试
python3 -m pytest

# 运行基础演示
python3 demo.py

# 运行统计处理演示
python3 demo_statistics.py

# 运行性能基准
python3 benchmark_blas.py
```

### 编程示例

```python
from ngsl import Parser, SemanticAnalyzer, NGSLInterpreter

# 编写NGSL程序
source = '''
let x = c(1, 2, 3, 4, 5);
let m = mean(x);
let v = var(x);
'''

# 词法分析 + 语法分析
program = Parser(source).parse()

# 语义分析 (类型检查)
analyzer = SemanticAnalyzer()
analyzer.analyze(program)

# 解释执行 (使用NumPy)
interpreter = NGSLInterpreter()
interpreter.interpret(program)

# 获取结果
mean_val = interpreter.env['m'].data  # 3.0
var_val = interpreter.env['v'].data   # 2.0

print(f"Mean: {mean_val}, Variance: {var_val}")
```

### NGSL语言示例

#### 向量操作
```ngsl
// 向量创建和操作
let x = c(1, 2, 3, 4, 5);
let y = seq(1, 10, 0.5);
let z = x + c(10, 20, 30, 40, 50);
let m = mean(x);
let s = sd(x);
```

#### 矩阵操作
```ngsl
// 矩阵创建和线性代数
let A = matrix(c(1, 2, 3, 4), 2, 2);
let B = matrix(c(5, 6, 7, 8), 2, 2);
let C = A * B;           // BLAS矩阵乘法
let d = det(A);          // LAPACK行列式
let Ainv = inv(A);       // LAPACK矩阵求逆
```

#### 统计分析
```ngsl
// 概率分布
let data = rnorm(1000, 0, 1);   // 从正态分布生成1000个数据
let d = dnorm(0, 0, 1);          // 密度
let p = pnorm(1.96, 0, 1);       // CDF
let q = qnorm(0.975, 0, 1);      // 分位数

// 相关性
let x = c(1, 2, 3, 4, 5);
let y = c(2, 4, 6, 8, 10);
let r = cor(x, y);  // 相关系数 = 1.0 (完全正相关)
```

#### 线性网索
```ngsl
// 求解线性系统
let A = matrix(c(1.0, 2.0, 3.0, 4.0), 2, 2);
let b = c(1.0, 2.0);
let x = solve(A, b);  // 解Ax=b

// 矩阵链式运算
let Xt = t(A);        // 转置
let AtA = Xt * A;     // A'A
let det_AtA = det(AtA);
```

#### 所有权和借用
```ngsl
// 移动语义
let a = "hello";
let b = a;          // a被移动到b
// let c = a;        // ❌ 编译错误: a已被移动

// 借用
let x = 5;
let rx = &x;        // 不可变借用
let ry = &x;        // 可以有多个不可变借用
// let mx = &mut x;  // ❌ 编译错误: x已被借用

// 显式drop
let y = &x;
drop(y);            // 显式释放借用
let mz = &mut x;    // 现在可以可变借用

// 块作用域
let ptr = &x;
{
    let local = 10;  // 局部变量
}                    // local在这里被释放
                     // ptr仍然有效
```

## 🏴 技术栈

| 组件 | 技术 |
|------|------|
| **词法分析** | Python (自实现) |
| **语法分析** | Python递归下降解析器 |
| **语义分析** | 类型推理 + 所有权检查 |
| **执行引擎** | NumPy/SciPy解释器 |
| **线性代数** | NumPy BLAS封装 |
| **矩阵运算** | NumPy LAPACK封装 |
| **统计函数** | SciPy统计模块 |
| **测试** | pytest (78个测试) |

## 📈 未来计划

- [ ] **IR生成** - 生成LLVM IR用于编译
- [ ] **JIT编译** - 使用Numba进行即时编译
- [ ] **GPU支持** - CuPy / GPU张量操作
- [ ] **并行处理** - OpenMP多线程支持
- [ ] **绘图** - Matplotlib集成
- [ ] **数据输入/输出** - CSV、HDF5支持
- [ ] **高级统计模型** - GLM、混合模型等

## 📝 实现概览

### 编译阶段

1. **词法分析** (`lexer.py`)
   - 分词：keywords, identifiers, numbers, strings, operators
   - 支持公式字面量：`f"y ~ x"`
   - 支持点缀名称：`data.frame`, `col.names`

2. **语法分析** (`parser.py`)
   - 递归下降解析器
   - 支持：let, return, expressions, blocks, method chains
   - 优先级处理二元运算符

3. **语义分析** (`semantics.py`)
   - **类型检查**：静态类型推理
   - **移动检查**：防止use-after-move of non-copy types
   - **借用检查**：类似Rust的&T/&mut T规则
   - **类型推理**：自动推导Vec、Result等泛型

### 执行阶段

4. **解释执行** (`interpreter.py`) - **NEW**
   - AST树解释器
   - NumPy数组作为Vector/Matrix
   - NumPy/SciPy函数绑定
   - 自动类型转换

## 🎓 学习资源

- **Rust所有权系统** - https://doc.rust-lang.org/book/
- **NumPy文档** - https://numpy.org/
- **SciPy文档** - https://scipy.org/
- **BLAS/LAPACK** - https://netlib.org/

## 📜 许可证

MIT License

---

**作者注**: 这个项目展示了如何将现代编程语言特性（Rust风格的所有权）与科学计算库（NumPy/SciPy）集成，为统计编程创建一个快速、安全和优雅的语言。所有编译时检查确保代码安全性，而运行时使用高度优化的数值库实现高性能。
