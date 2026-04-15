import pytest
from ngsl.parser import Parser
from ngsl.semantics import SemanticAnalyzer
from ngsl.errors import SemanticError


def test_semantics_numeric_promotion():
    source = 'let x = 3 + 2.5;'
    program = Parser(source).parse()
    analyzer = SemanticAnalyzer()
    analyzer.analyze(program)


def test_semantics_vector_method_inference():
    source = 'let data: Vector[Int] = some_source; data.filter().map();'
    program = Parser(source).parse()
    analyzer = SemanticAnalyzer()
    analyzer.analyze(program)


def test_semantics_ok_result_inference():
    source = 'let r: Result[Int, String] = Ok(1);'
    program = Parser(source).parse()
    analyzer = SemanticAnalyzer()
    analyzer.analyze(program)


def test_semantics_immutable_borrow_allows_multiple_reads():
    source = 'let x = 5; let y = &x; let z = &x;'
    program = Parser(source).parse()
    analyzer = SemanticAnalyzer()
    analyzer.analyze(program)


def test_semantics_mutable_borrow_exclusion():
    source = 'let x = 5; let y = &x; let z = &mut x;'
    program = Parser(source).parse()
    analyzer = SemanticAnalyzer()
    with pytest.raises(Exception, match="borrowed"):
        analyzer.analyze(program)


def test_semantics_move_after_borrow_error():
    source = 'let x = "hello"; let y = &x; let z = x;'
    program = Parser(source).parse()
    analyzer = SemanticAnalyzer()
    with pytest.raises(Exception, match="Cannot move borrowed value"):
        analyzer.analyze(program)


def test_semantics_borrow_scope_release_in_block():
    source = 'let x = 5; { let y = &x; } let z = &mut x;'
    program = Parser(source).parse()
    analyzer = SemanticAnalyzer()
    analyzer.analyze(program)


def test_semantics_borrow_scope_outlives_error():
    source = 'let x = 5; let y = &x; { let z = &mut x; }'
    program = Parser(source).parse()
    analyzer = SemanticAnalyzer()
    with pytest.raises(Exception, match="borrowed"):
        analyzer.analyze(program)


def test_semantics_explicit_drop_release():
    source = 'let x = "hello"; let y = &x; drop(y); let z = &mut x;'
    program = Parser(source).parse()
    analyzer = SemanticAnalyzer()
    analyzer.analyze(program)


def test_semantics_drop_moved_value_error():
    source = 'let x = "hello"; let y = x; drop(x);'
    program = Parser(source).parse()
    analyzer = SemanticAnalyzer()
    with pytest.raises(Exception, match="moved"):
        analyzer.analyze(program)


def test_semantics_drop_borrowed_value_error():
    source = 'let x = 5; let y = &x; drop(x);'
    program = Parser(source).parse()
    analyzer = SemanticAnalyzer()
    with pytest.raises(Exception, match="borrowed"):
        analyzer.analyze(program)
