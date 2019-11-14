from typing import List, Mapping, Union, TextIO

from src.engine.parser import Parser
from src.engine.syntax_analyser import SyntaxAnalyser
from src.engine.syntax_tree_processor import process_syntax_tree
from src.model.function_signiture import FunctionSignature
from src.model.parsed_token import ScopeAction
from src.model.syntax_node import SyntaxNode
from src.model.syntax_tree import SyntaxTree


class TemplatingEngine:
    def __init__(self,
                 global_variables: Mapping[str, Union[str, List[str]]],
                 template_open="{{",
                 template_close="}}",
                 function_open="#",
                 function_close="/",
                 throw_invalid=False):
        """
        Create new template engine.
        :param global_variables: Dictionary with variables used in the engine.
            For vars used in loops provide list with values.
        :param template_open: Two characters that define how template is started.
        :param template_close: Two characters that define how template is closed.
        :param function_open: One character defining start of a function.
        :param function_close: One character defining end of a function.
        :param throw_invalid: Raise error on invalid syntax.
        """
        self.throw_invalid = throw_invalid
        self.opening = template_open
        self.global_variables = global_variables
        self.parser = Parser(
            template_open,
            function_open,
            function_close,
            template_close)

    def process(self,
                input_stream: TextIO,
                output_stream: TextIO):
        """
        Start processing input stream and write the result into the output stream.
        :param input_stream: The text input. Make sure that proper buffering is used.
        :param output_stream: The output text stream. Make sure proper buffering is used.
        """
        syntax_tree = SyntaxTree()

        supported_functions = [
            FunctionSignature("raw", 1, False),
            FunctionSignature("error", 1, False),
            FunctionSignature("loop", 2, True),
            FunctionSignature("print", 1, False),
        ]
        syntax_analyser = SyntaxAnalyser(supported_functions)

        token = self.parser.parse_single_token(input_stream)

        while not token.function_name == "end":
            is_valid, analysed_token = syntax_analyser.analyse_token(
                syntax_tree.current_node,
                token)
            syntax_node = SyntaxNode(analysed_token.function_name, analysed_token.arguments)
            if analysed_token.scope is ScopeAction.NONE:
                syntax_tree.add_node_to_current_level(syntax_node)
            elif analysed_token.scope is ScopeAction.OPEN:
                syntax_tree.branch_with_new_node(syntax_node)
            elif analysed_token.scope is ScopeAction.CLOSE:
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

            token = self.parser.parse_single_token(input_stream)
