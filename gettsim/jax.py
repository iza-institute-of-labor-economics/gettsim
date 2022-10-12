import ast
import functools
import inspect
from copy import deepcopy
from importlib import import_module
from typing import Dict

import astor


DEFAULT_MAPPING = {" and ": " & ", " or ": " | ", " not ": " ~"}


def change_if_to_where_wrapper(
    func: callable, backend: str = "np", mapping: Dict[str, str] = DEFAULT_MAPPING
):
    """Change if statement to where call in the ast of func and return new function.

    Args:
        func (callable): Function.
        backend (str): Backend array library abbreviation.
        mapping (dict): Find-and-replace mapping which is applied to the source code
            before the ast is generated.

    Returns:
        callable: New function with altered ast.

    """
    tree = _change_if_to_where_ast(func, backend=backend, mapping=mapping)

    # recreate scope of function and add array library
    scope = func.__globals__
    if backend == "np":
        scope["np"] = import_module("numpy")
    elif backend == "jnp":
        scope["jnp"] = import_module("jax.numpy")
    else:
        msg = f"Argument 'backend' is {backend} but must be in {'np', 'jnp'}."
        raise NotImplementedError(msg)

    # execute new ast
    compiled = compile(tree, "<ast>", "exec")
    exec(compiled, scope)

    # assign created function
    new_func = scope[func.__name__]
    return functools.wraps(func)(new_func)


def change_if_to_where_source(
    func: callable, backend: str = "np", mapping: Dict[str, str] = DEFAULT_MAPPING
):
    """Change if statement to where call in the ast of func and return new source code.

    Note: This function only works when the package astor is installed.

    Args:
        func (callable): Function.
        backend (str): Backend array library abbreviation.
        mapping (dict): Find-and-replace mapping which is applied to the source code
            before the ast is generated.

    Returns:
        str: Source code of new function with altered ast.

    """
    tree = _change_if_to_where_ast(func, backend=backend, mapping=mapping)
    source = astor.code_gen.to_source(tree)
    return source


def _change_if_to_where_ast(
    func: callable, backend: str = "np", mapping: Dict[str, str] = DEFAULT_MAPPING
):
    """Change if statement to where call in the ast of func and return new ast.

    Args:
        func (callable): Function.
        backend (str): Backend array library abbreviation.
        mapping (dict): Find-and-replace mapping which is applied to the source code
            before the ast is generated.

    Returns:
        ast.Module: AST of new function with altered ast.

    """
    # create ast from func
    tree = _func_to_ast(func, mapping=mapping)
    tree = _add_parent_attr_to_ast(tree)

    # transform tree nodes
    new_tree = Transformer(backend).visit(tree)
    new_tree = ast.fix_missing_locations(new_tree)
    return new_tree


def _func_to_ast(func: callable, mapping: Dict = None):
    source = inspect.getsource(func)

    if mapping is not None:
        for old, new in mapping.items():
            source = source.replace(old, new)

    tree = ast.parse(source)
    return tree


def _add_parent_attr_to_ast(tree: ast.AST):
    tree = deepcopy(tree)
    for node in ast.walk(tree):
        for child in ast.iter_child_nodes(node):
            child.parent = node
    return tree


# ======================================================================================
# Transformation classes and functions
# ======================================================================================


class Transformer(ast.NodeTransformer):
    """Transformer class.

    The visit_{stmt|expr} methods are called while traversing the ast if the current
    node class is {stmt|expr}. The node is then swapped with the return value of
    visit_{stmt|expr}.

    """

    def __init__(self, backend: str):
        self.backend = backend

    def visit_If(self, node: ast.AST):  # noqa: N802
        if isinstance(node.parent, ast.FunctionDef):
            call = _if_to_call(node, backend=self.backend)
            if isinstance(node.body[0], ast.Return):
                out = ast.Return(call)
            elif isinstance(node.body[0], (ast.Assign, ast.AugAssign)):
                out = deepcopy(node.body[0])
                out.value = call
        else:
            out = node
        return out

    def visit_IfExp(self, node: ast.AST):  # noqa: N802
        call = _ifexp_to_call(node, backend=self.backend)
        return call


