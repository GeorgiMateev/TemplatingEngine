import unittest

from src.engine import syntax_tree_processor as syntax_processor
from src.model.syntax_node import SyntaxNode
from src.model.syntax_tree import SyntaxTree


class SyntaxTreeProcessorTests(unittest.TestCase):
    def test_flat_raw_nodes(self):
        syntax_tree = SyntaxTree()

        syntax_tree.add_node_to_current_level(SyntaxNode("raw", ["a"]))
        syntax_tree.add_node_to_current_level(SyntaxNode("raw", [" "]))
        syntax_tree.add_node_to_current_level(SyntaxNode("raw", ["test"]))
        syntax_tree.add_node_to_current_level(SyntaxNode("raw", [" "]))
        syntax_tree.add_node_to_current_level(SyntaxNode("raw", ["string"]))
        syntax_tree.add_node_to_current_level(SyntaxNode("raw", ["!"]))

        expected_result = "a test string!"

        variables = {}
        throw_invalid_syntax = False
        actual_result = syntax_processor.process_syntax_tree(
            syntax_tree,
            variables,
            throw_invalid_syntax)

        self.assertEqual(expected_result, actual_result)

    def test_flat_print_nodes(self):
        syntax_tree = SyntaxTree()

        syntax_tree.add_node_to_current_level(SyntaxNode("raw", ["a"]))
        syntax_tree.add_node_to_current_level(SyntaxNode("raw", [" "]))
        syntax_tree.add_node_to_current_level(SyntaxNode("print", ["var1"]))
        syntax_tree.add_node_to_current_level(SyntaxNode("print", ["var2"]))
        syntax_tree.add_node_to_current_level(SyntaxNode("print", ["var3"]))

        expected_result = "a test string"

        variables = {"var1": "test", "var2": " ", "var3": "string"}
        throw_invalid_syntax = False
        actual_result = syntax_processor.process_syntax_tree(
            syntax_tree,
            variables,
            throw_invalid_syntax)

        self.assertEqual(expected_result, actual_result)

    def test_loop_nodes(self):
        syntax_tree = SyntaxTree()

        syntax_tree.add_node_to_current_level(SyntaxNode("raw", ["loop"]))
        syntax_tree.add_node_to_current_level(SyntaxNode("raw", [" over:"]))

        syntax_tree.branch_with_new_node(
            SyntaxNode("loop", ["fruits", "fruit"]))

        syntax_tree.add_node_to_current_level(SyntaxNode("raw", [" "]))
        syntax_tree.add_node_to_current_level(SyntaxNode("print", ["fruit"]))
        syntax_tree.add_node_to_current_level(SyntaxNode("print", ["separator"]))

        syntax_tree.return_to_upper_level()

        syntax_tree.add_node_to_current_level(SyntaxNode("raw", ["!"]))

        expected_result = "loop over: apples, bananas, pie,!"

        variables = {
            "fruits": ["apples", "bananas", "pie"],
            "separator": ","
        }
        throw_invalid_syntax = False
        actual_result = syntax_processor.process_syntax_tree(
            syntax_tree,
            variables,
            throw_invalid_syntax)

        self.assertEqual(expected_result, actual_result)

    def test_nested_loop_nodes(self):
        syntax_tree = SyntaxTree()

        syntax_tree.add_node_to_current_level(SyntaxNode("raw", ["loop"]))
        syntax_tree.add_node_to_current_level(SyntaxNode("raw", [" over: "]))

        syntax_tree.branch_with_new_node(SyntaxNode("loop", ["fruits", "fruit"]))

        syntax_tree.add_node_to_current_level(SyntaxNode("raw", ["combo:"]))

        syntax_tree.branch_with_new_node(SyntaxNode("loop", ["drinks", "drink"]))

        syntax_tree.add_node_to_current_level(SyntaxNode("raw", [" "]))
        syntax_tree.add_node_to_current_level(SyntaxNode("print", ["fruit"]))
        syntax_tree.add_node_to_current_level(SyntaxNode("print", ["colon"]))
        syntax_tree.add_node_to_current_level(SyntaxNode("print", ["drink"]))
        syntax_tree.add_node_to_current_level(SyntaxNode("print", ["separator"]))

        syntax_tree.return_to_upper_level()

        syntax_tree.add_node_to_current_level(SyntaxNode("raw", [" or "]))

        syntax_tree.return_to_upper_level()

        syntax_tree.add_node_to_current_level(SyntaxNode("raw", ["!"]))

        expected_result = "loop over: combo: apples-water, apples-beer, or combo: bananas-water, bananas-beer, or !"

        variables = {
            "drinks": ["water", "beer"],
            "fruits": ["apples", "bananas"],
            "separator": ",",
            "colon": "-"
        }
        throw_invalid_syntax = False
        actual_result = syntax_processor.process_syntax_tree(
            syntax_tree,
            variables,
            throw_invalid_syntax)

        self.assertEqual(expected_result, actual_result)

    def test_error_node(self):
        syntax_tree = SyntaxTree()

        syntax_tree.add_node_to_current_level(SyntaxNode("raw", ["an"]))
        syntax_tree.add_node_to_current_level(SyntaxNode("raw", [" "]))
        syntax_tree.add_node_to_current_level(SyntaxNode("error", ["{{error}"]))

        expected_result = "an {{error}"

        variables = {}
        throw_invalid_syntax = False
        actual_result = syntax_processor.process_syntax_tree(
            syntax_tree,
            variables,
            throw_invalid_syntax)

        self.assertEqual(expected_result, actual_result)

    def test_error_node_should_raise(self):
        syntax_tree = SyntaxTree()

        syntax_tree.add_node_to_current_level(SyntaxNode("raw", ["an"]))
        syntax_tree.add_node_to_current_level(SyntaxNode("raw", [" "]))
        syntax_tree.add_node_to_current_level(SyntaxNode("error", ["{{error}"]))

        variables = {}
        throw_invalid_syntax = True

        self.assertRaises(ValueError,
                          syntax_processor.process_syntax_tree,
                          syntax_tree,
                          variables,
                          throw_invalid_syntax)

    def test_loop_invalid_variable_not_found(self):
        syntax_tree = SyntaxTree()

        syntax_tree.branch_with_new_node(
            SyntaxNode("loop", ["fruits", "fruit"]))

        syntax_tree.add_node_to_current_level(SyntaxNode("print", ["fruit"]))

        syntax_tree.return_to_upper_level()

        variables = {
        }
        throw_invalid_syntax = False
        self.assertRaises(ValueError,
                          syntax_processor.process_syntax_tree,
                          syntax_tree,
                          variables,
                          throw_invalid_syntax)

    def test_loop_invalid_variable_not_sequence(self):
        syntax_tree = SyntaxTree()

        syntax_tree.branch_with_new_node(
            SyntaxNode("loop", ["fruits", "fruit"]))

        syntax_tree.add_node_to_current_level(SyntaxNode("print", ["fruit"]))

        syntax_tree.return_to_upper_level()

        variables = {
            "fruits": "not a sequence"
        }

        throw_invalid_syntax = False
        self.assertRaises(ValueError,
                          syntax_processor.process_syntax_tree,
                          syntax_tree,
                          variables,
                          throw_invalid_syntax)


if __name__ == '__main__':
    unittest.main()
