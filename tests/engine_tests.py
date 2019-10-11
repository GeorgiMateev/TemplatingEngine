import io
import unittest

from src.engine.engine import TemplatingEngine


class E2EEngineTests(unittest.TestCase):
    def test_empty(self):
        test_stream = io.StringIO("")

        variables = {}
        engine = TemplatingEngine(variables)

        output = io.StringIO()
        engine.process(test_stream, output)

        expected = ""
        actual = output.getvalue()

        self.assertEqual(expected, actual)

    def test_single_variable(self):
        test_stream = io.StringIO("a {{arg}} v")

        variables = {"arg": "test"}
        engine = TemplatingEngine(variables)

        output = io.StringIO()
        engine.process(test_stream, output)

        expected = "a test v"
        actual = output.getvalue()

        self.assertEqual(expected, actual)

    def test_template_symbols_only(self):
        test_stream = io.StringIO("{{#loop list item}}{{item}}{{/loop}}")

        variables = {"list": ["1", "2", "3"]}
        engine = TemplatingEngine(variables)

        output = io.StringIO()
        engine.process(test_stream, output)

        expected = "123"
        actual = output.getvalue()

        self.assertEqual(expected, actual)

    def test_loop(self):
        test_stream = io.StringIO(''.join([
            "First line.",
            "{{header}}",
            "{{#loop somearray item}}",
            "This is a {{item}}.",
            "{{/loop}}",
            "{{footer}}",
            "Last line."]))

        variables = {
            "header": "Hello!",
            "somearray": ["apple", "banana", "citrus"],
            "footer": "That's it!"
        }

        engine = TemplatingEngine(variables)

        output = io.StringIO()
        engine.process(test_stream, output)

        expected = ''.join(["First line.",
                            "Hello!",
                            "This is a apple.",
                            "This is a banana.",
                            "This is a citrus.",
                            "That's it!",
                            "Last line."])

        actual = output.getvalue()

        self.assertEqual(expected, actual)

    def test_nested_loop(self):
        test_stream = io.StringIO(''.join([
            "First line.",
            "{{header}}",
            "{{#loop somearray item}}",
                "This is a {{item}}.",
                "You can combine:",
                    "{{#loop food item2}}",
                        "{{item}} - {{item2}}"
                    "{{/loop}}"
            "{{/loop}}",
            "{{footer}}",
            "Last line."]))

        variables = {
            "header": "Hello!",
            "somearray": ["apple", "banana"],
            "food": ["chicken", "pie"],
            "footer": "That's it!"
        }

        engine = TemplatingEngine(variables)

        output = io.StringIO()
        engine.process(test_stream, output)

        expected = ''.join(["First line.",
                            "Hello!",
                            "This is a apple.",
                            "You can combine:"
                            "apple - chicken",
                            "apple - pie",
                            "This is a banana.",
                            "You can combine:",
                            "banana - chicken",
                            "banana - pie",
                            "That's it!",
                            "Last line."])

        actual = output.getvalue()

        self.assertEqual(expected, actual)

    def test_invalid_template(self):
        test_stream = io.StringIO("text with {{that is not template")

        variables = {
            "that": "variable"
        }

        engine = TemplatingEngine(variables)

        output = io.StringIO()
        engine.process(test_stream, output)

        expected = "text with {{that is not template"

        actual = output.getvalue()

        self.assertEqual(expected, actual)

    def test_loop_invalid_template_no_arguments(self):
        test_stream = io.StringIO("text with {{#loop var}} .")

        variables = {
            "var": ["variable", "variable1"]
        }

        engine = TemplatingEngine(variables)

        output = io.StringIO()
        engine.process(test_stream, output)

        expected = "text with {{#loop var}} ."

        actual = output.getvalue()

        self.assertEqual(expected, actual)

    def test_loop_invalid_template_no_arguments_raise_error(self):
        test_stream = io.StringIO("text with {{#loop var}} .")

        variables = {
            "var": ["variable", "variable1"]
        }

        engine = TemplatingEngine(variables, throw_invalid=True)

        output = io.StringIO()

        self.assertRaises(ValueError, engine.process, test_stream, output)

    def test_loop_different_template_symbols(self):
        test_stream = io.StringIO(''.join([
            "First line.",
            "<<header>>",
            "<<*loop somearray item>>",
            "This is a <<item>>.",
            "<<@loop>>",
            "<<footer>>",
            "Last line."]))

        variables = {
            "header": "Hello!",
            "somearray": ["apple", "banana", "citrus"],
            "footer": "That's it!"
        }

        template_opening = "<<"
        template_close = ">>"
        function_open = "*"
        function_close = "@"
        engine = TemplatingEngine(variables, template_opening, template_close,
                                  function_open, function_close)

        output = io.StringIO()
        engine.process(test_stream, output)

        expected = ''.join(["First line.",
                            "Hello!",
                            "This is a apple.",
                            "This is a banana.",
                            "This is a citrus.",
                            "That's it!",
                            "Last line."])

        actual = output.getvalue()

        self.assertEqual(expected, actual)


if __name__ == '__main__':
    unittest.main()
