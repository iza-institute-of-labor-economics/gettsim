import ast
import functools
import inspect
from importlib import import_module

import astor

BACKEND_TO_MODULE = {"jax": "jax.numpy", "numpy": "numpy"}


def make_vectorizable(func: callable, backend: str):
    """Redefine function to be vectorizable given backend.

    This function replaces if statements with where() calls, as well as boolean
    operations with their bit operation counterpart, and not with inversion. After the
    replacement the function can be called with vector-valued input.

    Args:
        func (callable): Function.
        backend (str): Backend library. Currently supported backends are 'jax' and
            'numpy'. Array module must export function `where` that behaves as
            `numpy.where`.

    Returns:
        callable: New function with altered ast.

    """
    module = _module_from_backend(backend)
    tree = _make_vectorizable_ast(func, module=module)

    # recreate scope of function, add policy_function decorator and array library
    scope = func.__globals__
    from _gettsim.function_types import policy_function

    scope["policy_function"] = policy_function
    scope[module] = import_module(module)

    # execute new ast
    compiled = compile(tree, "<ast>", "exec")
    exec(compiled, scope)  # noqa: S102

    # assign created function
    new_func = scope[func.__name__]
    return functools.wraps(func)(new_func)


def make_vectorizable_source(
    func: callable,
    backend: str,
):
    """Redefine function source to be vectorizable given backend.

    This function replaces if statements with {backend}.where(), as well as boolean
    operations with their bit operation counterpart, and not with inversion. After the
    replacement the function can be called with vector-valued input.

    Args:
        func (callable): Function.
        backend (str): Backend library. See dict `BACKEND_TO_MODULE` for currently
            supported backends. Array module must export function `where` that behaves
            as `numpy.where`.

    Returns:
        str: Source code of new function with altered ast.

    """
    module = _module_from_backend(backend)
    tree = _make_vectorizable_ast(func, module=module)
    source = astor.code_gen.to_source(tree)
    return source


def _make_vectorizable_ast(func: callable, module: str):
    """Change if statement to where call in the ast of func and return new ast.

    Args:
        func (callable): Function.
        module (str): Module which exports the function `where` that behaves as
            `numpy.where`.

    Returns:
        ast.Module: AST of new function with altered ast.

    """
    # create ast from func
    tree = _func_to_ast(func)
    tree = _add_parent_attr_to_ast(tree)

    # get function location for error messages
    func_loc = func.__module__ + "/" + func.__name__

    # transform tree nodes
    new_tree = Transformer(module, func_loc).visit(tree)
    new_tree = ast.fix_missing_locations(new_tree)
    return new_tree


def _func_to_ast(func: callable):
    source = inspect.getsource(func)
    tree = ast.parse(source)
    return tree


def _add_parent_attr_to_ast(tree: ast.AST):
    for node in ast.walk(tree):
        for child in ast.iter_child_nodes(node):
            child.parent = node
    return tree


# ======================================================================================
# Transformation class
# ======================================================================================


class Transformer(ast.NodeTransformer):
    def __init__(self, module: str, func_loc: str):
        self.module = module
        self.func_loc = func_loc

    def visit_Call(self, node: ast.Call):  # noqa: N802
        self.generic_visit(node)
        call = _call_to_call_from_module(
            node, module=self.module, func_loc=self.func_loc
        )
        return call

    def visit_UnaryOp(self, node: ast.UnaryOp):  # noqa: N802
        if isinstance(node.op, ast.Not):
            out = _not_to_call(node, module=self.module)
        else:
            out = node
        return out

    def visit_BoolOp(self, node: ast.BoolOp):  # noqa: N802
        self.generic_visit(node)
        call = _boolop_to_call(node, module=self.module)
        return call

    def visit_If(self, node: ast.If):  # noqa: N802
        self.generic_visit(node)
        call = _if_to_call(node, module=self.module, func_loc=self.func_loc)
        if isinstance(node.body[0], ast.Return):
            out = ast.Return(call)
        elif isinstance(node.body[0], ast.Assign | ast.AugAssign):
            out = node.body[0]
            out.value = call
        return out

    def visit_IfExp(self, node: ast.IfExp):  # noqa: N802
        self.generic_visit(node)
        call = _ifexp_to_call(node, module=self.module)
        return call


