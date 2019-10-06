import io
from io import TextIOBase
from typing import Dict, List

from src.engine import stream_reader
from src.engine.parser import Parser
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
        self.opening = template_opening
        self.global_variables = global_variables
        self.parser = Parser(
            template_opening,
            function_open,
            function_close,
            template_closing)

    def parse(self,
              input_stream: TextIOBase,
              output_stream: TextIOBase,
              variables: Dict,
              function_stack: List):
        current_template_text = []
        syntax_tree = SyntaxTree()

        has_opening, current_template_text = try_detect_opening(
            input_stream,
            current_template_text)

        if has_opening:
            has_function, function_name, current_template_text = try_detect_function(
                input_stream, current_template_text)

            if has_function:
                has_arguments, arguments, current_template_text = try_detect_function_args(
                    input_stream, function_name, current_template_text)

                if has_arguments:
                    has_template_closing, current_template_text = try_detect_template_closing(
                        input_stream, current_template_text)

                    if has_template_closing:
                        function_node = SyntaxNode(function_name, arguments)
                        syntax_tree.branch_with_new_node(function_name)

                    else:
                        handle_error_state(
                            output_stream,
                            current_template_text,
                            syntax_tree)

                else:
                    handle_error_state(
                        output_stream,
                        current_template_text,
                        syntax_tree)

            else:
                has_variable, variable, current_template_text = try_detect_variable(
                    input_stream, current_template_text)

                if has_variable:
                    has_template_closing, current_template_text = try_detect_template_closing(
                        input_stream, current_template_text)

                    if has_template_closing:
                        print_node = SyntaxNode("print", variable)
                        syntax_tree.add_node_to_current_level(print_node)

                    else:
                        handle_error_state(
                            output_stream,
                            current_template_text,
                            syntax_tree)

                else:
                    handle_error_state(
                        output_stream,
                        current_template_text,
                        syntax_tree)

        else:
            print_char(current_template_text, output_stream)
