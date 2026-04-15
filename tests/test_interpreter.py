"""
Tests for BLAS/LAPACK integration with NumPy backend
"""

import pytest
import numpy as np
from ngsl import Parser, SemanticAnalyzer, NGSLInterpreter, NGSLValue


class TestBasicArithmetic:
    """Test basic arithmetic with NumPy backend"""
    
    def test_vector_addition(self):
        """Test vector addition using NumPy"""
        source = 'let x = c(1, 2, 3); let y = c(4, 5, 6); let z = x + y;'
        program = Parser(source).parse()
        analyzer = SemanticAnalyzer()
        analyzer.analyze(program)
        
        interpreter = NGSLInterpreter()
        interpreter.interpret(program)
        
        assert 'z' in interpreter.env
        z = interpreter.env['z']
        assert z.type_name == 'Vector'
        np.testing.assert_array_equal(z.data, np.array([5, 7, 9]))
    
    def test_vector_subtraction(self):
        """Test vector subtraction"""
        source = 'let x = c(5, 6, 7); let y = c(1, 2, 3); let z = x - y;'
        program = Parser(source).parse()
        analyzer = SemanticAnalyzer()
        analyzer.analyze(program)
        
        interpreter = NGSLInterpreter()
        interpreter.interpret(program)
        
        z = interpreter.env['z']
        np.testing.assert_array_equal(z.data, np.array([4, 4, 4]))
    
    def test_vector_multiplication(self):
        """Test element-wise vector multiplication"""
        source = 'let x = c(1, 2, 3); let y = c(2, 3, 4); let z = x * y;'
        program = Parser(source).parse()
        analyzer = SemanticAnalyzer()
        analyzer.analyze(program)
        
        interpreter = NGSLInterpreter()
        interpreter.interpret(program)
        
        z = interpreter.env['z']
        np.testing.assert_array_equal(z.data, np.array([2, 6, 12]))
    
    def test_vector_division(self):
        """Test element-wise vector division"""
        source = 'let x = c(4.0, 6.0, 8.0); let y = c(2.0, 3.0, 4.0); let z = x / y;'
        program = Parser(source).parse()
        analyzer = SemanticAnalyzer()
        analyzer.analyze(program)
        
        interpreter = NGSLInterpreter()
        interpreter.interpret(program)
        
        z = interpreter.env['z']
        np.testing.assert_array_almost_equal(z.data, np.array([2.0, 2.0, 2.0]))


class TestDescriptiveStatistics:
    """Test statistical functions with NumPy"""
    
    def test_mean(self):
        """Test mean calculation"""
        source = 'let x = c(1, 2, 3, 4, 5); let m = mean(x);'
        program = Parser(source).parse()
        analyzer = SemanticAnalyzer()
        analyzer.analyze(program)
        
        interpreter = NGSLInterpreter()
        interpreter.interpret(program)
        
        m = interpreter.env['m']
        assert m.type_name == 'Float'
        assert m.data == 3.0
    
    def test_variance(self):
        """Test variance calculation"""
        source = 'let x = c(1, 2, 3, 4, 5); let v = var(x);'
        program = Parser(source).parse()
        analyzer = SemanticAnalyzer()
        analyzer.analyze(program)
        
        interpreter = NGSLInterpreter()
        interpreter.interpret(program)
        
        v = interpreter.env['v']
        assert v.type_name == 'Float'
        assert v.data == 2.0
    
    def test_std_dev(self):
        """Test standard deviation calculation"""
        source = 'let x = c(1, 2, 3, 4, 5); let s = sd(x);'
        program = Parser(source).parse()
        analyzer = SemanticAnalyzer()
        analyzer.analyze(program)
        
        interpreter = NGSLInterpreter()
        interpreter.interpret(program)
        
        s = interpreter.env['s']
        assert s.type_name == 'Float'
        assert abs(s.data - np.sqrt(2.0)) < 0.0001
    
    def test_median(self):
        """Test median calculation"""
        source = 'let x = c(1, 2, 3, 4, 5); let med = median(x);'
        program = Parser(source).parse()
        analyzer = SemanticAnalyzer()
        analyzer.analyze(program)
        
        interpreter = NGSLInterpreter()
        interpreter.interpret(program)
        
        med = interpreter.env['med']
        assert med.type_name == 'Float'
        assert med.data == 3.0
    
    def test_sum(self):
        """Test sum calculation"""
        source = 'let x = c(1, 2, 3, 4, 5); let total = sum(x);'
        program = Parser(source).parse()
        analyzer = SemanticAnalyzer()
        analyzer.analyze(program)
        
        interpreter = NGSLInterpreter()
        interpreter.interpret(program)
        
        total = interpreter.env['total']
        assert total.type_name == 'Float'
        assert total.data == 15.0