# ======================================================================================
# Transformation functions on node level
# ======================================================================================


def _not_to_call(node: ast.UnaryOp, module: str):
    """Transform negation operation to Call.

    Args:
        node (ast.If): A UnaryOp node in the ast.
        module (str): Module which exports the function `where` that behaves as
            `numpy.where`.

    Returns:
        ast.Call: The negation reformatted using a call to {module}.logical_not().

    """
    call = ast.Call(
        func=ast.Attribute(
            value=ast.Name(id=module, ctx=ast.Load()),
            attr="logical_not",
            ctx=ast.Load(),
        ),
        args=[node.operand],
        keywords=[],
    )
    return call


def _if_to_call(node: ast.If, module: str, func_loc: str):
    """Transform If statement to Call.

    Args:
        node (ast.If): An If node in the ast.
        module (str): Module which exports the function `where` that behaves as
            `numpy.where`.
        func_loc (str): Path to function.

    Returns:
        ast.Call: The If statement reformatted using a call to {module}.where().

    """
    args = [node.test, node.body[0].value]

    if len(node.orelse) > 1 or len(node.body) > 1:
        msg = _too_many_operations_error_message(node, func_loc=func_loc)
        raise TranslateToVectorizableError(msg)
    elif node.orelse == []:
        if isinstance(node.body[0], ast.Return):
            msg = _return_and_no_else_error_message(node, func_loc=func_loc)
            raise TranslateToVectorizableError(msg)
        elif hasattr(node.body[0], "targets"):
            name = ast.Name(id=node.body[0].targets[0].id, ctx=ast.Load())
        else:
            name = ast.Name(id=node.body[0].target.id, ctx=ast.Load())
        args.append(name)
    elif isinstance(node.orelse[0], ast.Return):
        args.append(node.orelse[0].value)
    elif isinstance(node.orelse[0], ast.If):
        call = _if_to_call(node.orelse[0], module=module)
        args.append(call)
    elif isinstance(node.orelse[0], ast.Assign | ast.AugAssign):
        if isinstance(node.orelse[0].value, ast.IfExp):
            call = _ifexp_to_call(node.orelse[0].value, module=module)
            args.append(call)
        else:
            args.append(node.orelse[0].value)
    else:
        msg = _unallowed_operation_error_message(node.orelse[0], func_loc=func_loc)
        raise TranslateToVectorizableError(msg)

    call = ast.Call(
        func=ast.Attribute(
            value=ast.Name(id=module, ctx=ast.Load()), attr="where", ctx=ast.Load()
        ),
        args=args,
        keywords=[],
    )
    return call


def _ifexp_to_call(node: ast.IfExp, module: str):
    """Transform IfExp expression to Call.

    Args:
        node (ast.IfExp): An IfExp node in the ast.
        module (str): Module which exports the function `where` that behaves as
            `numpy.where`.

    Returns:
        ast.Call: The IfExp expression reformatted using a call to {module}.where().

    """
    args = [node.test, node.body]

    if isinstance(node.orelse, ast.IfExp):
        call = _ifexp_to_call(node.orelse, module=module)
        args.append(call)
    else:
        args.append(node.orelse)

    call = ast.Call(
        func=ast.Attribute(
            value=ast.Name(id=module, ctx=ast.Load()), attr="where", ctx=ast.Load()
        ),
        args=args,
        keywords=[],
    )
    return call


def _boolop_to_call(node: ast.BoolOp, module: str):
    """Transform BoolOp operation to Call.

    Args:
        node (ast.BoolOp): A BoolOp node in the ast.

    Returns:
        ast.Call: The BoolOp expression reformatted using functions 'logical_and'
            instead of 'and', and 'logical_or' instead of 'or'.

    """
    operation = {ast.And: "logical_and", ast.Or: "logical_or"}[type(node.op)]

    def _constructor(left, right):
        """Construct calls of the form `numpy.logical_(and|or)(left, right)`."""
        return ast.Call(
            func=ast.Attribute(
                value=ast.Name(id=module, ctx=ast.Load()),
                attr=operation,
                ctx=ast.Load(),
            ),
            args=[left, right],
            keywords=[],
        )

    values = [
        _boolop_to_call(v, module=module) if isinstance(v, ast.BoolOp) else v
        for v in node.values
    ]

    call = functools.reduce(_constructor, values)
    return call


