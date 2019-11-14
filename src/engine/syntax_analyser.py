from typing import List

from src.model.function_signiture import FunctionSignature
from src.model.parsed_token import ParsedToken, ScopeAction
from src.model.syntax_node import SyntaxNode


class SyntaxAnalyser:
    def __init__(self, supported_functions: List[FunctionSignature]):
        self.supported_functions: List[FunctionSignature] = supported_functions

    def analyse_token(self,
                      current_node: SyntaxNode,
                      token: ParsedToken):
        if token.scope == ScopeAction.CLOSE:
            if current_node.function_name != token.function_name:
                return False, ParsedToken(
                    False,
                    'error',
                    [''.join(token.raw_text)],
                    ScopeAction.NONE,
                    raw_text=token.raw_text)

        if token.scope == ScopeAction.OPEN or token.scope == ScopeAction.NONE:
            signature, *rest = [f for f in self.supported_functions if f.name == token.function_name]
            if not signature:
                return False, ParsedToken(
                    False,
                    'error',
                    [''.join(token.raw_text)],
                    ScopeAction.NONE,
                    raw_text=token.raw_text)

            if len(token.arguments) != signature.arity:
                return False, ParsedToken(
                    False,
                    'error',
                    [''.join(token.raw_text)],
                    ScopeAction.NONE,
                    raw_text=token.raw_text)

        return True, token
