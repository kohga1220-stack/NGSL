import pytest
from ngsl.lexer import Lexer, TokenType
from ngsl.errors import LexerError


def test_lexer_basic_tokens():
    source = 'let x: Int = 42; return x + 3.14;'
    tokens = Lexer(source).tokenize()
    assert [token.type for token in tokens] == [
        TokenType.LET,
        TokenType.IDENT,
        TokenType.COLON,
        TokenType.IDENT,
        TokenType.ASSIGN,
        TokenType.INT,
        TokenType.SEMICOLON,
        TokenType.RETURN,
        TokenType.IDENT,
        TokenType.PLUS,
        TokenType.FLOAT,
        TokenType.SEMICOLON,
        TokenType.EOF,
    ]


def test_lexer_formula_literal():
    source = 'let f = f"y ~ x + z";'
    tokens = Lexer(source).tokenize()
    assert tokens[3].type == TokenType.FORMULA
    assert tokens[3].lexeme == 'y ~ x + z'


def test_lexer_unterminated_string():
    with pytest.raises(LexerError):
        Lexer('"hello').tokenize()
