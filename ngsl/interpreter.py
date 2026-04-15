"""
NGSL Interpreter - Evaluates AST with NumPy/SciPy for fast numerical operations
"""

import csv
import os
import uuid
import numpy as np
from scipy import stats
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from .ast import (
    BooleanLiteral,
    BlockStatement,
    BorrowExpression,
    BinaryExpression,
    CallExpression,
    DropExpression,
    ExpressionStatement,
    FormulaLiteral,
    Identifier,
    KeywordArgument,
    LetStatement,
    MethodCallExpression,
    NumberLiteral,
    PropertyAccess,
    ReturnStatement,
    StringLiteral,
)

try:
    import matplotlib
    matplotlib.use('Agg')
    from matplotlib import pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    plt = None
    MATPLOTLIB_AVAILABLE = False
from .errors import SemanticError

@dataclass
class NGSLValue:
    """Wrapper for NGSL runtime values"""
    type_name: str  # 'Int', 'Float', 'String', 'Vector', 'Matrix', 'DataFrame', etc.
    data: Any       # The actual Python/NumPy value
    
    def __repr__(self) -> str:
        if self.type_name == 'Vector':
            return f"Vector({list(self.data)})"
        elif self.type_name == 'Matrix':
            return f"Matrix\n{self.data}"
        elif self.type_name == 'DataFrame':
            return f"DataFrame\n{self.data}"
        else:
            return f"{self.type_name}({self.data})"

@dataclass
class NGSLDataFrame:
    columns: List[str]
    data: Dict[str, np.ndarray]

    def to_rows(self):
        rows = []
        keys = self.columns
        n = len(self.data[keys[0]]) if keys else 0
        for i in range(n):
            rows.append({k: self.data[k][i] for k in keys})
        return rows

    def __repr__(self) -> str:
        cols = ', '.join(self.columns)
        return f"DataFrame(columns=[{cols}], rows={len(self.data[self.columns[0]]) if self.columns else 0})"

@dataclass
class GLMModel:
    coefficients: np.ndarray
    intercept: float
    formula: str
    feature_names: List[str]

@dataclass
class PCAResult:
    components: np.ndarray
    explained_variance: np.ndarray
    mean: np.ndarray

@dataclass
class KMeansResult:
    centroids: np.ndarray
    labels: np.ndarray

