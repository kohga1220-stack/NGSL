from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Node:
    pass

@dataclass
class Program(Node):
    statements: List[Node]

@dataclass
class LetStatement(Node):
    name: str
    type_annotation: Optional[Node]
    value: Node

@dataclass
class ReturnStatement(Node):
    value: Node

@dataclass
class ExpressionStatement(Node):
    expression: Node

@dataclass
class Identifier(Node):
    name: str

@dataclass
class NumberLiteral(Node):
    value: float

@dataclass
class StringLiteral(Node):
    value: str

@dataclass
class BooleanLiteral(Node):
    value: bool

@dataclass
class FormulaLiteral(Node):
    value: str

@dataclass
class PropertyAccess(Node):
    receiver: Node
    property_name: str

@dataclass
class KeywordArgument(Node):
    name: str
    value: Node

@dataclass
class BinaryExpression(Node):
    left: Node
    operator: str
    right: Node

@dataclass
class CallExpression(Node):
    callee: Node
    arguments: List[Node]

@dataclass
class MethodCallExpression(Node):
    receiver: Node
    method_name: str
    arguments: List[Node]

@dataclass
class BorrowExpression(Node):
    target: Node
    mutable: bool

@dataclass
class BlockStatement(Node):
    statements: List[Node]

@dataclass
class DropExpression(Node):
    target: Node

@dataclass
class FunctionDef(Node):
    name: str
    parameters: List[tuple[str, Node]]
    return_type: Optional[Node]
    body: Node

@dataclass
class TypeAnnotation(Node):
    name: str
    generics: Optional[List[Node]] = None

@dataclass
class ResultType(Node):
    ok_type: Node
    err_type: Node
