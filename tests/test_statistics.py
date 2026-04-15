"""
Tests for statistical processing features in NGSL
"""

import pytest
from ngsl import Parser, SemanticAnalyzer, SemanticError, NGSLInterpreter


class TestDescriptiveStatistics:
    """Test basic statistical functions"""
    
    def test_mean_on_vector(self):
        """mean(x: Vector) -> Float"""
        source = 'let x = c(1, 2, 3); let avg = mean(x);'
        program = Parser(source).parse()
        analyzer = SemanticAnalyzer()
        analyzer.analyze(program)
        assert analyzer.env['avg'].name == 'Float'
    
    def test_variance_on_vector(self):
        """var(x: Vector) -> Float"""
        source = 'let x = c(1, 2, 3); let v = var(x);'
        program = Parser(source).parse()
        analyzer = SemanticAnalyzer()
        analyzer.analyze(program)
        assert analyzer.env['v'].name == 'Float'
    
    def test_std_dev_on_vector(self):
        """sd(x: Vector) -> Float"""
        source = 'let x = c(1, 2, 3); let s = sd(x);'
        program = Parser(source).parse()
        analyzer = SemanticAnalyzer()
        analyzer.analyze(program)
        assert analyzer.env['s'].name == 'Float'
    
    def test_vector_construction(self):
        """c(1, 2, 3) -> Vector[Int]"""
        source = 'let nums = c(1, 2, 3);'
        program = Parser(source).parse()
        analyzer = SemanticAnalyzer()
        analyzer.analyze(program)
        assert analyzer.env['nums'].name == 'Vector'
        assert analyzer.env['nums'].generics[0].name == 'Int'
    
    def test_vector_construction_floats(self):
        """c(1.0, 2.0, 3.0) -> Vector[Float]"""
        source = 'let floats = c(1.0, 2.0, 3.0);'
        program = Parser(source).parse()
        analyzer = SemanticAnalyzer()
        analyzer.analyze(program)
        assert analyzer.env['floats'].name == 'Vector'
        assert analyzer.env['floats'].generics[0].name == 'Float'
    
    def test_median_returns_element_type(self):
        """median(x: Vector[T]) -> T"""
        source = 'let x = c(1.0, 2.0, 3.0); let m = median(x);'
        program = Parser(source).parse()
        analyzer = SemanticAnalyzer()
        analyzer.analyze(program)
        assert analyzer.env['m'].name == 'Float'
    
    def test_min_max_on_vector(self):
        """min(x: Vector[T]) -> T, max(x: Vector[T]) -> T"""
        source = 'let x = c(1, 2, 3); let mn = min(x); let mx = max(x);'
        program = Parser(source).parse()
        analyzer = SemanticAnalyzer()
        analyzer.analyze(program)
        assert analyzer.env['mn'].name == 'Int'
        assert analyzer.env['mx'].name == 'Int'
    
    def test_sum_on_vector(self):
        """sum(x: Vector[T]) -> T"""
        source = 'let x = c(1, 2, 3); let total = sum(x);'
        program = Parser(source).parse()
        analyzer = SemanticAnalyzer()
        analyzer.analyze(program)
        assert analyzer.env['total'].name == 'Int'


class TestVectorGeneration:
    """Test vector generation functions"""
    
    def test_seq_function(self):
        """seq(from, to, by) -> Vector[Float]"""
        source = 'let x = seq(1, 10, 0.5);'
        program = Parser(source).parse()
        analyzer = SemanticAnalyzer()
        analyzer.analyze(program)
        assert analyzer.env['x'].name == 'Vector'
        assert analyzer.env['x'].generics[0].name == 'Float'
    
    def test_range_function(self):
        """range(min, max) -> Vector[Int]"""
        source = 'let x = range(1, 10);'
        program = Parser(source).parse()
        analyzer = SemanticAnalyzer()
        analyzer.analyze(program)
        assert analyzer.env['x'].name == 'Vector'
        assert analyzer.env['x'].generics[0].name == 'Int'
    
    def test_rep_function(self):
        """rep(x, times) -> Vector[T]"""
        source = 'let x = rep(5, 3);'
        program = Parser(source).parse()
        analyzer = SemanticAnalyzer()
        analyzer.analyze(program)
        assert analyzer.env['x'].name == 'Vector'
        assert analyzer.env['x'].generics[0].name == 'Int'


