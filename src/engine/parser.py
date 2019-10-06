from io import TextIOBase

from src.model.parsed_token import ParsedToken


class Parser:
    def __init__(self,
                 template_opening="{{",
                 function_open="#",
                 function_close="/",
                 template_closing="}}"):
        self.template_closing = template_closing
        self.function_close = function_close
        self.function_open = function_open
        self.template_opening = template_opening

    def parse_single_construct(self, input_stream: TextIOBase):
        read_sequence = []
        char = input_stream.read(1)
        read_sequence.append(char)

        has_template_open, current_read_sequence = self.try_parse_template_border(
            input_stream,
            self.template_opening)
        read_sequence += current_read_sequence
        if has_template_open:
            if char == self.function_open:
                function_name, raw_text_read = self.parse_argument(input_stream)
                read_sequence += raw_text_read

                argument1, raw_text_read = self.parse_argument(input_stream)
                read_sequence += raw_text_read

                argument2, raw_text_read = self.parse_argument(input_stream)
                read_sequence += raw_text_read

                has_template_close, current_read_sequence = self.try_parse_template_border(
                    input_stream,
                    self.template_closing)
                read_sequence += current_read_sequence

                if has_template_close:
                    return ParsedToken(
                        True,
                        function_name,
                        [argument1, argument2],
                        "open",
                        read_sequence)
                else:
                    return ParsedToken(
                        False,
                        raw_text=read_sequence)
            if char == self.function_close:
                function_name, raw_text_read = self.parse_argument(input_stream)
                read_sequence += raw_text_read

                char = input_stream.read(1)
                read_sequence.append(char)

                has_template_close, current_read_sequence = self.try_parse_template_border(
                    input_stream,
                    self.template_closing)
                read_sequence += current_read_sequence

                if has_template_close:
                    return ParsedToken(
                        True,
                        function_name,
                        [],
                        "close",
                        read_sequence)
                else:
                    return ParsedToken(
                        False,
                        raw_text=read_sequence)
            else:
                function_name, raw_text_read = self.parse_argument(input_stream)
                read_sequence += raw_text_read

                has_template_close, current_read_sequence = self.try_parse_template_border(
                    input_stream, self.template_closing)
                read_sequence += current_read_sequence

                if has_template_close:
                    return ParsedToken(
                        True,
                        "print",
                        [],
                        "none",
                        read_sequence)
                return ParsedToken(
                    False,
                    raw_text=read_sequence)

        else:
            return ParsedToken(
                True,
                "raw",
                [],
                "none",
                raw_text=read_sequence)

    @staticmethod
    def parse_argument(input_stream):
        argument = []
        raw_text_read = []
        while True:
            char = input_stream.read(1)
            raw_text_read.append(char)

            if char == ' ':
                break
            else:
                argument.append(char)
        return argument, raw_text_read

    @staticmethod
    def try_parse_template_border(input_stream, template_border):
        read_sequence = []
        char = input_stream.read(1)
        read_sequence.append(char)

        if char == template_border[0]:
            char = input_stream.read(1)
            read_sequence.append(char)

            if char == template_border[1]:
                char = input_stream.read(1)
                read_sequence.append(char)

                return True, read_sequence
            else:
                return False, read_sequence
        else:
            return False, read_sequence
