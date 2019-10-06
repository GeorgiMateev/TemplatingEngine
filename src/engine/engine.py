import io
from io import TextIOBase
from typing import Dict, List

from src.engine import stream_reader
from src.engine.parser import Parser
from src.engine.syntax_tree_processor import process_syntax_tree
from src.model.syntax_node import SyntaxNode
from src.model.syntax_tree import SyntaxTree


def try_detect_opening(input_stream, current_read_text):
    pass


def execute_loop(arguments, variables, function_stack, input_stream,
                 function_out_stream):
    iteration_values_var, identifier_var = arguments
    iteration_values = variables[iteration_values_var]

    for value in iteration_values:
        new_scope_vars = {**variables, **{identifier_var: value}}
        new_stack = function_stack + ['loop']


def execute_function(function_name, arguments, variables, function_stack,
                     input_stream, function_out_stream):

    if function_name == "loop":
        execute_loop(arguments, variables, function_stack, input_stream, function_out_stream)


def handle_error_state(output_stream, current_template_text,
                       syntax_tree):
    pass


class TemplatingEngine:
    def __init__(self,
                 global_variables: Dict,
                 template_opening="{{",
                 function_open="#",
                 function_close="/",
                 template_closing="}}",
                 throw_invalid=False):
        self.throw_invalid = throw_invalid
        self.opening = template_opening
        self.global_variables = global_variables
        self.parser = Parser(
            template_opening,
            function_open,
            function_close,
            template_closing)

    def process(self,
                input_stream: TextIOBase,
                output_stream: TextIOBase):
        syntax_tree = SyntaxTree()

        token = self.parser.parse_single_construct(input_stream)

        while not token.function_name == "end":
            syntax_node = SyntaxNode(token.function_name, token.arguments)
            if token.scope.NONE:
                syntax_tree.add_node_to_current_level(syntax_node)
            elif token.scope.OPEN:
                syntax_tree.branch_with_new_node(syntax_node)
            elif token.scope.CLOSE:
                syntax_tree.return_to_upper_level()

            # once we have flat structure (simple text or after loop exit)
            # we can process and output a result
            if syntax_tree.current_level == 1:
                result = process_syntax_tree(
                    syntax_tree,
                    self.global_variables,
                    self.throw_invalid)

                output_stream.write(result)

                syntax_tree = SyntaxTree()

            token = self.parser.parse_single_construct(input_stream)