class TestProbabilityDistributions:
    """Test probability distribution functions"""
    
    def test_dnorm(self):
        """dnorm(x, mean, sd) -> Float"""
        source = 'let d = dnorm(0, 0, 1);'
        program = Parser(source).parse()
        analyzer = SemanticAnalyzer()
        analyzer.analyze(program)
        assert analyzer.env['d'].name == 'Float'
    
    def test_pnorm(self):
        """pnorm(q, mean, sd) -> Float"""
        source = 'let p = pnorm(1.96, 0, 1);'
        program = Parser(source).parse()
        analyzer = SemanticAnalyzer()
        analyzer.analyze(program)
        assert analyzer.env['p'].name == 'Float'
    
    def test_qnorm(self):
        """qnorm(p, mean, sd) -> Float"""
        source = 'let q = qnorm(0.975, 0, 1);'
        program = Parser(source).parse()
        analyzer = SemanticAnalyzer()
        analyzer.analyze(program)
        assert analyzer.env['q'].name == 'Float'
    
    def test_rnorm(self):
        """rnorm(n, mean, sd) -> Vector[Float]"""
        source = 'let x = rnorm(100, 0, 1);'
        program = Parser(source).parse()
        analyzer = SemanticAnalyzer()
        analyzer.analyze(program)
        assert analyzer.env['x'].name == 'Vector'
        assert analyzer.env['x'].generics[0].name == 'Float'
    
    def test_runif(self):
        """runif(n, min, max) -> Vector[Float]"""
        source = 'let x = runif(100, 0, 1);'
        program = Parser(source).parse()
        analyzer = SemanticAnalyzer()
        analyzer.analyze(program)
        assert analyzer.env['x'].name == 'Vector'
        assert analyzer.env['x'].generics[0].name == 'Float'
    
    def test_rbinom(self):
        """rbinom(n, size, prob) -> Vector[Int]"""
        source = 'let x = rbinom(100, 10, 0.5);'
        program = Parser(source).parse()
        analyzer = SemanticAnalyzer()
        analyzer.analyze(program)
        assert analyzer.env['x'].name == 'Vector'
        assert analyzer.env['x'].generics[0].name == 'Int'
    
    def test_dunif(self):
        """dunif(x, min, max) -> Float"""
        source = 'let d = dunif(0.5, 0, 1);'
        program = Parser(source).parse()
        analyzer = SemanticAnalyzer()
        analyzer.analyze(program)
        assert analyzer.env['d'].name == 'Float'