def _if_to_call(node: ast.If, backend: str):
    """Transform If statement to Call.

    Args:
        node (ast.If): A If node in the ast.
        backend (str): Backend array library.

    Returns:
        ast.Call: The If statement reformatted using a call to {backend}.where().

    """
    args = [node.test, node.body[0].value]

    if len(node.orelse) > 1 or len(node.body) > 1:
        msg = _too_many_operations_message(node)
        raise TranslateToJaxError(msg)
    elif node.orelse == []:
        if isinstance(node.body[0], ast.Return):
            msg = _return_and_no_else_message(node)
            raise TranslateToJaxError(msg)
        elif hasattr(node.body[0], "targets"):
            name = ast.Name(id=node.body[0].targets[0].id, ctx=ast.Load())
        else:
            name = ast.Name(id=node.body[0].target.id, ctx=ast.Load())
        args.append(name)
    elif isinstance(node.orelse[0], ast.Return):
        args.append(node.orelse[0].value)
    elif isinstance(node.orelse[0], ast.If):
        call = _if_to_call(node.orelse[0], backend=backend)
        args.append(call)
    elif isinstance(node.orelse[0], (ast.Assign, ast.AugAssign)):
        if isinstance(node.orelse[0].value, ast.IfExp):
            call = _ifexp_to_call(node.orelse[0].value, backend=backend)
            args.append(call)
        else:
            args.append(node.orelse[0].value)
    else:
        msg = _unallowed_operation_message(node.orelse[0])
        raise TranslateToJaxError(msg)

    call = ast.Call(
        func=ast.Attribute(
            value=ast.Name(id=backend, ctx=ast.Load()), attr="where", ctx=ast.Load()
        ),
        args=args,
        keywords=[],
    )
    return call


def _ifexp_to_call(node: ast.IfExp, backend: str):
    """Transform IfExp expression to Call.

    Args:
        node (ast.IfExp): A IfExp node in the ast.
        backend (str): Backend array library.

    Returns:
        ast.Call: The IfExp expression reformatted using a call to {backend}.where().

    """
    args = [node.test, node.body]

    if isinstance(node.orelse, ast.IfExp):
        call = _ifexp_to_call(node.orelse, backend=backend)
        args.append(call)
    else:
        args.append(node.orelse)

    call = ast.Call(
        func=ast.Attribute(
            value=ast.Name(id=backend, ctx=ast.Load()), attr="where", ctx=ast.Load()
        ),
        args=args,
        keywords=[],
    )
    return call


# ======================================================================================
# Transformation errors
# ======================================================================================


class TranslateToJaxError(ValueError):
    """Error when function cannot be translated into JAX compatible format."""

    pass


def _return_and_no_else_message(node: ast.Return):
    source = _node_to_formatted_source(node)
    msg = (
        "The if-clause body is a return statement, while the else clause is missing.\n"
        "Please swap the return statement for an assignment or add an else-clause.\n"
        f"The source code in question is:\n\n{source}"
    )
    return msg


def _too_many_operations_message(node: ast.If):
    source = _node_to_formatted_source(node)
    msg = (
        "An if statement is performing multiple operations, which is forbidden.\n"
        "Please only perform one operation in the body of an if-elif-else statement.\n"
        f"The source code in question is:\n\n{source}"
    )
    return msg


def _unallowed_operation_message(node: ast.If):
    source = _node_to_formatted_source(node)
    msg = (
        "An if-elif-else clause body is of type {type(node)}, which is forbidden.\n"
        "Allowed types are the following:\n\n"
        "ast.If : Another if-else-elif clause\n"
        "ast.IfExp : A one-line if-else statement. Example: 1 if flag else 0\n"
        "ast.Assign : An assignment. Example: x = 3\n"
        "ast.Return : A return statement. Example: return out\n\n"
        f"The source code in question is:\n\n{source}"
    )
    return msg


def _node_to_formatted_source(node: ast.AST):
    source = astor.code_gen.to_source(node)
    source = " > " + source[:-1].replace("\n", "\n > ")
    return source
