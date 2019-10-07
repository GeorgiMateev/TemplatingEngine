import logging
from typing import Dict, Mapping, Union, List, Sequence

from src.model.syntax_node import SyntaxNode
from src.model.syntax_tree import SyntaxTree


def process_syntax_tree(
        tree: SyntaxTree,
        variables: Mapping[str, Union[str, Sequence[str]]],
        throw_invalid_template_parse: bool) -> str:
    body = [process_node(
        node,
        variables,
        throw_invalid_template_parse) for node in tree.root.body]
    return ''.join(body)


def process_node(
        node: SyntaxNode,
        variables: Mapping[str, Union[str, Sequence[str]]],
        throw_invalid_body_parse: bool) -> str:
    if node.function_name == 'raw':
        return ''.join(node.arguments)
    elif node.function_name == 'print':
        return process_print(node, variables, throw_invalid_body_parse)
    elif node.function_name == 'loop':
        return process_loop(node, variables, throw_invalid_body_parse)
    elif node.function_name == 'error':
        return process_syntax_error(node, variables, throw_invalid_body_parse)


def process_print(
        node: SyntaxNode,
        variables: Mapping[str, Union[str, Sequence[str]]],
        throw_invalid_body_parse: bool) -> str:
    if len(node.arguments) != 1:
        raise ValueError("print function must have one argument")
    if node.arguments[0] not in variables:
        raise ValueError("No such variable: {}".format(node.arguments[0]))

    var = variables[node.arguments[0]]

    return str(var)


def process_loop(
        node: SyntaxNode,
        variables: Mapping[str, Union[str, List[str]]],
        throw_invalid_body_parse: bool) -> str:
    if len(node.arguments) != 2:
        raise ValueError("loop function must have two arguments")
    if node.arguments[0] not in variables:
        raise ValueError("No such variable: {}".format(node.arguments[0]))

    iterator_var = variables[node.arguments[0]]

    if not isinstance(iterator_var, List):
        raise ValueError(
            "Cannot iterate over variable: {}. It is not List."
            .format(iterator_var))

    identifier_var = node.arguments[1]

    loop_body = []
    for value in iterator_var:
        new_scope_vars = {**variables, **{identifier_var: value}}

        loop_iteration_body = [process_node(
            body_part_node,
            new_scope_vars,
            throw_invalid_body_parse) for body_part_node in node.body]

        loop_body.append(''.join(loop_iteration_body))

    return ''.join(loop_body)


def process_syntax_error(
        node: SyntaxNode,
        variables: Mapping[str, Union[str, Sequence[str]]],
        throw_invalid_body_parse: bool) -> str:
    if throw_invalid_body_parse:
        raise ValueError("Invalid syntax: {}".format(''.join(node.arguments)))
    else:
        logging.warning("Invalid syntax: {}. Printed as raw string."
                        .format(''.join(node.arguments)))
        return ''.join(node.arguments)