class TestMatrixOperations:
    """Test matrix and DataFrame operations"""
    
    def test_matrix_creation(self):
        """matrix(data, nrow, ncol) -> Matrix[T]"""
        source = 'let m = matrix(c(1, 2, 3, 4), 2, 2);'
        program = Parser(source).parse()
        analyzer = SemanticAnalyzer()
        analyzer.analyze(program)
        assert analyzer.env['m'].name == 'Matrix'
        assert analyzer.env['m'].generics[0].name == 'Int'
    
    def test_data_frame_creation(self):
        """data.frame(...) -> DataFrame[T]"""
        source = 'let df = data.frame(1, 2, 3);'
        program = Parser(source).parse()
        analyzer = SemanticAnalyzer()
        analyzer.analyze(program)
        assert analyzer.env['df'].name == 'DataFrame'
    
    def test_matrix_transpose(self):
        """t(x: Matrix[T]) -> Matrix[T]"""
        source = 'let m = matrix(c(1, 2, 3, 4), 2, 2); let mt = t(m);'
        program = Parser(source).parse()
        analyzer = SemanticAnalyzer()
        analyzer.analyze(program)
        assert analyzer.env['mt'].name == 'Matrix'
        assert analyzer.env['mt'].generics[0].name == 'Int'
    
    def test_nrow_ncol(self):
        """nrow(x: Matrix) -> Int, ncol(x: Matrix) -> Int"""
        source = 'let m = matrix(c(1, 2, 3, 4), 2, 2); let r = nrow(m); let c = ncol(m);'
        program = Parser(source).parse()
        analyzer = SemanticAnalyzer()
        analyzer.analyze(program)
        assert analyzer.env['r'].name == 'Int'
        assert analyzer.env['c'].name == 'Int'
    
    def test_dim(self):
        """dim(x: Matrix) -> Vector[Int]"""
        source = 'let m = matrix(c(1, 2, 3, 4), 2, 2); let d = dim(m);'
        program = Parser(source).parse()
        analyzer = SemanticAnalyzer()
        analyzer.analyze(program)
        assert analyzer.env['d'].name == 'Vector'
        assert analyzer.env['d'].generics[0].name == 'Int'
    
    def test_colSums(self):
        """colSums(x: Matrix[T]) -> Vector[T]"""
        source = 'let m = matrix(c(1, 2, 3, 4), 2, 2); let cs = colSums(m);'
        program = Parser(source).parse()
        analyzer = SemanticAnalyzer()
        analyzer.analyze(program)
        assert analyzer.env['cs'].name == 'Vector'
        assert analyzer.env['cs'].generics[0].name == 'Int'
    
    def test_colMeans(self):
        """colMeans(x: Matrix) -> Vector[Float]"""
        source = 'let m = matrix(c(1, 2, 3, 4), 2, 2); let cm = colMeans(m);'
        program = Parser(source).parse()
        analyzer = SemanticAnalyzer()
        analyzer.analyze(program)
        assert analyzer.env['cm'].name == 'Vector'
        assert analyzer.env['cm'].generics[0].name == 'Float'
    
    def test_rowSums(self):
        """rowSums(x: Matrix[T]) -> Vector[T]"""
        source = 'let m = matrix(c(1, 2, 3, 4), 2, 2); let rs = rowSums(m);'
        program = Parser(source).parse()
        analyzer = SemanticAnalyzer()
        analyzer.analyze(program)
        assert analyzer.env['rs'].name == 'Vector'
        assert analyzer.env['rs'].generics[0].name == 'Int'


class TestCorrelationCovariance:
    """Test correlation and covariance functions"""
    
    def test_cor_two_vectors(self):
        """cor(x, y) -> Float"""
        source = 'let x = c(1, 2, 3); let y = c(4, 5, 6); let r = cor(x, y);'
        program = Parser(source).parse()
        analyzer = SemanticAnalyzer()
        analyzer.analyze(program)
        assert analyzer.env['r'].name == 'Float'
    
    def test_cor_matrix(self):
        """cor(x: Matrix) -> Matrix[Float]"""
        source = 'let m = matrix(c(1, 2, 3, 4), 2, 2); let cm = cor(m);'
        program = Parser(source).parse()
        analyzer = SemanticAnalyzer()
        analyzer.analyze(program)
        assert analyzer.env['cm'].name == 'Matrix'
        assert analyzer.env['cm'].generics[0].name == 'Float'
    
    def test_cov_two_vectors(self):
        """cov(x, y) -> Float"""
        source = 'let x = c(1, 2, 3); let y = c(4, 5, 6); let cv = cov(x, y);'
        program = Parser(source).parse()
        analyzer = SemanticAnalyzer()
        analyzer.analyze(program)
        assert analyzer.env['cv'].name == 'Float'


class TestLinearRegression:
    """Test linear regression and model functions"""
    
    def test_lm_creates_model(self):
        """lm(formula, data) -> LinearModel"""
        source = 'let data = data.frame(1, 2); let model = lm(f"y ~ x", data);'
        program = Parser(source).parse()
        analyzer = SemanticAnalyzer()
        analyzer.analyze(program)
        assert analyzer.env['model'].name == 'LinearModel'
    
    def test_summary_function(self):
        """summary(x) -> Summary"""
        source = 'let data = data.frame(1, 2); let model = lm(f"y ~ x", data); let s = summary(model);'
        program = Parser(source).parse()
        analyzer = SemanticAnalyzer()
        analyzer.analyze(program)
        assert analyzer.env['s'].name == 'String'
    
    def test_predict_from_model(self):
        """predict(model: LinearModel, newdata) -> Vector[Float]"""
        source = 'let data = data.frame(1, 2); let model = lm(f"y ~ x", data); let newdata = data.frame(1); let pred = predict(model, newdata);'
        program = Parser(source).parse()
        analyzer = SemanticAnalyzer()
        analyzer.analyze(program)
        assert analyzer.env['pred'].name == 'Vector'
        assert analyzer.env['pred'].generics[0].name == 'Float'


