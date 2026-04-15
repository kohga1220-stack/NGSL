from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import List, Optional
from .errors import LexerError

class TokenType(Enum):
    EOF = auto()
    IDENT = auto()
    INT = auto()
    FLOAT = auto()
    STRING = auto()
    FORMULA = auto()
    TRUE = auto()
    FALSE = auto()
    LET = auto()
    RETURN = auto()
    DROP = auto()
    COLON = auto()
    SEMICOLON = auto()
    COMMA = auto()
    ASSIGN = auto()
    DOT = auto()
    LPAREN = auto()
    RPAREN = auto()
    LBRACKET = auto()
    RBRACKET = auto()
    LBRACE = auto()
    RBRACE = auto()
    PLUS = auto()
    MINUS = auto()
    STAR = auto()
    SLASH = auto()
    DOLLAR = auto()
    TILDE = auto()
    AMPERSAND = auto()
    LT = auto()
    GT = auto()
    EQ = auto()

KEYWORDS = {
    "let": TokenType.LET,
    "return": TokenType.RETURN,
    "drop": TokenType.DROP,
    "mut": TokenType.IDENT,
    "Int": TokenType.IDENT,
    "Float": TokenType.IDENT,
    "String": TokenType.IDENT,
    "Bool": TokenType.IDENT,
    "Dist": TokenType.IDENT,
    "Vector": TokenType.IDENT,
    "TRUE": TokenType.TRUE,
    "FALSE": TokenType.FALSE,
}

@dataclass
class Token:
    type: TokenType
    lexeme: str
    line: int
    column: int

@dataclass
class Lexer:
    source: str
    position: int = 0
    line: int = 1
    column: int = 1
    tokens: List[Token] = None

    def __post_init__(self):
        self.tokens = []

    def tokenize(self) -> List[Token]:
        while not self._is_at_end():
            self._skip_whitespace_and_comments()
            if self._is_at_end():
                break
            start = self.position
            ch = self._advance()
            if ch == 'f' and self._peek() == '"':
                self._formula(start)
            elif ch.isalpha() or ch == '_':
                self._identifier_or_keyword(start)
            elif ch.isdigit():
                self._number(start)
            elif ch == '"':
                self._string(start)
            else:
                self._single_char_token(ch)
        self.tokens.append(Token(TokenType.EOF, "", self.line, self.column))
        return self.tokens

    def _is_at_end(self) -> bool:
        return self.position >= len(self.source)

    def _advance(self) -> str:
        ch = self.source[self.position]
        self.position += 1
        self.column += 1
        return ch

    def _peek(self) -> str:
        return self.source[self.position] if not self._is_at_end() else "\0"

    def _peek_next(self) -> str:
        return self.source[self.position + 1] if self.position + 1 < len(self.source) else "\0"

    def _skip_whitespace_and_comments(self) -> None:
        while not self._is_at_end():
            ch = self._peek()
            if ch in " \t\r":
                self._advance()
                continue
            if ch == '\n':
                self._advance()
                self.line += 1
                self.column = 1
                continue
            if ch == '/' and self._peek_next() == '/':
                self._advance(); self._advance()
                while not self._is_at_end() and self._peek() != '\n':
                    self._advance()
                continue
            break

    def _identifier_or_keyword(self, start: int) -> None:
        # Standard identifier: alphanumeric and underscore
        while self._peek().isalnum() or self._peek() == '_':
            self._advance()
        
        # Support dotted names like "data.frame" only for specific patterns
        # Check if we have a dot followed by a letter (potential multi-part identifier)
        if self._peek() == '.' and self._peek_next().isalpha():
            # Look ahead to see if this looks like a function name (ends before parens/whitespace)
            saved_pos = self.position
            self._advance()  # consume dot
            while self._peek().isalnum() or self._peek() == '_':
                self._advance()
            # Allow dotted identifiers only for known patterns or if no method call follows
            # For now, keep the dot as a separate token if it's clearly a method call pattern
            if self._peek() in ['(', ' ', '\t', ';', '\n', ')']:
                # This is likely a method call, revert
                self.position = saved_pos
            # Otherwise, keep the dotted identifier
        
        text = self.source[start:self.position]
        token_type = KEYWORDS.get(text, TokenType.IDENT)
        self.tokens.append(Token(token_type, text, self.line, self.column))

    def _number(self, start: int) -> None:
        while self._peek().isdigit():
            self._advance()
        if self._peek() == '.' and self._peek_next().isdigit():
            self._advance()
            while self._peek().isdigit():
                self._advance()
            token_type = TokenType.FLOAT
        else:
            token_type = TokenType.INT
        text = self.source[start:self.position]
        self.tokens.append(Token(token_type, text, self.line, self.column))

    def _string(self, start: int) -> None:
        value = []
        while not self._is_at_end() and self._peek() != '"':
            ch = self._advance()
            if ch == '\n':
                raise LexerError(f"Unterminated string literal at line {self.line}")
            value.append(ch)
        if self._is_at_end():
            raise LexerError(f"Unterminated string literal at line {self.line}")
        self._advance()
        self.tokens.append(Token(TokenType.STRING, ''.join(value), self.line, self.column))

    def _formula(self, start: int) -> None:
        if self._peek() != '"':
            raise LexerError(f"Invalid formula prefix at line {self.line}")
        self._advance()
        value = []
        while not self._is_at_end() and self._peek() != '"':
            value.append(self._advance())
        if self._is_at_end():
            raise LexerError(f"Unterminated formula literal at line {self.line}")
        self._advance()
        self.tokens.append(Token(TokenType.FORMULA, ''.join(value), self.line, self.column))

    def _single_char_token(self, ch: str) -> None:
        token_map = {
            ':': TokenType.COLON,
            ';': TokenType.SEMICOLON,
            ',': TokenType.COMMA,
            '=': TokenType.ASSIGN,
            '.': TokenType.DOT,
            '(': TokenType.LPAREN,
            ')': TokenType.RPAREN,
            '[': TokenType.LBRACKET,
            ']': TokenType.RBRACKET,
            '{': TokenType.LBRACE,
            '}': TokenType.RBRACE,
            '+': TokenType.PLUS,
            '-': TokenType.MINUS,
            '*': TokenType.STAR,
            '/': TokenType.SLASH,
            '$': TokenType.DOLLAR,
            '~': TokenType.TILDE,
            '&': TokenType.AMPERSAND,
            '<': TokenType.LT,
            '>': TokenType.GT,
        }
        token_type = token_map.get(ch)
        if token_type is None:
            raise LexerError(f"Unexpected character '{ch}' at line {self.line} column {self.column}")
        self.tokens.append(Token(token_type, ch, self.line, self.column))