class TestVectorGeneration:
    """Test vector generation functions"""
    
    def test_seq(self):
        """Test sequence generation"""
        source = 'let x = seq(1, 5, 1);'
        program = Parser(source).parse()
        analyzer = SemanticAnalyzer()
        analyzer.analyze(program)
        
        interpreter = NGSLInterpreter()
        interpreter.interpret(program)
        
        x = interpreter.env['x']
        assert x.type_name == 'Vector'
        np.testing.assert_array_equal(x.data, np.array([1, 2, 3, 4, 5]))
    
    def test_range(self):
        """Test range generation"""
        source = 'let x = range(1, 5);'
        program = Parser(source).parse()
        analyzer = SemanticAnalyzer()
        analyzer.analyze(program)
        
        interpreter = NGSLInterpreter()
        interpreter.interpret(program)
        
        x = interpreter.env['x']
        assert x.type_name == 'Vector'
        np.testing.assert_array_equal(x.data, np.array([1, 2, 3, 4, 5]))
    
    def test_rep(self):
        """Test repetition"""
        source = 'let x = rep(5, 3);'
        program = Parser(source).parse()
        analyzer = SemanticAnalyzer()
        analyzer.analyze(program)
        
        interpreter = NGSLInterpreter()
        interpreter.interpret(program)
        
        x = interpreter.env['x']
        assert x.type_name == 'Vector'
        np.testing.assert_array_equal(x.data, np.array([5, 5, 5]))

    def test_dataframe_property_access(self):
        """Test data.frame column access via df.V1"""
        source = 'let df = data.frame(c(1, 2), c(3, 4)); let x = df.V1;'
        program = Parser(source).parse()
        analyzer = SemanticAnalyzer()
        analyzer.analyze(program)
        
        interpreter = NGSLInterpreter()
        interpreter.interpret(program)
        
        x = interpreter.env['x']
        assert x.type_name == 'Vector'
        np.testing.assert_array_equal(x.data, np.array([1, 2]))

    def test_dataframe_dollar_access(self):
        """Test data.frame column access via df$V1"""
        source = 'let df = data.frame(c(1, 2), c(3, 4)); let x = df$V1;'
        program = Parser(source).parse()
        analyzer = SemanticAnalyzer()
        analyzer.analyze(program)
        
        interpreter = NGSLInterpreter()
        interpreter.interpret(program)
        
        x = interpreter.env['x']
        assert x.type_name == 'Vector'
        np.testing.assert_array_equal(x.data, np.array([1, 2]))

    def test_read_csv_options(self, tmp_path):
        """Test read.csv with header and separator options"""
        csv_file = tmp_path / 'sample.csv'
        csv_file.write_text('a;b\n1;2\n3;4\n')
        source = f'let df = read.csv("{csv_file}", header=TRUE, sep=";"); let x = df.a;'
        program = Parser(source).parse()
        analyzer = SemanticAnalyzer()
        analyzer.analyze(program)
        
        interpreter = NGSLInterpreter()
        interpreter.interpret(program)
        
        x = interpreter.env['x']
        assert x.type_name == 'Vector'
        np.testing.assert_array_equal(x.data, np.array([1, 3]))

    def test_write_csv_options(self, tmp_path):
        """Test write.csv with row_names and separator options"""
        out_file = tmp_path / 'out.csv'
        source = f'let df = data.frame(c(1, 2), c(3, 4)); write.csv(df, "{out_file}", row_names=FALSE, sep=",");'
        program = Parser(source).parse()
        analyzer = SemanticAnalyzer()
        analyzer.analyze(program)
        
        interpreter = NGSLInterpreter()
        interpreter.interpret(program)
        
        assert out_file.exists()
        content = out_file.read_text()
        assert 'V1,V2' in content
        assert '1,3' in content
        assert '2,4' in content
        assert 'row.names' not in content

    def test_write_csv_options_row_names_property(self, tmp_path):
        """Test write.csv with row.names alias"""
        out_file = tmp_path / 'out2.csv'
        source = f'let df = data.frame(c(1, 2), c(3, 4)); write.csv(df, "{out_file}", row.names=FALSE, sep=",");'
        program = Parser(source).parse()
        analyzer = SemanticAnalyzer()
        analyzer.analyze(program)
        
        interpreter = NGSLInterpreter()
        interpreter.interpret(program)
        
        assert out_file.exists()
        content = out_file.read_text()
        assert 'V1,V2' in content
        assert '1,3' in content
        assert '2,4' in content
        assert 'row.names' not in content

    def test_read_csv_row_names_option(self, tmp_path):
        """Test read.csv with row.names option alias"""
        csv_file = tmp_path / 'sample2.csv'
        csv_file.write_text('a;b\n1;2\n3;4\n')
        source = f'let df = read.csv("{csv_file}", header=TRUE, sep=";", row.names=FALSE); let x = df.a;'
        program = Parser(source).parse()
        analyzer = SemanticAnalyzer()
        analyzer.analyze(program)
        
        interpreter = NGSLInterpreter()
        interpreter.interpret(program)
        
        x = interpreter.env['x']
        assert x.type_name == 'Vector'
        np.testing.assert_array_equal(x.data, np.array([1, 3]))


