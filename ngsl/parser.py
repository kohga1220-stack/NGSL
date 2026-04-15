from __future__ import annotations
from typing import List, Optional
from .lexer import Lexer, Token, TokenType
from .ast import (
    Program,
    LetStatement,
    ReturnStatement,
    ExpressionStatement,
    Identifier,
    NumberLiteral,
    StringLiteral,
    BooleanLiteral,
    FormulaLiteral,
    BinaryExpression,
    CallExpression,
    MethodCallExpression,
    PropertyAccess,
    KeywordArgument,
    BorrowExpression,
    BlockStatement,
    DropExpression,
    FunctionDef,
    TypeAnnotation,
    ResultType,
)
from .errors import ParserError

PRECEDENCE = {
    TokenType.PLUS: 1,
    TokenType.MINUS: 1,
    TokenType.STAR: 2,
    TokenType.SLASH: 2,
}

class Parser:
    def __init__(self, source: str):
        self.tokens = Lexer(source).tokenize()
        self.current = 0

    def parse(self) -> Program:
        statements = []
        while not self._match(TokenType.EOF):
            statements.append(self._parse_statement())
            if self._match(TokenType.SEMICOLON):
                continue
        return Program(statements)

    def _parse_statement(self):
        if self._match(TokenType.LET):
            return self._parse_let_statement()
        if self._match(TokenType.RETURN):
            return self._parse_return_statement()
        if self._match(TokenType.DROP):
            return self._parse_drop_statement()
        if self._match(TokenType.LBRACE):
            return self._parse_block_statement()
        return ExpressionStatement(self._parse_expression())

    def _parse_let_statement(self) -> LetStatement:
        name = self._consume(TokenType.IDENT, "Expected identifier after 'let'").lexeme
        type_annotation = None
        if self._match(TokenType.COLON):
            type_annotation = self._parse_type()
        self._consume(TokenType.ASSIGN, "Expected '=' after let declaration")
        value = self._parse_expression()
        return LetStatement(name, type_annotation, value)

    def _parse_return_statement(self) -> ReturnStatement:
        value = self._parse_expression()
        return ReturnStatement(value)

    def _parse_drop_statement(self):
        self._consume(TokenType.LPAREN, "Expected '(' after 'drop'")
        target = self._parse_expression()
        self._consume(TokenType.RPAREN, "Expected ')' after drop target")
        return ExpressionStatement(DropExpression(target))

    def _parse_expression(self, precedence: int = 0):
        expr = self._parse_method_chain()
        while self._peek().type in PRECEDENCE and PRECEDENCE[self._peek().type] >= precedence:
            operator = self._advance()
            next_precedence = PRECEDENCE[operator.type] + 1
            right = self._parse_expression(next_precedence)
            expr = BinaryExpression(expr, operator.lexeme, right)
        return expr

    def _parse_method_chain(self):
        expr = self._parse_primary()
        while True:
            if self._match(TokenType.LPAREN):
                arguments = []
                if not self._check(TokenType.RPAREN):
                    arguments.append(self._parse_argument())
                    while self._match(TokenType.COMMA):
                        arguments.append(self._parse_argument())
                self._consume(TokenType.RPAREN, "Expected ')' after function call")
                expr = CallExpression(expr, arguments)
                continue
            if self._match(TokenType.DOT):
                property_name = self._consume(TokenType.IDENT, "Expected identifier after '.'").lexeme
                if self._match(TokenType.LPAREN):
                    arguments = []
                    if not self._check(TokenType.RPAREN):
                        arguments.append(self._parse_argument())
                        while self._match(TokenType.COMMA):
                            arguments.append(self._parse_argument())
                    self._consume(TokenType.RPAREN, "Expected ')' after method call")
                    expr = MethodCallExpression(expr, property_name, arguments)
                else:
                    expr = PropertyAccess(expr, property_name)
                continue
            if self._match(TokenType.DOLLAR):
                property_name = self._consume(TokenType.IDENT, "Expected identifier after '$'").lexeme
                expr = PropertyAccess(expr, property_name)
                continue
            break
        return expr

    def _peek_next(self) -> Token:
        if self.current + 1 < len(self.tokens):
            return self.tokens[self.current + 1]
        return Token(TokenType.EOF, "", self._peek().line, self._peek().column)

    def _parse_argument(self):
        if self._check(TokenType.IDENT) and self._peek_next().type == TokenType.ASSIGN:
            name = self._advance().lexeme
            self._advance()  # consume ASSIGN
            value = self._parse_expression()
            return KeywordArgument(name, value)
        return self._parse_expression()

    def _parse_primary(self):
        if self._match(TokenType.AMPERSAND):
            mutable = False
            if self._match(TokenType.IDENT) and self._previous().lexeme == "mut":
                mutable = True
            elif self._previous().lexeme != "mut":
                self.current -= 1
            target = self._parse_primary()
            return BorrowExpression(target, mutable)
        if self._match(TokenType.INT):
            return NumberLiteral(int(self._previous().lexeme))
        if self._match(TokenType.FLOAT):
            return NumberLiteral(float(self._previous().lexeme))
        if self._match(TokenType.STRING):
            return StringLiteral(self._previous().lexeme)
        if self._match(TokenType.TRUE):
            return BooleanLiteral(True)
        if self._match(TokenType.FALSE):
            return BooleanLiteral(False)
        if self._match(TokenType.FORMULA):
            return FormulaLiteral(self._previous().lexeme)
        if self._match(TokenType.IDENT):
            return Identifier(self._previous().lexeme)
        if self._match(TokenType.LPAREN):
            expr = self._parse_expression()
            self._consume(TokenType.RPAREN, "Expected ')' after expression")
            return expr
        raise ParserError(f"Unexpected token {self._peek().type} at position {self.current}")

    def _parse_block_statement(self):
        statements = []
        while not self._check(TokenType.RBRACE) and not self._is_at_end():
            statements.append(self._parse_statement())
            if self._match(TokenType.SEMICOLON):
                continue
        self._consume(TokenType.RBRACE, "Expected '}' after block")
        return BlockStatement(statements)

    def _parse_type(self):
        if self._match(TokenType.IDENT):
            name = self._previous().lexeme
            generics = None
            if self._match(TokenType.LBRACKET):
                generics = [self._parse_type()]
                while self._match(TokenType.COMMA):
                    generics.append(self._parse_type())
                self._consume(TokenType.RBRACKET, "Expected ']' after generic type")
            if name == "Result":
                if generics is None or len(generics) != 2:
                    raise ParserError("Result type requires two type arguments")
                return ResultType(generics[0], generics[1])
            return TypeAnnotation(name, generics)
        raise ParserError("Expected type annotation")

    def _match(self, *types: TokenType) -> bool:
        for token_type in types:
            if self._check(token_type):
                self._advance()
                return True
        return False

    def _check(self, token_type: TokenType) -> bool:
        return self._peek().type == token_type

    def _advance(self) -> Token:
        if not self._is_at_end():
            self.current += 1
        return self._previous()

    def _consume(self, token_type: TokenType, message: str) -> Token:
        if self._check(token_type):
            return self._advance()
        raise ParserError(message)

    def _peek(self) -> Token:
        return self.tokens[self.current]

    def _previous(self) -> Token:
        return self.tokens[self.current - 1]

    def _is_at_end(self) -> bool:
        return self._peek().type == TokenType.EOF
