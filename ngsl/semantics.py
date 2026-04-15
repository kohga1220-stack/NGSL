from __future__ import annotations
from typing import Dict, List, Optional, Tuple
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
from .errors import SemanticError

class SemanticType:
    def __init__(self, name: str, generics: Optional[Tuple[SemanticType, ...]] = None):
        self.name = name
        self.generics = generics or ()

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, SemanticType):
            return False
        return self.name == other.name and self.generics == other.generics

    def __repr__(self) -> str:
        if self.generics:
            inner = ', '.join(repr(g) for g in self.generics)
            return f"{self.name}[{inner}]"
        return self.name

class SemanticAnalyzer:
    def __init__(self):
        self.env: Dict[str, SemanticType] = {}
        self.moved_vars: Dict[str, bool] = {}
        self.immutable_borrow_count: Dict[str, int] = {}
        self.mutable_borrow: Dict[str, bool] = {}
        self.borrow_vars: Dict[str, tuple[str, bool]] = {}
        self.scope_stack: List[set[str]] = []
        self._current_statement_temporary_borrows: List[tuple[str, bool]] = []

    def analyze(self, program: Program) -> None:
        self.env.clear()
        self.moved_vars.clear()
        self.immutable_borrow_count.clear()
        self.mutable_borrow.clear()
        self.borrow_vars.clear()
        self.scope_stack.clear()
        self._enter_scope()
        self._initialize_builtins()
        for statement in program.statements:
            self._check_statement(statement)
        # Don't exit the global scope - keep variables in env for external access
        # self._exit_scope()

    def _initialize_builtins(self) -> None:
        # Result constructors
        self.env["Ok"] = SemanticType("Function")
        self.env["Err"] = SemanticType("Function")
        self.env["some_source"] = SemanticType("Vector", (SemanticType("Int"),))
        
        # Statistical functions - these are treated as built-in functions
        # Descriptive statistics
        self.env["mean"] = SemanticType("Function")      # mean(x: Vector[T]) -> Float
        self.env["var"] = SemanticType("Function")       # var(x: Vector[T]) -> Float
        self.env["sd"] = SemanticType("Function")        # sd(x: Vector[T]) -> Float (standard deviation)
        self.env["median"] = SemanticType("Function")    # median(x: Vector[T]) -> T
        self.env["min"] = SemanticType("Function")       # min(x: Vector[T]) -> T
        self.env["max"] = SemanticType("Function")       # max(x: Vector[T]) -> T
        self.env["sum"] = SemanticType("Function")       # sum(x: Vector[T]) -> T
        self.env["range"] = SemanticType("Function")     # range(min, max) -> Vector[Int]
        self.env["seq"] = SemanticType("Function")       # seq(from, to, by) -> Vector[Float]
        self.env["rep"] = SemanticType("Function")       # rep(x, times) -> Vector[T]
        self.env["c"] = SemanticType("Function")         # c(...) -> Vector[T]
        
        # Column statistics
        self.env["colMeans"] = SemanticType("Function")  # colMeans(x: Matrix/DataFrame) -> Vector[Float]
        self.env["colSums"] = SemanticType("Function")   # colSums(x: Matrix/DataFrame) -> Vector[T]
        self.env["rowMeans"] = SemanticType("Function")  # rowMeans(x: Matrix/DataFrame) -> Vector[Float]
        self.env["rowSums"] = SemanticType("Function")   # rowSums(x: Matrix/DataFrame) -> Vector[T]
        
        # Probability distributions
        self.env["dnorm"] = SemanticType("Function")     # dnorm(x, mean, sd) -> Float (density)
        self.env["pnorm"] = SemanticType("Function")     # pnorm(q, mean, sd) -> Float (CDF)
        self.env["qnorm"] = SemanticType("Function")     # qnorm(p, mean, sd) -> Float (quantile)
        self.env["rnorm"] = SemanticType("Function")     # rnorm(n, mean, sd) -> Vector[Float] (random)
        
        self.env["dunif"] = SemanticType("Function")     # dunif(x, min, max) -> Float (uniform density)
        self.env["punif"] = SemanticType("Function")     # punif(q, min, max) -> Float (uniform CDF)
        self.env["runif"] = SemanticType("Function")     # runif(n, min, max) -> Vector[Float] (uniform random)
        
        self.env["dbinom"] = SemanticType("Function")    # dbinom(x, size, prob) -> Float (binomial density)
        self.env["rbinom"] = SemanticType("Function")    # rbinom(n, size, prob) -> Vector[Int]
        
        # Matrix and data frame operations
        self.env["matrix"] = SemanticType("Function")    # matrix(data, nrow, ncol) -> Matrix[T]
        self.env["data.frame"] = SemanticType("Function")# data.frame(...) -> DataFrame
        self.env["read.csv"] = SemanticType("Function")  # read.csv(path) -> DataFrame
        self.env["write.csv"] = SemanticType("Function") # write.csv(df, path) -> Unit
        self.env["plot"] = SemanticType("Function")      # plot(x, y?) -> Unit
        self.env["t"] = SemanticType("Function")         # t(x: Matrix[T]) -> Matrix[T] (transpose)
        self.env["nrow"] = SemanticType("Function")      # nrow(x: Matrix/DataFrame) -> Int
        self.env["ncol"] = SemanticType("Function")      # ncol(x: Matrix/DataFrame) -> Int
        self.env["dim"] = SemanticType("Function")       # dim(x: Matrix/DataFrame) -> Vector[Int]
        
        # Linear regression and models
        self.env["lm"] = SemanticType("Function")        # lm(formula, data) -> LinearModel
        self.env["summary"] = SemanticType("Function")   # summary(x) -> Summary object
        self.env["predict"] = SemanticType("Function")   # predict(model, newdata) -> Vector[Float]
        
        # Unsupervised learning
        self.env["pca"] = SemanticType("Function")       # pca(data, k) -> PCA
        self.env["kmeans"] = SemanticType("Function")    # kmeans(data, k) -> KMeans
        self.env["glm"] = SemanticType("Function")       # glm(formula, data) -> GLMModel
        
        # Correlation and covariance
        self.env["cor"] = SemanticType("Function")       # cor(x, y) -> Float or cor(x) -> Matrix[Float]
        self.env["cov"] = SemanticType("Function")       # cov(x, y) -> Float or cov(x) -> Matrix[Float]
        
        # Matrix algebra
        self.env["solve"] = SemanticType("Function")     # solve(a, b) -> Vector[Float] (linear system)
        self.env["det"] = SemanticType("Function")       # det(x: Matrix[Float]) -> Float (determinant)
        self.env["inv"] = SemanticType("Function")       # inv(x: Matrix[Float]) -> Matrix[Float] (inverse)

    def _check_statement(self, statement) -> None:
        self._current_statement_temporary_borrows = []
        try:
            if isinstance(statement, LetStatement):
                self._check_let(statement)
            elif isinstance(statement, ReturnStatement):
                self._check_return(statement)
            elif isinstance(statement, ExpressionStatement):
                self._check_expression(statement.expression)
            elif isinstance(statement, BlockStatement):
                self._enter_scope()
                for sub in statement.statements:
                    self._check_statement(sub)
                self._exit_scope()
            else:
                raise SemanticError(f"Unknown statement type: {type(statement).__name__}")
        finally:
            self._release_temporary_borrows()

    def _check_let(self, statement: LetStatement) -> None:
        if statement.name in self.env and self.moved_vars.get(statement.name, False):
            raise SemanticError(f"Variable '{statement.name}' was moved and cannot be reassigned")
        if statement.name in self.env and self._is_borrowed(statement.name):
            raise SemanticError(f"Variable '{statement.name}' is borrowed and cannot be reassigned")
        if isinstance(statement.value, Identifier) and self._is_borrowed(statement.value.name):
            raise SemanticError(f"Cannot move borrowed value '{statement.value.name}'")
        value_type = self._check_expression(statement.value)
        declared_type = None
        if statement.type_annotation is not None:
            declared_type = self._resolve_type_annotation(statement.type_annotation)
            if declared_type != value_type and not self._is_compatible_type(declared_type, value_type):
                raise SemanticError(
                    f"Type mismatch for '{statement.name}': declared {declared_type}, got {value_type}"
                )
        else:
            declared_type = value_type
        self.env[statement.name] = declared_type
        self.scope_stack[-1].add(statement.name)
        if isinstance(statement.value, Identifier) and not self._is_copy_type(value_type):
            self.moved_vars[statement.value.name] = True
        if isinstance(statement.value, BorrowExpression) and isinstance(statement.value.target, Identifier):
            target_name = statement.value.target.name
            self._register_borrow_variable(statement.name, target_name, statement.value.mutable)

    def _check_return(self, statement: ReturnStatement) -> None:
        self._check_expression(statement.value)

    def _check_expression(self, expression):
        if isinstance(expression, Identifier):
            return self._check_identifier(expression)
        if isinstance(expression, NumberLiteral):
            return SemanticType("Float") if isinstance(expression.value, float) else SemanticType("Int")
        if isinstance(expression, BooleanLiteral):
            return SemanticType("Bool")
        if isinstance(expression, StringLiteral):
            return SemanticType("String")
        if isinstance(expression, FormulaLiteral):
            return SemanticType("Formula")
        if isinstance(expression, BinaryExpression):
            return self._check_binary(expression)
        if isinstance(expression, CallExpression):
            return self._check_call(expression)
        if isinstance(expression, MethodCallExpression):
            return self._check_method_call(expression)
        if isinstance(expression, PropertyAccess):
            return self._check_property_access(expression)
        if isinstance(expression, KeywordArgument):
            return self._check_expression(expression.value)
        if isinstance(expression, BorrowExpression):
            return self._check_borrow(expression)
        if isinstance(expression, DropExpression):
            return self._check_drop(expression)
        raise SemanticError(f"Unsupported expression type: {type(expression).__name__}")

    def _check_identifier(self, identifier: Identifier) -> SemanticType:
        if identifier.name not in self.env:
            raise SemanticError(f"Undefined variable '{identifier.name}'")
        if self.moved_vars.get(identifier.name, False):
            raise SemanticError(f"Use of moved variable '{identifier.name}'")
        return self.env[identifier.name]

    def _check_binary(self, expression: BinaryExpression) -> SemanticType:
        left_type = self._check_expression(expression.left)
        right_type = self._check_expression(expression.right)
        operator = expression.operator
        if operator in "+-*/":
            # Vector-Vector operations
            if left_type.name == "Vector" and right_type.name == "Vector":
                return left_type  # Return same vector type
            # Vector-Scalar operations
            if left_type.name == "Vector" and self._is_numeric_type(right_type):
                return left_type
            if self._is_numeric_type(left_type) and right_type.name == "Vector":
                return right_type
            # Matrix-Matrix operations
            if left_type.name == "Matrix" and right_type.name == "Matrix":
                return left_type  # Return same matrix type
            # Matrix-Scalar operations
            if left_type.name == "Matrix" and self._is_numeric_type(right_type):
                return left_type
            if self._is_numeric_type(left_type) and right_type.name == "Matrix":
                return right_type
            # Numeric operations
            if self._is_numeric_type(left_type) and self._is_numeric_type(right_type):
                if left_type == right_type:
                    return left_type
                return SemanticType("Float")
            if operator == "+" and left_type.name == "String" and right_type.name == "String":
                return left_type
            raise SemanticError(
                f"Invalid binary operation: {left_type} {operator} {right_type}"
            )
        raise SemanticError(f"Unknown binary operator '{operator}'")

    def _check_call(self, expression: CallExpression) -> SemanticType:
        callee_type = self._check_expression(expression.callee)
        arg_types = [self._check_expression(arg) for arg in expression.arguments]
        
        if isinstance(expression.callee, Identifier):
            func_name = expression.callee.name
            
            # Result constructors
            if func_name == "Ok" and len(arg_types) == 1:
                return SemanticType("Result", (arg_types[0], SemanticType("Unknown")))
            if func_name == "Err" and len(arg_types) == 1:
                return SemanticType("Result", (SemanticType("Unknown"), arg_types[0]))
            
            # Descriptive statistics - return Float
            if func_name in {"mean", "var", "sd"} and len(arg_types) == 1:
                if arg_types[0].name == "Vector":
                    return SemanticType("Float")
                if arg_types[0].name == "Matrix":
                    return SemanticType("Vector", (SemanticType("Float"),))
            
            # Aggregate functions
            if func_name in {"median", "min", "max", "sum"} and len(arg_types) == 1:
                if arg_types[0].name == "Vector" and arg_types[0].generics:
                    return arg_types[0].generics[0]  # Return element type
            
            # Vector construction
            if func_name == "c":  # c(1, 2, 3, ...) infer type from first arg
                if arg_types:
                    return SemanticType("Vector", (arg_types[0],))
                return SemanticType("Vector", (SemanticType("Unknown"),))
            
            if func_name == "rep" and len(arg_types) >= 2:  # rep(x, times)
                return SemanticType("Vector", (arg_types[0],))
            
            if func_name == "seq" and len(arg_types) >= 2:  # seq(from, to, by)
                return SemanticType("Vector", (SemanticType("Float"),))
            
            if func_name == "range" and len(arg_types) == 2:  # range(min, max)
                return SemanticType("Vector", (SemanticType("Int"),))
            
            # Column/Row operations
            if func_name in {"colMeans", "rowMeans"} and len(arg_types) == 1:
                return SemanticType("Vector", (SemanticType("Float"),))
            
            if func_name in {"colSums", "rowSums"} and len(arg_types) == 1:
                if arg_types[0].name in {"Matrix", "DataFrame"} and arg_types[0].generics:
                    elem_type = arg_types[0].generics[0]
                else:
                    elem_type = SemanticType("Unknown")
                return SemanticType("Vector", (elem_type,))
            
            # Probability distribution functions - mostly return Float
            if func_name in {"dnorm", "pnorm", "qnorm", "dunif", "punif", "dbinom"}:
                return SemanticType("Float")
            
            if func_name in {"rnorm", "runif"} and len(arg_types) >= 1:  # rnorm(n, mean, sd)
                return SemanticType("Vector", (SemanticType("Float"),))
            
            if func_name == "rbinom" and len(arg_types) >= 1:
                return SemanticType("Vector", (SemanticType("Int"),))
            
            # Matrix operations (including dotted names like "data.frame")
            if func_name == "matrix" and len(arg_types) >= 1:
                # matrix(data, nrow, ncol) - extract element type from first arg
                if arg_types[0].name == "Vector" and arg_types[0].generics:
                    elem_type = arg_types[0].generics[0]
                else:
                    elem_type = arg_types[0]  # Default to the type of first argument
                return SemanticType("Matrix", (elem_type,))
            
            if func_name == "data.frame" and len(arg_types) >= 1:
                return SemanticType("DataFrame", (arg_types[0],))
            
            if func_name == "read.csv" and len(arg_types) >= 1:
                return SemanticType("DataFrame", (SemanticType("Unknown"),))
            if func_name == "write.csv" and len(arg_types) >= 2:
                return SemanticType("Unit")
            if func_name == "plot":
                return SemanticType("Unit")
            if func_name == "t" and len(arg_types) == 1:
                return SemanticType("Matrix", (arg_types[0].generics[0] if arg_types[0].generics else SemanticType("Unknown"),))
            if func_name in {"nrow", "ncol"} and len(arg_types) == 1:
                return SemanticType("Int")
            if func_name == "dim" and len(arg_types) == 1:
                return SemanticType("Vector", (SemanticType("Int"),))
            
            if func_name == "lm":  # lm(formula, data)
                return SemanticType("LinearModel")
            if func_name == "glm":
                return SemanticType("GLMModel")
            if func_name == "summary":
                return SemanticType("String")
            if func_name == "predict" and len(arg_types) >= 1 and arg_types[0].name in {"GLMModel", "LinearModel"}:
                return SemanticType("Vector", (SemanticType("Float"),))
            if func_name == "pca":
                return SemanticType("PCA")
            if func_name == "kmeans":
                return SemanticType("KMeans")
            
            if func_name in {"cor", "cov"}:
                if len(arg_types) == 2:
                    return SemanticType("Float")  # cor(x, y) -> Float
                elif len(arg_types) == 1 and arg_types[0].name in {"Matrix", "DataFrame"}:
                    return SemanticType("Matrix", (SemanticType("Float"),))  # cor(matrix) -> Matrix[Float]
            
            if func_name == "solve" and len(arg_types) >= 2:
                return SemanticType("Vector", (SemanticType("Float"),))
            
            if func_name == "det" and len(arg_types) == 1:
                return SemanticType("Float")
            if func_name == "inv" and len(arg_types) == 1 and arg_types[0].name == "Matrix":
                return arg_types[0]  # Same dimension matrix
        
        return callee_type

    def _check_borrow(self, expression: BorrowExpression) -> SemanticType:
        target_type = self._check_expression(expression.target)
        if isinstance(expression.target, Identifier):
            name = expression.target.name
            if self.moved_vars.get(name, False):
                raise SemanticError(f"Cannot borrow moved variable '{name}'")
            if expression.mutable:
                if self._has_immutable_borrows(name) > 0 or self.mutable_borrow.get(name, False):
                    raise SemanticError(f"Cannot create mutable borrow of '{name}' while it is already borrowed")
                self.mutable_borrow[name] = True
            else:
                if self.mutable_borrow.get(name, False):
                    raise SemanticError(f"Cannot create immutable borrow of '{name}' while it is mutably borrowed")
                self.immutable_borrow_count[name] = self._has_immutable_borrows(name) + 1
            self._current_statement_temporary_borrows.append((name, expression.mutable))
        return SemanticType("MutRef", (target_type,)) if expression.mutable else SemanticType("Ref", (target_type,))

    def _check_drop(self, expression: DropExpression) -> SemanticType:
        if isinstance(expression.target, Identifier):
            name = expression.target.name
            if name not in self.env:
                raise SemanticError(f"Cannot drop undefined variable '{name}'")
            if self.moved_vars.get(name, False):
                raise SemanticError(f"Cannot drop already moved variable '{name}'")
            target_type = self.env[name]
            if name in self.borrow_vars:
                source_name, mutable = self.borrow_vars.pop(name)
                self._decrement_borrow(source_name, mutable)
            elif self._is_borrowed(name):
                raise SemanticError(f"Cannot drop borrowed variable '{name}'")
            self.env.pop(name, None)
            self.moved_vars[name] = True
            return SemanticType("Unit")
        raise SemanticError("Drop target must be a variable")

    def _check_method_call(self, expression: MethodCallExpression) -> SemanticType:
        # Check if receiver is defined; if not, treat as a function call with dotted name
        if isinstance(expression.receiver, Identifier) and expression.receiver.name not in self.env:
            func_name = f"{expression.receiver.name}.{expression.method_name}"
            from .ast import CallExpression
            synth_call = CallExpression(
                callee=Identifier(name=func_name),
                arguments=expression.arguments
            )
            return self._check_call(synth_call)
        
        # Normal method call processing
        receiver_type = self._check_expression(expression.receiver)
        for arg in expression.arguments:
            self._check_expression(arg)
        if receiver_type.name == "Vector" and receiver_type.generics:
            method = expression.method_name
            if method in {"filter", "map", "sort", "reverse"}:
                return receiver_type
            if method == "sum":
                return receiver_type.generics[0]
            if method == "mean":
                return SemanticType("Float")
            if method == "len":
                return SemanticType("Int")
        return receiver_type

    def _check_property_access(self, expression: PropertyAccess) -> SemanticType:
        receiver_type = self._check_expression(expression.receiver)
        if receiver_type.name == "DataFrame":
            return SemanticType("Vector", (SemanticType("Unknown"),))
        raise SemanticError(f"Property access not supported for {receiver_type}")

    def _resolve_type_annotation(self, annotation):
        if isinstance(annotation, TypeAnnotation):
            generics = tuple(self._resolve_type_annotation(g) for g in annotation.generics or [])
            return SemanticType(annotation.name, generics)
        if isinstance(annotation, ResultType):
            ok_type = self._resolve_type_annotation(annotation.ok_type)
            err_type = self._resolve_type_annotation(annotation.err_type)
            return SemanticType("Result", (ok_type, err_type))
        raise SemanticError("Unsupported type annotation")

    def _is_compatible_type(self, declared: SemanticType, inferred: SemanticType) -> bool:
        if declared == inferred:
            return True
        if declared.name == "Result" and inferred.name == "Result" and len(declared.generics) == 2 and len(inferred.generics) == 2:
            declared_ok, declared_err = declared.generics
            inferred_ok, inferred_err = inferred.generics
            if inferred_ok.name == "Unknown" and declared_err == inferred_err:
                return True
            if inferred_err.name == "Unknown" and declared_ok == inferred_ok:
                return True
        return False

    def _has_immutable_borrows(self, name: str) -> int:
        return self.immutable_borrow_count.get(name, 0)

    def _is_borrowed(self, name: str) -> bool:
        return self._has_immutable_borrows(name) > 0 or self.mutable_borrow.get(name, False)

    def _enter_scope(self) -> None:
        self.scope_stack.append(set())

    def _exit_scope(self) -> None:
        if not self.scope_stack:
            return
        scope_vars = self.scope_stack.pop()
        for name in list(scope_vars):
            self.env.pop(name, None)
            self.moved_vars.pop(name, None)
            if name in self.borrow_vars:
                target_name, mutable = self.borrow_vars.pop(name)
                self._decrement_borrow(target_name, mutable)

    def _register_borrow_variable(self, name: str, target: str, mutable: bool) -> None:
        self.borrow_vars[name] = (target, mutable)
        try:
            self._current_statement_temporary_borrows.remove((target, mutable))
        except ValueError:
            pass

    def _decrement_borrow(self, target: str, mutable: bool) -> None:
        if mutable:
            self.mutable_borrow[target] = False
        else:
            self.immutable_borrow_count[target] = max(0, self._has_immutable_borrows(target) - 1)

    def _release_temporary_borrows(self) -> None:
        for target, mutable in self._current_statement_temporary_borrows:
            self._decrement_borrow(target, mutable)
        self._current_statement_temporary_borrows = []

    def _is_numeric_type(self, semantic_type: SemanticType) -> bool:
        return semantic_type.name in {"Int", "Float"}

    def _is_copy_type(self, semantic_type: SemanticType) -> bool:
        if semantic_type.name in {"Int", "Float", "Bool"}:
            return True
        if semantic_type.name in {"Ref", "MutRef"}:
            return True
        return False