def _call_to_call_from_module(node: ast.Call, module: str, func_loc: str):
    """Transform built-in Calls to Calls from module.

    Transforms built-in functions in ('sum', 'any', 'all', 'max', 'min') to their
    backend equivalent.

    Args:
        node (ast.Call): A Call node in the ast.

    Returns:
        ast.Call: The Call expression reformatted using functions from the module
            `module`, e.g., `{module}.max(x)` instead of `max(x)`.

    """
    to_transform = ("sum", "any", "all", "max", "min")

    transform_node = hasattr(node.func, "id") and node.func.id in to_transform

    if not transform_node:
        # Only transform built-in calls, otherwise return node
        return node

    func_id = node.func.id
    call = node
    args = node.args

    if len(args) == 1:
        # Handles all cases called with a single sequence-type argument
        call.func = ast.Attribute(
            value=ast.Name(id=module, ctx=ast.Load()),
            attr=func_id,
            ctx=ast.Load(),
        )
    elif func_id in ("max", "min") and len(args) == 2:
        # Handles case of comparison between two variables
        attr = func_id + "imum"  # max -> maximum, min -> minimum
        call.func = ast.Attribute(
            value=ast.Name(id=module, ctx=ast.Load()),
            attr=attr,
            ctx=ast.Load(),
        )
    else:
        msg = _too_many_arguments_call_error_message(node, func_loc=func_loc)
        raise TranslateToVectorizableError(msg)

    return call


# ======================================================================================
# Transformation errors
# ======================================================================================


class TranslateToVectorizableError(ValueError):
    """Error when function cannot be translated into vectorizable compatible format."""


def _too_many_arguments_call_error_message(node: ast.Call, func_loc: str):
    source = _node_to_formatted_source(node)
    _func_name = node.func.id
    msg = (
        "\n\n"
        f"The function {_func_name} is called with too many arguments. Please only use "
        "one iterable argument for (`sum`, `any`, `all`, `max`, `min`) or two "
        "arguments for (`max`, `min`)."
        f"\n\nFunction: {func_loc}\n\n"
        "Problematic source code (after transformations that were possible, if any):"
        f"\n\n{source}\n"
    )
    return msg


def _return_and_no_else_error_message(node: ast.Return, func_loc: str):
    source = _node_to_formatted_source(node)
    msg = (
        "\n\n"
        "The if-clause body is a return statement, while the else clause is missing.\n"
        "Please swap the return statement for an assignment or add an else-clause."
        f"\n\nFunction: {func_loc}\n\n"
        "Problematic source code (after transformations that were possible, if any):"
        f"\n\n{source}\n"
    )
    return msg


def _too_many_operations_error_message(node: ast.If, func_loc: str):
    source = _node_to_formatted_source(node)
    msg = (
        "\n\n"
        "An if statement is performing multiple operations, which is forbidden.\n"
        "Please only perform one operation in the body of an if-elif-else statement."
        f"\n\nFunction: {func_loc}\n\n"
        "Problematic source code (after transformations that were possible, if any):"
        f"\n\n{source}\n"
    )
    return msg


def _unallowed_operation_error_message(node: ast.If, func_loc: str):
    source = _node_to_formatted_source(node)
    msg = (
        "\n\n"
        "An if-elif-else clause body is of type {type(node)}, which is forbidden.\n"
        "Allowed types are the following:\n\n"
        "ast.If : Another if-else-elif clause\n"
        "ast.IfExp : A one-line if-else statement. Example: 1 if flag else 0\n"
        "ast.Assign : An assignment. Example: x = 3\n"
        "ast.Return : A return statement. Example: return out"
        f"\n\nFunction: {func_loc}\n\n"
        "Problematic source code (after transformations that were possible, if any):"
        f"\n\n{source}\n"
    )
    return msg


def _node_to_formatted_source(node: ast.AST):
    source = astor.code_gen.to_source(node)
    source = " > " + source[:-1].replace("\n", "\n > ")
    return source


def _module_from_backend(backend: str):
    module = BACKEND_TO_MODULE.get(backend)
    if module is None:
        msg = (
            f"Argument 'backend' is {backend} but must be in "
            f"{BACKEND_TO_MODULE.keys()}."
        )
        raise NotImplementedError(msg)
    return module