class TestDataFrameAndModelRuntime:
    """Runtime behavior for data frames, CSV I/O, and models"""

    def test_data_frame_construction_and_length(self):
        source = 'let df = data.frame(c(1, 2, 3), c(4, 5, 6));'
        program = Parser(source).parse()
        analyzer = SemanticAnalyzer()
        analyzer.analyze(program)
        interpreter = NGSLInterpreter()
        interpreter.interpret(program)
        df = interpreter.env['df']
        assert df.type_name == 'DataFrame'
        assert hasattr(df.data, 'columns')
        assert df.data.columns == ['V1', 'V2']
        assert len(df.data.data['V1']) == 3

    def test_read_write_csv_roundtrip(self, tmp_path):
        csv_path = tmp_path / 'test.csv'
        with open(csv_path, 'w', newline='') as f:
            f.write('a,b\n1,2\n3,4\n')
        source = f'let df = read.csv("{csv_path}"); let result = write.csv(df, "{csv_path}");'
        program = Parser(source).parse()
        analyzer = SemanticAnalyzer()
        analyzer.analyze(program)
        interpreter = NGSLInterpreter()
        interpreter.interpret(program)
        result = interpreter.env['result']
        assert result.type_name == 'Unit'
        assert csv_path.exists()

    def test_glm_and_predict_runtime(self):
        source = 'let df = data.frame(c(1, 2, 3), c(2, 4, 6)); let model = glm(f"V2 ~ V1", df); let pred = predict(model, df);'
        program = Parser(source).parse()
        analyzer = SemanticAnalyzer()
        analyzer.analyze(program)
        interpreter = NGSLInterpreter()
        interpreter.interpret(program)
        pred = interpreter.env['pred']
        assert pred.type_name == 'Vector'
        assert len(pred.data) == 3

    def test_pca_runtime(self):
        source = 'let m = matrix(c(1.0, 2.0, 1.0, 2.0), 2, 2); let result = pca(m);'
        program = Parser(source).parse()
        analyzer = SemanticAnalyzer()
        analyzer.analyze(program)
        interpreter = NGSLInterpreter()
        interpreter.interpret(program)
        result = interpreter.env['result']
        assert result.type_name == 'PCAResult'
        assert result.data.components.shape[0] == 2

    def test_kmeans_runtime(self):
        source = 'let m = matrix(c(1.0, 1.0, 10.0, 10.0), 2, 2); let result = kmeans(m, 2);'
        program = Parser(source).parse()
        analyzer = SemanticAnalyzer()
        analyzer.analyze(program)
        interpreter = NGSLInterpreter()
        interpreter.interpret(program)
        result = interpreter.env['result']
        assert result.type_name == 'KMeansResult'
        assert len(result.data.labels) == 2


class TestMatrixAlgebra:
    """Test matrix algebra operations"""
    
    def test_matrix_determinant(self):
        """det(x: Matrix[Float]) -> Float"""
        source = 'let m = matrix(c(1.0, 2.0, 3.0, 4.0), 2, 2); let d = det(m);'
        program = Parser(source).parse()
        analyzer = SemanticAnalyzer()
        analyzer.analyze(program)
        assert analyzer.env['d'].name == 'Float'
    
    def test_matrix_inverse(self):
        """inv(x: Matrix[Float]) -> Matrix[Float]"""
        source = 'let m = matrix(c(1.0, 2.0, 3.0, 4.0), 2, 2); let mi = inv(m);'
        program = Parser(source).parse()
        analyzer = SemanticAnalyzer()
        analyzer.analyze(program)
        assert analyzer.env['mi'].name == 'Matrix'
        assert analyzer.env['mi'].generics[0].name == 'Float'
    
    def test_solve_linear_system(self):
        """solve(a: Matrix, b: Vector) -> Vector[Float]"""
        source = 'let a = matrix(c(1.0, 2.0, 3.0, 4.0), 2, 2); let b = c(1.0, 2.0); let x = solve(a, b);'
        program = Parser(source).parse()
        analyzer = SemanticAnalyzer()
        analyzer.analyze(program)
        assert analyzer.env['x'].name == 'Vector'
        assert analyzer.env['x'].generics[0].name == 'Float'