class TestMatrixOperations:
    """Test matrix operations with BLAS/LAPACK backend"""
    
    def test_matrix_creation(self):
        """Test matrix creation"""
        source = 'let m = matrix(c(1, 2, 3, 4), 2, 2);'
        program = Parser(source).parse()
        analyzer = SemanticAnalyzer()
        analyzer.analyze(program)
        
        interpreter = NGSLInterpreter()
        interpreter.interpret(program)
        
        m = interpreter.env['m']
        assert m.type_name == 'Matrix'
        assert m.data.shape == (2, 2)
    
    def test_matrix_transpose(self):
        """Test matrix transpose using BLAS"""
        source = 'let m = matrix(c(1, 2, 3, 4), 2, 2); let mt = t(m);'
        program = Parser(source).parse()
        analyzer = SemanticAnalyzer()
        analyzer.analyze(program)
        
        interpreter = NGSLInterpreter()
        interpreter.interpret(program)
        
        mt = interpreter.env['mt']
        assert mt.type_name == 'Matrix'
        np.testing.assert_array_equal(mt.data, np.array([[1, 3], [2, 4]]))
    
    def test_matrix_determinant(self):
        """Test matrix determinant using LAPACK"""
        source = 'let m = matrix(c(1.0, 2.0, 3.0, 4.0), 2, 2); let d = det(m);'
        program = Parser(source).parse()
        analyzer = SemanticAnalyzer()
        analyzer.analyze(program)
        
        interpreter = NGSLInterpreter()
        interpreter.interpret(program)
        
        d = interpreter.env['d']
        assert d.type_name == 'Float'
        assert abs(d.data - (-2.0)) < 0.0001
    
    def test_matrix_inverse(self):
        """Test matrix inverse using LAPACK"""
        source = 'let m = matrix(c(1.0, 2.0, 3.0, 4.0), 2, 2); let mi = inv(m);'
        program = Parser(source).parse()
        analyzer = SemanticAnalyzer()
        analyzer.analyze(program)
        
        interpreter = NGSLInterpreter()
        interpreter.interpret(program)
        
        mi = interpreter.env['mi']
        assert mi.type_name == 'Matrix'
        expected = np.array([[-2.0, 1.0], [1.5, -0.5]])
        np.testing.assert_array_almost_equal(mi.data, expected)
    
    def test_matrix_multiply(self):
        """Test matrix multiplication using BLAS"""
        source = 'let a = matrix(c(1, 2, 3, 4), 2, 2); let b = matrix(c(5, 6, 7, 8), 2, 2); let c = a * b;'
        program = Parser(source).parse()
        analyzer = SemanticAnalyzer()
        analyzer.analyze(program)
        
        interpreter = NGSLInterpreter()
        interpreter.interpret(program)
        
        c = interpreter.env['c']
        assert c.type_name == 'Matrix'
        # Expected: [[1, 2], [3, 4]] * [[5, 6], [7, 8]] = [[19, 22], [43, 50]]
        expected = np.array([[19, 22], [43, 50]])
        np.testing.assert_array_equal(c.data, expected)
    
    def test_solve_linear_system(self):
        """Test solving linear system using LAPACK"""
        source = 'let a = matrix(c(1.0, 2.0, 3.0, 4.0), 2, 2); let b = c(1.0, 2.0); let x = solve(a, b);'
        program = Parser(source).parse()
        analyzer = SemanticAnalyzer()
        analyzer.analyze(program)
        
        interpreter = NGSLInterpreter()
        interpreter.interpret(program)
        
        x = interpreter.env['x']
        assert x.type_name == 'Vector'
        # Verify Ax = b
        A = np.array([[1.0, 2.0], [3.0, 4.0]])
        computed_b = np.dot(A, x.data)
        np.testing.assert_array_almost_equal(computed_b, np.array([1.0, 2.0]))


