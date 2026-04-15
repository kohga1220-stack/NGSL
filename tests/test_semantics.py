import pytest
from ngsl.parser import Parser
from ngsl.semantics import SemanticAnalyzer
from ngsl.errors import SemanticError


def test_semantics_type_mismatch():
    source = 'let x: Int = 3.14;'
    program = Parser(source).parse()
    analyzer = SemanticAnalyzer()
    with pytest.raises(SemanticError, match="Type mismatch"):
        analyzer.analyze(program)


def test_semantics_move_error():
    source = 'let a: String = "hello"; let b = a; let c = a;'
    program = Parser(source).parse()
    analyzer = SemanticAnalyzer()
    with pytest.raises(SemanticError, match="Use of moved variable"):
        analyzer.analyze(program)


def test_semantics_method_chain_type():
    source = 'let some_value = 1; let data = some_value; data.filter().map();'
    program = Parser(source).parse()
    analyzer = SemanticAnalyzer()
    analyzer.analyze(program)
