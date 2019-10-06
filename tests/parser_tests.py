import io
import unittest

from src.engine.parser import Parser
from src.model.parsed_token import ParsedToken, ScopeAction


class ParserTests(unittest.TestCase):
    def test_single_variable(self):
        parser = Parser()

        test_stream = io.StringIO("a {{test}} v")

        expected_result = [
            ParsedToken(True, "raw", ["a"], ScopeAction.NONE, ["a"]),
            ParsedToken(True, "raw", [" "], ScopeAction.NONE, [" "]),
            ParsedToken(True, "print", ["test"], ScopeAction.NONE, list("{{test}}")),
            ParsedToken(True, "raw", [" "], ScopeAction.NONE, [" "]),
            ParsedToken(True, "raw", ["v"], ScopeAction.NONE, ["v"]),
            ParsedToken(True, "end", [], ScopeAction.NONE, [])
        ]

        actual_result = self.parse_stream(parser, test_stream)

        self.assert_parsed_tokens(actual_result, expected_result)

    def test_loop_start(self):
        parser = Parser()

        test_stream = io.StringIO("a {{#loop arg1 arg2}} v")

        expected_result = [
            ParsedToken(True, "raw", ["a"], ScopeAction.NONE, ["a"]),
            ParsedToken(True, "raw", [" "], ScopeAction.NONE, [" "]),
            ParsedToken(True, "loop", ["arg1", "arg2"], ScopeAction.OPEN, list("{{#loop arg1 arg2}}")),
            ParsedToken(True, "raw", [" "], ScopeAction.NONE, [" "]),
            ParsedToken(True, "raw", ["v"], ScopeAction.NONE, ["v"]),
            ParsedToken(True, "end", [], ScopeAction.NONE, [])
        ]

        actual_result = self.parse_stream(parser, test_stream)

        self.assert_parsed_tokens(actual_result, expected_result)

    def test_loop_end(self):
        parser = Parser()

        test_stream = io.StringIO("a {{/loop}} v")

        expected_result = [
            ParsedToken(True, "raw", ["a"], ScopeAction.NONE, ["a"]),
            ParsedToken(True, "raw", [" "], ScopeAction.NONE, [" "]),
            ParsedToken(True, "loop", [], ScopeAction.CLOSE, list("{{/loop}}")),
            ParsedToken(True, "raw", [" "], ScopeAction.NONE, [" "]),
            ParsedToken(True, "raw", ["v"], ScopeAction.NONE, ["v"]),
            ParsedToken(True, "end", [], ScopeAction.NONE, [])
        ]

        actual_result = self.parse_stream(parser, test_stream)

        self.assert_parsed_tokens(actual_result, expected_result)

    def test_template_not_open(self):
        parser = Parser()

        test_stream = io.StringIO("a {loop}} v")

        expected_result = [
            ParsedToken(True, "raw", ["a"], ScopeAction.NONE, ["a"]),
            ParsedToken(True, "raw", [" "], ScopeAction.NONE, [" "]),
            ParsedToken(True, "raw", ["{l"], ScopeAction.NONE, list("{l")),
            ParsedToken(True, "raw", ["o"], ScopeAction.NONE, ["o"]),
            ParsedToken(True, "raw", ["o"], ScopeAction.NONE, ["o"]),
            ParsedToken(True, "raw", ["p"], ScopeAction.NONE, ["p"]),
            ParsedToken(True, "raw", ["}"], ScopeAction.NONE, ["}"]),
            ParsedToken(True, "raw", ["}"], ScopeAction.NONE, ["}"]),
            ParsedToken(True, "raw", [" "], ScopeAction.NONE, [" "]),
            ParsedToken(True, "raw", ["v"], ScopeAction.NONE, ["v"]),
            ParsedToken(True, "end", [], ScopeAction.NONE, [])
        ]

        actual_result = self.parse_stream(parser, test_stream)

        self.assert_parsed_tokens(actual_result, expected_result)

    def test_template_invalid_close_print(self):
        parser = Parser()

        test_stream = io.StringIO("a {{arg} v")

        expected_result = [
            ParsedToken(True, "raw", ["a"], ScopeAction.NONE, ["a"]),
            ParsedToken(True, "raw", [" "], ScopeAction.NONE, [" "]),
            ParsedToken(False, "error", ["{{arg} "], ScopeAction.NONE, list("{{arg} ")),
            ParsedToken(True, "raw", ["v"], ScopeAction.NONE, ["v"]),
            ParsedToken(True, "end", [], ScopeAction.NONE, [])
        ]

        actual_result = self.parse_stream(parser, test_stream)

        self.assert_parsed_tokens(actual_result, expected_result)

    def test_template_invalid_close_loop(self):
        parser = Parser()

        test_stream = io.StringIO("a {{#loop arg1 arg2} v")

        expected_result = [
            ParsedToken(True, "raw", ["a"], ScopeAction.NONE, ["a"]),
            ParsedToken(True, "raw", [" "], ScopeAction.NONE, [" "]),
            ParsedToken(False, "error", ["{{#loop arg1 arg2} "], ScopeAction.NONE, list("{{#loop arg1 arg2} ")),
            ParsedToken(True, "raw", ["v"], ScopeAction.NONE, ["v"]),
            ParsedToken(True, "end", [], ScopeAction.NONE, [])
        ]

        actual_result = self.parse_stream(parser, test_stream)

        self.assert_parsed_tokens(actual_result, expected_result)

    def test_template_invalid_close_end_loop(self):
        parser = Parser()

        test_stream = io.StringIO("a {{/loop} v")

        expected_result = [
            ParsedToken(True, "raw", ["a"], ScopeAction.NONE, ["a"]),
            ParsedToken(True, "raw", [" "], ScopeAction.NONE, [" "]),
            ParsedToken(False, "error", ["{{/loop} "], ScopeAction.NONE, list("{{/loop} ")),
            ParsedToken(True, "raw", ["v"], ScopeAction.NONE, ["v"]),
            ParsedToken(True, "end", [], ScopeAction.NONE, [])
        ]

        actual_result = self.parse_stream(parser, test_stream)

        self.assert_parsed_tokens(actual_result, expected_result)

    @staticmethod
    def parse_stream(parser, test_stream):
        actual_result = []
        token = parser.parse_single_construct(test_stream)
        actual_result.append(token)
        while not token.function_name == "end":
            token = parser.parse_single_construct(test_stream)
            actual_result.append(token)
        return actual_result

    def assert_parsed_tokens(self, actual_result, expected_result):
        for expected, actual in zip(expected_result, actual_result):
            self.assertEqual(expected, actual)

if __name__ == '__main__':
    unittest.main()