class TestDistributions:
    """Test probability distributions"""
    
    def test_dnorm(self):
        """Test normal distribution PDF"""
        source = 'let d = dnorm(0, 0, 1);'
        program = Parser(source).parse()
        analyzer = SemanticAnalyzer()
        analyzer.analyze(program)
        
        interpreter = NGSLInterpreter()
        interpreter.interpret(program)
        
        d = interpreter.env['d']
        assert d.type_name == 'Float'
        expected = 1.0 / np.sqrt(2 * np.pi)
        assert abs(d.data - expected) < 0.0001
    
    def test_pnorm(self):
        """Test normal distribution CDF"""
        source = 'let p = pnorm(0, 0, 1);'
        program = Parser(source).parse()
        analyzer = SemanticAnalyzer()
        analyzer.analyze(program)
        
        interpreter = NGSLInterpreter()
        interpreter.interpret(program)
        
        p = interpreter.env['p']
        assert p.type_name == 'Float'
        assert abs(p.data - 0.5) < 0.0001
    
    def test_rnorm(self):
        """Test normal distribution random generation"""
        source = 'let x = rnorm(1000, 0, 1);'
        program = Parser(source).parse()
        analyzer = SemanticAnalyzer()
        analyzer.analyze(program)
        
        interpreter = NGSLInterpreter()
        interpreter.interpret(program)
        
        x = interpreter.env['x']
        assert x.type_name == 'Vector'
        assert len(x.data) == 1000
        # Check that mean is approximately 0 and std is approximately 1
        assert abs(np.mean(x.data)) < 0.1
        assert abs(np.std(x.data) - 1.0) < 0.1


class TestCorrelation:
    """Test correlation and covariance"""
    
    def test_correlation(self):
        """Test correlation between two vectors"""
        source = 'let x = c(1, 2, 3, 4, 5); let y = c(2, 4, 6, 8, 10); let r = cor(x, y);'
        program = Parser(source).parse()
        analyzer = SemanticAnalyzer()
        analyzer.analyze(program)
        
        interpreter = NGSLInterpreter()
        interpreter.interpret(program)
        
        r = interpreter.env['r']
        assert r.type_name == 'Float'
        # Perfect correlation
        assert abs(r.data - 1.0) < 0.0001


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
