from typing import List, Mapping, Union, TextIO

from src.engine.parser import Parser
from src.engine.syntax_tree_processor import process_syntax_tree
from src.model.parsed_token import ScopeAction
from src.model.syntax_node import SyntaxNode
from src.model.syntax_tree import SyntaxTree


class TemplatingEngine:
    def __init__(self,
                 global_variables: Mapping[str, Union[str, List[str]]],
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
                input_stream: TextIO,
                output_stream: TextIO):
        syntax_tree = SyntaxTree()

        token = self.parser.parse_single_construct(input_stream)

        while not token.function_name == "end":
            syntax_node = SyntaxNode(token.function_name, token.arguments)
            if token.scope is ScopeAction.NONE:
                syntax_tree.add_node_to_current_level(syntax_node)
            elif token.scope is ScopeAction.OPEN:
                syntax_tree.branch_with_new_node(syntax_node)
            elif token.scope is ScopeAction.CLOSE:
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
