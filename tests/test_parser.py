import pytest
from ngsl.parser import Parser
from ngsl.ast import Program, LetStatement, Identifier, NumberLiteral, BinaryExpression, TypeAnnotation, FormulaLiteral


def test_parser_let_statement():
    source = 'let x: Int = 7 + 5;'
    program = Parser(source).parse()
    assert isinstance(program, Program)
    assert len(program.statements) == 1
    stmt = program.statements[0]
    assert isinstance(stmt, LetStatement)
    assert stmt.name == 'x'
    assert isinstance(stmt.type_annotation, TypeAnnotation)
    assert isinstance(stmt.value, BinaryExpression)


def test_parser_method_chain():
    source = 'data.filter(x).map(y)'
    program = Parser(source).parse()
    expr = program.statements[0].expression
    assert expr.method_name == 'map'
    assert expr.receiver.method_name == 'filter'


def test_parser_formula_literal():
    source = 'let f = f"y ~ x + z";'
    program = Parser(source).parse()
    stmt = program.statements[0]
    assert isinstance(stmt.value, FormulaLiteral)
    assert stmt.value.value == 'y ~ x + z'


def test_parser_missing_equal():
    with pytest.raises(Exception):
        Parser('let x: Int 7 + 2;').parse()