class NGSLInterpreter:
    """Interprets and evaluates NGSL programs with NumPy/SciPy backend"""
    
    def __init__(self):
        self.env: Dict[str, NGSLValue] = {}
        self.scope_stack: List[Dict[str, NGSLValue]] = []
    
    def interpret(self, program: Program) -> None:
        """Execute NGSL program"""
        self.env.clear()
        self.scope_stack.clear()
        self._initialize_builtins()
        
        for statement in program.statements:
            self._eval_statement(statement)
    
    def _initialize_builtins(self) -> None:
        """Initialize built-in functions as callable objects"""
        pass  # Built-ins are handled via function dispatch
    
    def _eval_statement(self, statement) -> Any:
        """Evaluate a statement"""
        if isinstance(statement, LetStatement):
            return self._eval_let(statement)
        elif isinstance(statement, ReturnStatement):
            return self._eval_return(statement)
        elif isinstance(statement, ExpressionStatement):
            return self._eval_expression(statement.expression)
        elif isinstance(statement, BlockStatement):
            self.scope_stack.append({})
            for sub in statement.statements:
                self._eval_statement(sub)
            self.scope_stack.pop()
        else:
            raise SemanticError(f"Unknown statement: {type(statement).__name__}")
    
    def _eval_let(self, statement: LetStatement) -> None:
        """Evaluate variable assignment"""
        value = self._eval_expression(statement.value)
        self.env[statement.name] = value
    
    def _eval_return(self, statement: ReturnStatement) -> Any:
        """Evaluate return statement"""
        return self._eval_expression(statement.value)
    
    def _eval_expression(self, expr) -> NGSLValue:
        """Evaluate an expression"""
        if isinstance(expr, NumberLiteral):
            value = expr.value
            type_name = 'Float' if isinstance(value, float) else 'Int'
            return NGSLValue(type_name, value)
        
        elif isinstance(expr, BooleanLiteral):
            return NGSLValue('Bool', expr.value)
        
        elif isinstance(expr, StringLiteral):
            return NGSLValue('String', expr.value)
        elif isinstance(expr, FormulaLiteral):
            return NGSLValue('Formula', expr.value)
        
        elif isinstance(expr, Identifier):
            if expr.name not in self.env:
                raise SemanticError(f"Undefined variable: {expr.name}")
            return self.env[expr.name]
        
        elif isinstance(expr, BinaryExpression):
            return self._eval_binary(expr)
        
        elif isinstance(expr, CallExpression):
            return self._eval_call(expr)
        
        elif isinstance(expr, MethodCallExpression):
            return self._eval_method_call(expr)
        
        elif isinstance(expr, PropertyAccess):
            receiver = self._eval_expression(expr.receiver)
            if receiver.type_name == 'DataFrame' and isinstance(receiver.data, NGSLDataFrame):
                if expr.property_name not in receiver.data.columns:
                    raise SemanticError(f"Column '{expr.property_name}' not found in data.frame")
                return NGSLValue('Vector', receiver.data.data[expr.property_name])
            raise SemanticError(f"Property access not supported for '{receiver.type_name}'")
        
        elif isinstance(expr, KeywordArgument):
            raise SemanticError("Unexpected keyword argument outside of function call")
        
        elif isinstance(expr, BorrowExpression):
            # Borrows are no-op in interpreter; just return the borrowed value
            return self._eval_expression(expr.target)
        
        elif isinstance(expr, DropExpression):
            # Drops are no-op in interpreter
            return NGSLValue('Unit', None)
        
        else:
            raise SemanticError(f"Unknown expression: {type(expr).__name__}")
    
    def _extract_call_arguments(self, arguments: List[Any]) -> tuple[list[NGSLValue], Dict[str, NGSLValue]]:
        positional_args: list[NGSLValue] = []
        keyword_args: Dict[str, NGSLValue] = {}
        for arg in arguments:
            if isinstance(arg, KeywordArgument):
                keyword_args[arg.name] = self._eval_expression(arg.value)
            else:
                positional_args.append(self._eval_expression(arg))
        return positional_args, keyword_args

    def _broadcast_vector_arrays(self, left_array: np.ndarray, right_array: np.ndarray):
        if left_array.shape == right_array.shape:
            return left_array, right_array
        if left_array.ndim == 1 and right_array.ndim == 1:
            len_l = len(left_array)
            len_r = len(right_array)
            if len_l == 1:
                return np.full(len_r, left_array[0]), right_array
            if len_r == 1:
                return left_array, np.full(len_l, right_array[0])
            if len_r % len_l == 0:
                return np.tile(left_array, len_r // len_l), right_array
            if len_l % len_r == 0:
                return left_array, np.tile(right_array, len_l // len_r)
            raise SemanticError(
                f"Vector lengths are not compatible for recycling: {len_l} and {len_r}"
            )
        return np.broadcast_arrays(left_array, right_array)

    def _eval_binary(self, expr: BinaryExpression) -> NGSLValue:
        """Evaluate binary operations"""
        left = self._eval_expression(expr.left)
        right = self._eval_expression(expr.right)
        op = expr.operator
        
        if op == '+':
            if left.type_name == 'Vector' and right.type_name == 'Vector':
                left_arr, right_arr = self._broadcast_vector_arrays(np.array(left.data), np.array(right.data))
                return NGSLValue('Vector', left_arr + right_arr)
            elif left.type_name == 'Vector' and right.type_name in ('Float', 'Int'):
                return NGSLValue('Vector', np.array(left.data) + right.data)
            elif left.type_name in ('Float', 'Int') and right.type_name == 'Vector':
                return NGSLValue('Vector', left.data + np.array(right.data))
            elif left.type_name == 'Matrix' and right.type_name == 'Matrix':
                return NGSLValue('Matrix', left.data + right.data)
            elif left.type_name == 'Matrix' and right.type_name in ('Float', 'Int'):
                return NGSLValue('Matrix', left.data + right.data)
            elif left.type_name in ('Float', 'Int') and right.type_name == 'Matrix':
                return NGSLValue('Matrix', left.data + right.data)
            else:
                return NGSLValue('Float' if isinstance(left.data + right.data, float) else 'Int',
                               left.data + right.data)
        
        elif op == '-':
            if left.type_name == 'Vector' and right.type_name == 'Vector':
                left_arr, right_arr = self._broadcast_vector_arrays(np.array(left.data), np.array(right.data))
                return NGSLValue('Vector', left_arr - right_arr)
            elif left.type_name == 'Vector' and right.type_name in ('Float', 'Int'):
                return NGSLValue('Vector', np.array(left.data) - right.data)
            elif left.type_name in ('Float', 'Int') and right.type_name == 'Vector':
                return NGSLValue('Vector', left.data - np.array(right.data))
            elif left.type_name == 'Matrix' and right.type_name == 'Matrix':
                return NGSLValue('Matrix', left.data - right.data)
            elif left.type_name == 'Matrix' and right.type_name in ('Float', 'Int'):
                return NGSLValue('Matrix', left.data - right.data)
            elif left.type_name in ('Float', 'Int') and right.type_name == 'Matrix':
                return NGSLValue('Matrix', left.data - right.data)
            else:
                return NGSLValue('Float' if isinstance(left.data - right.data, float) else 'Int',
                               left.data - right.data)
        
        elif op == '*':
            if left.type_name == 'Vector' and right.type_name == 'Vector':
                left_arr, right_arr = self._broadcast_vector_arrays(np.array(left.data), np.array(right.data))
                return NGSLValue('Vector', left_arr * right_arr)
            elif left.type_name == 'Vector' and right.type_name in ('Float', 'Int'):
                return NGSLValue('Vector', np.array(left.data) * right.data)
            elif left.type_name in ('Float', 'Int') and right.type_name == 'Vector':
                return NGSLValue('Vector', left.data * np.array(right.data))
            elif left.type_name == 'Matrix' and right.type_name == 'Matrix':
                # Matrix multiplication using BLAS
                return NGSLValue('Matrix', np.matmul(left.data, right.data))
            elif left.type_name == 'Matrix' and right.type_name in ('Float', 'Int'):
                return NGSLValue('Matrix', left.data * right.data)
            elif left.type_name in ('Float', 'Int') and right.type_name == 'Matrix':
                return NGSLValue('Matrix', left.data * right.data)
            else:
                return NGSLValue('Float' if isinstance(left.data * right.data, float) else 'Int',
                               left.data * right.data)
        
        elif op == '/':
            if left.type_name == 'Vector' and right.type_name == 'Vector':
                left_arr, right_arr = self._broadcast_vector_arrays(np.array(left.data), np.array(right.data))
                return NGSLValue('Vector', left_arr / right_arr)
            elif left.type_name == 'Vector' and right.type_name in ('Float', 'Int'):
                return NGSLValue('Vector', np.array(left.data) / right.data)
            elif left.type_name in ('Float', 'Int') and right.type_name == 'Vector':
                return NGSLValue('Vector', left.data / np.array(right.data))
            elif left.type_name == 'Matrix' and right.type_name == 'Matrix':
                # Matrix division (element-wise)
                return NGSLValue('Matrix', left.data / right.data)
            elif left.type_name == 'Matrix' and right.type_name in ('Float', 'Int'):
                return NGSLValue('Matrix', left.data / right.data)
            elif left.type_name in ('Float', 'Int') and right.type_name == 'Matrix':
                return NGSLValue('Matrix', left.data / right.data)
            else:
                return NGSLValue('Float', left.data / right.data)
        
        else:
            raise SemanticError(f"Unknown operator: {op}")
    
    def _eval_call(self, expr: CallExpression) -> NGSLValue:
        """Evaluate function calls"""
        if not isinstance(expr.callee, Identifier):
            raise SemanticError("Function must be an identifier")
        
        func_name = expr.callee.name
        args, kwargs = self._extract_call_arguments(expr.arguments)
        
        # Vector construction
        if func_name == 'c':
            values = [arg.data for arg in args]
            arr = np.array(values)
            return NGSLValue('Vector', arr)
        
        # Sequence generation
        if func_name == 'seq':
            if len(args) < 2:
                raise SemanticError("seq requires at least 2 arguments")
            start = args[0].data
            end = args[1].data
            by = args[2].data if len(args) > 2 else 1.0
            seq_array = np.arange(start, end + by, by)
            return NGSLValue('Vector', seq_array)
        
        if func_name == 'range':
            if len(args) != 2:
                raise SemanticError("range requires 2 arguments")
            start = int(args[0].data)
            end = int(args[1].data)
            return NGSLValue('Vector', np.arange(start, end + 1))
        
        # Repetition
        if func_name == 'rep':
            if len(args) < 2:
                raise SemanticError("rep requires at least 2 arguments")
            value = args[0].data
            times = int(args[1].data)
            return NGSLValue('Vector', np.repeat(value, times))
        
        # Descriptive statistics
        if func_name == 'mean':
            if len(args) != 1:
                raise SemanticError("mean requires 1 argument")
            data = args[0].data
            if isinstance(data, np.ndarray):
                return NGSLValue('Float', float(np.mean(data)))
            else:
                return NGSLValue('Float', float(data))
        
        if func_name == 'var':
            if len(args) != 1:
                raise SemanticError("var requires 1 argument")
            data = args[0].data
            if isinstance(data, np.ndarray):
                return NGSLValue('Float', float(np.var(data)))
            else:
                return NGSLValue('Float', 0.0)
        
        if func_name == 'sd':
            if len(args) != 1:
                raise SemanticError("sd requires 1 argument")
            data = args[0].data
            if isinstance(data, np.ndarray):
                return NGSLValue('Float', float(np.std(data)))
            else:
                return NGSLValue('Float', 0.0)
        
        if func_name == 'median':
            if len(args) != 1:
                raise SemanticError("median requires 1 argument")
            data = args[0].data
            if isinstance(data, np.ndarray):
                result = float(np.median(data))
                return NGSLValue('Float', result)
            else:
                return NGSLValue('Float', float(data))
        
        if func_name in {'min', 'max'}:
            if len(args) != 1:
                raise SemanticError(f"{func_name} requires 1 argument")
            data = args[0].data
            if isinstance(data, np.ndarray):
                result = float(np.min(data) if func_name == 'min' else np.max(data))
                return NGSLValue('Float', result)
            else:
                return NGSLValue('Float', float(data))
        
        if func_name == 'sum':
            if len(args) != 1:
                raise SemanticError("sum requires 1 argument")
            data = args[0].data
            if isinstance(data, np.ndarray):
                result = float(np.sum(data))
                return NGSLValue('Float', result)
            else:
                return NGSLValue('Float', float(data))
        
        # Distributions (normal)
        if func_name == 'dnorm':
            if len(args) < 1:
                raise SemanticError("dnorm requires at least 1 argument")
            x = args[0].data
            mean = args[1].data if len(args) > 1 else 0.0
            sd = args[2].data if len(args) > 2 else 1.0
            result = float(stats.norm.pdf(x, mean, sd))
            return NGSLValue('Float', result)
        
        if func_name == 'pnorm':
            if len(args) < 1:
                raise SemanticError("pnorm requires at least 1 argument")
            q = args[0].data
            mean = args[1].data if len(args) > 1 else 0.0
            sd = args[2].data if len(args) > 2 else 1.0
            result = float(stats.norm.cdf(q, mean, sd))
            return NGSLValue('Float', result)
        
        if func_name == 'qnorm':
            if len(args) < 1:
                raise SemanticError("qnorm requires at least 1 argument")
            p = args[0].data
            mean = args[1].data if len(args) > 1 else 0.0
            sd = args[2].data if len(args) > 2 else 1.0
            result = float(stats.norm.ppf(p, mean, sd))
            return NGSLValue('Float', result)
        
        if func_name == 'rnorm':
            if len(args) < 1:
                raise SemanticError("rnorm requires at least 1 argument")
            n = int(args[0].data)
            mean = args[1].data if len(args) > 1 else 0.0
            sd = args[2].data if len(args) > 2 else 1.0
            result = np.random.normal(mean, sd, n)
            return NGSLValue('Vector', result)
        
        # Uniform distribution
        if func_name == 'runif':
            if len(args) < 1:
                raise SemanticError("runif requires at least 1 argument")
            n = int(args[0].data)
            min_val = args[1].data if len(args) > 1 else 0.0
            max_val = args[2].data if len(args) > 2 else 1.0
            result = np.random.uniform(min_val, max_val, n)
            return NGSLValue('Vector', result)
        
        # Matrix operations
        if func_name == 'matrix':
            if len(args) < 3:
                raise SemanticError("matrix requires at least 3 arguments")
            data = args[0].data
            nrow = int(args[1].data)
            ncol = int(args[2].data)
            if isinstance(data, np.ndarray):
                matrix = data.reshape((nrow, ncol))
            else:
                matrix = np.array([data] * (nrow * ncol)).reshape((nrow, ncol))
            return NGSLValue('Matrix', matrix)
        
        if func_name == 'data.frame':
            if len(args) == 0:
                return NGSLValue('DataFrame', NGSLDataFrame([], {}))
            columns: List[str] = []
            frame_data: Dict[str, np.ndarray] = {}
            max_length = 0

            for index, arg in enumerate(args):
                col_name = f"V{index + 1}"
                value = arg.data
                if isinstance(value, np.ndarray):
                    if value.ndim != 1:
                        raise SemanticError("data.frame columns must be vectors")
                    array = value
                else:
                    array = np.array([value])
                max_length = max(max_length, len(array))
                columns.append(col_name)
                frame_data[col_name] = array

            for col_name, array in frame_data.items():
                if len(array) != max_length:
                    if len(array) == 1:
                        frame_data[col_name] = np.repeat(array[0], max_length)
                    else:
                        raise SemanticError("data.frame columns must have equal length")

            return NGSLValue('DataFrame', NGSLDataFrame(columns, frame_data))

        if func_name == 'read.csv':
            if len(args) != 1:
                raise SemanticError("read.csv requires exactly 1 positional argument")
            path = args[0].data
            if not isinstance(path, str):
                raise SemanticError("read.csv requires a string file path")
            if not os.path.exists(path):
                raise SemanticError(f"File does not exist: {path}")
            header = True
            sep = ','
            if 'header' in kwargs:
                header_value = kwargs['header']
                if header_value.type_name != 'Bool':
                    raise SemanticError("read.csv header must be a Bool")
                header = header_value.data
            if 'sep' in kwargs:
                sep_value = kwargs['sep']
                if sep_value.type_name != 'String':
                    raise SemanticError("read.csv sep must be a String")
                sep = sep_value.data
            if 'row.names' in kwargs:
                row_names_value = kwargs['row.names']
                if row_names_value.type_name != 'Bool':
                    raise SemanticError("read.csv row.names must be a Bool")
                # currently ignore row names and keep default numeric indexing
                _ = row_names_value.data
            with open(path, newline='') as csvfile:
                if header:
                    reader = csv.DictReader(csvfile, delimiter=sep)
                    columns = reader.fieldnames or []
                    data: Dict[str, np.ndarray] = {col: [] for col in columns}
                    for row in reader:
                        for col in columns:
                            cell = row[col]
                            if cell is None or cell == '':
                                data[col].append(None)
                                continue
                            try:
                                if '.' in cell:
                                    data[col].append(float(cell))
                                else:
                                    data[col].append(int(cell))
                            except ValueError:
                                data[col].append(cell)
                else:
                    reader = csv.reader(csvfile, delimiter=sep)
                    rows = list(reader)
                    if not rows:
                        columns = []
                        data = {}
                    else:
                        num_cols = len(rows[0])
                        columns = [f"V{i+1}" for i in range(num_cols)]
                        data = {col: [] for col in columns}
                        for row in rows:
                            for idx, col in enumerate(columns):
                                cell = row[idx] if idx < len(row) else ''
                                if cell == '':
                                    data[col].append(None)
                                    continue
                                try:
                                    if '.' in cell:
                                        data[col].append(float(cell))
                                    else:
                                        data[col].append(int(cell))
                                except ValueError:
                                    data[col].append(cell)
                for col in columns:
                    data[col] = np.array(data[col], dtype=object)
            return NGSLValue('DataFrame', NGSLDataFrame(columns, data))

        if func_name == 'write.csv':
            if len(args) != 2:
                raise SemanticError("write.csv requires exactly 2 positional arguments")
            df_value = args[0]
            path = args[1].data
            if not isinstance(path, str):
                raise SemanticError("write.csv requires a string file path")
            sep = ','
            row_names = False
            if 'sep' in kwargs:
                sep_value = kwargs['sep']
                if sep_value.type_name != 'String':
                    raise SemanticError("write.csv sep must be a String")
                sep = sep_value.data
            if 'row_names' in kwargs:
                row_names_value = kwargs['row_names']
                if row_names_value.type_name != 'Bool':
                    raise SemanticError("write.csv row_names must be a Bool")
                row_names = row_names_value.data
            if 'row.names' in kwargs:
                row_names_value = kwargs['row.names']
                if row_names_value.type_name != 'Bool':
                    raise SemanticError("write.csv row.names must be a Bool")
                row_names = row_names_value.data
            if df_value.type_name == 'DataFrame' and isinstance(df_value.data, NGSLDataFrame):
                columns = df_value.data.columns
                rows = df_value.data.to_rows()
                fieldnames = ['row.names'] + columns if row_names else columns
                with open(path, 'w', newline='') as csvfile:
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=sep)
                    writer.writeheader()
                    for row_index, row in enumerate(rows):
                        out_row = {k: ('' if v is None else v) for k, v in row.items()}
                        if row_names:
                            out_row = {'row.names': row_index + 1, **out_row}
                        writer.writerow(out_row)
                return NGSLValue('Unit', None)
            raise SemanticError('write.csv requires a DataFrame as the first argument')

        if func_name == 'plot':
            if not MATPLOTLIB_AVAILABLE:
                raise SemanticError('plot requires matplotlib to be installed')
            if len(args) == 1:
                data = args[0]
                if data.type_name == 'Vector':
                    plt.figure()
                    plt.plot(data.data)
                    plt.show()
                    return NGSLValue('Unit', None)
                if data.type_name == 'Matrix':
                    plt.figure()
                    for col in range(data.data.shape[1]):
                        plt.plot(data.data[:, col], label=f"col{col}")
                    plt.legend()
                    plt.show()
                    return NGSLValue('Unit', None)
                if data.type_name == 'DataFrame' and isinstance(data.data, NGSLDataFrame):
                    if len(data.data.columns) == 1:
                        plt.figure()
                        plt.plot(data.data.data[data.data.columns[0]])
                        plt.show()
                        return NGSLValue('Unit', None)
            elif len(args) == 2:
                x = args[0]
                y = args[1]
                if x.type_name == 'Vector' and y.type_name == 'Vector':
                    plt.figure()
                    plt.scatter(x.data, y.data)
                    plt.show()
                    return NGSLValue('Unit', None)
                if x.type_name == 'DataFrame' and x.data and isinstance(x.data, NGSLDataFrame) and isinstance(y.data, str):
                    if y.data in x.data.columns:
                        plt.figure()
                        plt.plot(x.data.data[y.data])
                        plt.show()
                        return NGSLValue('Unit', None)
            raise SemanticError('plot expects a vector, matrix, or data.frame with optional column name')

        if func_name == 'lm':
            if len(args) != 2:
                raise SemanticError('lm requires a formula and a data.frame')
            formula_value = args[0]
            data_value = args[1]
            if formula_value.type_name not in ('String', 'Formula'):
                raise SemanticError('lm requires a formula string as first argument')
            if data_value.type_name != 'DataFrame' or not isinstance(data_value.data, NGSLDataFrame):
                raise SemanticError('lm requires a data.frame as second argument')
            formula = formula_value.data
            response = self._linear_model_from_formula(formula, data_value.data)
            return NGSLValue('LinearModel', response)

        if func_name == 'glm':
            if len(args) != 2:
                raise SemanticError('glm requires a formula and a data.frame')
            formula_value = args[0]
            data_value = args[1]
            if formula_value.type_name not in ('String', 'Formula'):
                raise SemanticError('glm requires a formula string as first argument')
            if data_value.type_name != 'DataFrame' or not isinstance(data_value.data, NGSLDataFrame):
                raise SemanticError('glm requires a data.frame as second argument')
            formula = formula_value.data
            response = self._linear_model_from_formula(formula, data_value.data)
            return NGSLValue('GLMModel', response)

        if func_name == 'pca':
            if len(args) != 1:
                raise SemanticError('pca requires 1 argument')
            data_value = args[0]
            matrix = self._extract_matrix(data_value)
            cols = matrix.shape[1]
            mean = np.mean(matrix, axis=0)
            centered = matrix - mean
            cov_matrix = np.cov(centered, rowvar=False)
            eigvals, eigvecs = np.linalg.eigh(cov_matrix)
            order = np.argsort(eigvals)[::-1]
            components = eigvecs[:, order]
            explained = eigvals[order] / np.sum(eigvals)
            return NGSLValue('PCAResult', PCAResult(components, explained, mean))

        if func_name == 'kmeans':
            if len(args) != 2:
                raise SemanticError('kmeans requires 2 arguments')
            data_value = args[0]
            k_value = args[1]
            matrix = self._extract_matrix(data_value)
            k = int(k_value.data)
            if k <= 0:
                raise SemanticError('kmeans requires positive cluster count')
            centroids, labels = self._run_kmeans(matrix, k)
            return NGSLValue('KMeansResult', KMeansResult(centroids, labels))

        if func_name == 'summary':
            if len(args) != 1:
                raise SemanticError('summary requires 1 argument')
            arg = args[0]
            if arg.type_name == 'GLMModel' and isinstance(arg.data, GLMModel):
                coef_lines = [f"{name}: {coef:.4f}" for name, coef in zip(arg.data.feature_names, arg.data.coefficients)]
                coef_lines.append(f"intercept: {arg.data.intercept:.4f}")
                summary_text = "\n".join(coef_lines)
                return NGSLValue('String', summary_text)
            if arg.type_name == 'DataFrame' and isinstance(arg.data, NGSLDataFrame):
                rows = len(arg.data.data[arg.data.columns[0]]) if arg.data.columns else 0
                return NGSLValue('String', f"DataFrame with {rows} rows and {len(arg.data.columns)} columns")
            raise SemanticError('summary only supports GLMModel and DataFrame')

        if func_name == 'predict':
            if len(args) != 2:
                raise SemanticError('predict requires a model and a data.frame')
            model_value = args[0]
            newdata = args[1]
            if model_value.type_name != 'GLMModel' or not isinstance(model_value.data, GLMModel):
                raise SemanticError('predict requires a GLMModel as first argument')
            if newdata.type_name != 'DataFrame' or not isinstance(newdata.data, NGSLDataFrame):
                raise SemanticError('predict requires a data.frame as second argument')
            prediction = self._predict_glm(model_value.data, newdata.data)
            return NGSLValue('Vector', prediction)

        if func_name == 't':
            if len(args) != 1:
                raise SemanticError("t requires 1 argument")
            matrix = args[0].data
            if isinstance(matrix, np.ndarray):
                return NGSLValue('Matrix', np.transpose(matrix))
            else:
                raise SemanticError("t requires a matrix argument")
        
        if func_name in {'nrow', 'ncol'}:
            if len(args) != 1:
                raise SemanticError(f"{func_name} requires 1 argument")
            matrix = args[0].data
            if isinstance(matrix, np.ndarray):
                shape = matrix.shape
                result = shape[0] if func_name == 'nrow' else shape[1]
                return NGSLValue('Int', result)
            else:
                raise SemanticError(f"{func_name} requires a matrix argument")
        
        if func_name == 'dim':
            if len(args) != 1:
                raise SemanticError("dim requires 1 argument")
            matrix = args[0].data
            if isinstance(matrix, np.ndarray):
                return NGSLValue('Vector', np.array(matrix.shape))
            else:
                raise SemanticError("dim requires a matrix argument")
        
        # Matrix algebra
        if func_name == 'det':
            if len(args) != 1:
                raise SemanticError("det requires 1 argument")
            matrix = args[0].data
            if isinstance(matrix, np.ndarray):
                result = float(np.linalg.det(matrix))
                return NGSLValue('Float', result)
            else:
                raise SemanticError("det requires a matrix argument")
        
        if func_name == 'inv':
            if len(args) != 1:
                raise SemanticError("inv requires 1 argument")
            matrix = args[0].data
            if isinstance(matrix, np.ndarray):
                result = np.linalg.inv(matrix)
                return NGSLValue('Matrix', result)
            else:
                raise SemanticError("inv requires a matrix argument")
        
        if func_name == 'solve':
            if len(args) < 2:
                raise SemanticError("solve requires at least 2 arguments")
            a = args[0].data
            b = args[1].data
            # Solve Ax = b using LAPACK (via NumPy)
            x = np.linalg.solve(a, b)
            return NGSLValue('Vector', x)
        
        # Correlation and covariance
        if func_name == 'cor':
            if len(args) == 2:
                x = args[0].data
                y = args[1].data
                if isinstance(x, np.ndarray) and isinstance(y, np.ndarray):
                    x_arr, y_arr = self._broadcast_vector_arrays(x, y)
                    result = float(np.corrcoef(x_arr, y_arr)[0, 1])
                    return NGSLValue('Float', result)
            elif len(args) == 1 and isinstance(args[0].data, np.ndarray):
                data = args[0].data
                result = np.corrcoef(data.T)
                return NGSLValue('Matrix', result)
        
        if func_name == 'cov':
            if len(args) == 2:
                x = args[0].data
                y = args[1].data
                if isinstance(x, np.ndarray) and isinstance(y, np.ndarray):
                    x_arr, y_arr = self._broadcast_vector_arrays(x, y)
                    result = float(np.cov(x_arr, y_arr)[0, 1])
                    return NGSLValue('Float', result)
            elif len(args) == 1 and isinstance(args[0].data, np.ndarray):
                data = args[0].data
                result = np.cov(data.T)
                return NGSLValue('Matrix', result)
        
        raise SemanticError(f"Unknown function: {func_name}")

    def _linear_model_from_formula(self, formula: str, frame: NGSLDataFrame) -> GLMModel:
        if '~' not in formula:
            raise SemanticError('glm formula must contain ~')
        lhs, rhs = formula.split('~', 1)
        response_name = lhs.strip()
        predictors = [token.strip() for token in rhs.split('+') if token.strip()]
        if response_name not in frame.columns:
            raise SemanticError(f"Response variable '{response_name}' not found in data frame")
        y = frame.data[response_name].astype(float)
        design = [np.ones(len(y))]
        feature_names = ['intercept']
        for term in predictors:
            if term not in frame.columns:
                raise SemanticError(f"Predictor '{term}' not found in data frame")
            column = frame.data[term].astype(float)
            design.append(column)
            feature_names.append(term)
        x = np.vstack(design).T
        coefficients, *_ = np.linalg.lstsq(x, y, rcond=None)
        intercept = float(coefficients[0])
        return GLMModel(coefficients=coefficients[1:], intercept=intercept, formula=formula, feature_names=predictors)

    def _predict_glm(self, model: GLMModel, frame: NGSLDataFrame) -> np.ndarray:
        if len(model.feature_names) == 0:
            return np.full(len(next(iter(frame.data.values()))), model.intercept)
        values = []
        for term in model.feature_names:
            if term not in frame.columns:
                raise SemanticError(f"Predictor '{term}' not found in new data")
            values.append(frame.data[term].astype(float))
        x = np.vstack(values).T
        return x.dot(model.coefficients) + model.intercept

    def _extract_matrix(self, value: NGSLValue) -> np.ndarray:
        if value.type_name == 'Matrix' and isinstance(value.data, np.ndarray):
            return value.data
        if value.type_name == 'DataFrame' and isinstance(value.data, NGSLDataFrame):
            arrays = [value.data.data[col].astype(float) for col in value.data.columns]
            return np.vstack(arrays).T
        raise SemanticError('Expected matrix or data.frame for PCA/kmeans')

    def _run_kmeans(self, matrix: np.ndarray, k: int) -> Tuple[np.ndarray, np.ndarray]:
        n, d = matrix.shape
        rng = np.random.default_rng()
        centroids = matrix[rng.choice(n, size=k, replace=False)]
        labels = np.zeros(n, dtype=int)
        for iteration in range(100):
            distances = np.linalg.norm(matrix[:, None, :] - centroids[None, :, :], axis=2)
            new_labels = np.argmin(distances, axis=1)
            if np.array_equal(new_labels, labels):
                break
            labels = new_labels
            for j in range(k):
                points = matrix[labels == j]
                if len(points) > 0:
                    centroids[j] = np.mean(points, axis=0)
        return centroids, labels
    
    def _eval_method_call(self, expr: MethodCallExpression) -> NGSLValue:
        """Evaluate method calls on objects"""
        if isinstance(expr.receiver, Identifier) and expr.receiver.name not in self.env:
            func_name = f"{expr.receiver.name}.{expr.method_name}"
            synth_call = CallExpression(callee=Identifier(func_name), arguments=expr.arguments)
            return self._eval_call(synth_call)

        receiver = self._eval_expression(expr.receiver)
        args = [self._eval_expression(arg) for arg in expr.arguments]
        
        if receiver.type_name == 'Vector':
            method = expr.method_name
            data = receiver.data
            
            if method == 'sum':
                return NGSLValue('Float', float(np.sum(data)))
            elif method == 'mean':
                return NGSLValue('Float', float(np.mean(data)))
            elif method == 'filter':
                # Simplified filter: just return same vector for now
                return receiver
            elif method == 'map':
                # Simplified map: just return same vector for now
                return receiver
            elif method == 'len':
                return NGSLValue('Int', len(data))
            elif method == 'sort':
                return NGSLValue('Vector', np.sort(data))
            elif method == 'reverse':
                return NGSLValue('Vector', np.flip(data))
        
        raise SemanticError(f"Unknown method: {expr.method_name}")
