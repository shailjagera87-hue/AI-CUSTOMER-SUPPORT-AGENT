
import ast
import operator
import re


OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


def _calculate(node: ast.AST) -> float:
    if isinstance(node, ast.Constant) and type(node.value) in (int, float):
        return float(node.value)

    if isinstance(node, ast.BinOp) and type(node.op) in OPERATORS:
        left = _calculate(node.left)
        right = _calculate(node.right)

        if isinstance(node.op, ast.Div) and right == 0:
            raise ValueError("Division by zero is not allowed.")

        result = OPERATORS[type(node.op)](left, right)

        if abs(result) > 1e12:
            raise ValueError("Result exceeds the permitted range.")

        return result

    if isinstance(node, ast.UnaryOp) and type(node.op) in OPERATORS:
        return OPERATORS[type(node.op)](_calculate(node.operand))

    raise ValueError("Only basic arithmetic is supported.")


def calculate_expression(expression: str) -> float:
    expression = expression.strip()

    if len(expression) > 100:
        raise ValueError("Expression is too long.")

    if not re.fullmatch(r"[0-9+\-*/().\s]+", expression):
        raise ValueError("Expression contains unsupported characters.")

    tree = ast.parse(expression, mode="eval")
    return _calculate(tree.body)
