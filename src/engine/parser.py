from io import TextIOBase

from src.model.parsed_token import ParsedToken, ScopeAction


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

        # end of stream
        if char == '':
            return ParsedToken(True, "end", [], ScopeAction.NONE, [])

        read_sequence.append(char)

        has_template_open, current_read_sequence = self.try_parse_template_border(
            char,
            input_stream,
            self.template_opening)
        read_sequence += current_read_sequence

        if has_template_open:
            char = input_stream.read(1)
            read_sequence.append(char)

            if char == self.function_open:
                function_name, raw_text_read = self.parse_argument(
                    input_stream, " ")
                read_sequence += raw_text_read

                argument1, raw_text_read = self.parse_argument(input_stream, " ")
                read_sequence += raw_text_read

                argument2, raw_text_read = self.parse_argument(
                    input_stream,
                    self.template_closing[0])
                read_sequence += raw_text_read

                last_char = read_sequence[-1]
                has_template_close, current_read_sequence = self.try_parse_template_border(
                    last_char,
                    input_stream,
                    self.template_closing)
                read_sequence += current_read_sequence

                if has_template_close:
                    return ParsedToken(
                        True,
                        function_name,
                        [argument1, argument2],
                        ScopeAction.OPEN,
                        read_sequence)
                else:
                    return ParsedToken(
                        False,
                        'error',
                        [''.join(read_sequence)],
                        ScopeAction.NONE,
                        raw_text=read_sequence)
            elif char == self.function_close:
                function_name, raw_text_read = self.parse_argument(
                    input_stream,
                    self.template_closing[0])

                read_sequence += raw_text_read

                last_char = read_sequence[-1]

                has_template_close, current_read_sequence = self.try_parse_template_border(
                    last_char,
                    input_stream,
                    self.template_closing)
                read_sequence += current_read_sequence

                if has_template_close:
                    return ParsedToken(
                        True,
                        function_name,
                        [],
                        ScopeAction.CLOSE,
                        read_sequence)
                else:
                    return ParsedToken(
                        False,
                        'error',
                        [''.join(read_sequence)],
                        ScopeAction.NONE,
                        raw_text=read_sequence)
            else:
                argument, raw_text_read = self.parse_argument(
                    input_stream,
                    self.template_closing[0])
                argument = char + argument
                read_sequence += raw_text_read

                last_char = read_sequence[-1]

                has_template_close, current_read_sequence = self.try_parse_template_border(
                    last_char,
                    input_stream,
                    self.template_closing)

                read_sequence += current_read_sequence

                if has_template_close:
                    return ParsedToken(
                        True,
                        "print",
                        [argument],
                        ScopeAction.NONE,
                        read_sequence)
                return ParsedToken(
                    False,
                    'error',
                    [''.join(read_sequence)],
                    ScopeAction.NONE,
                    raw_text=read_sequence)

        else:
            return ParsedToken(
                True,
                "raw",
                [''.join(read_sequence)],
                ScopeAction.NONE,
                raw_text=read_sequence)

    @staticmethod
    def parse_argument(input_stream, stop_char):
        argument = []
        raw_text_read = []
        while True:
            char = input_stream.read(1)
            raw_text_read.append(char)

            if char == stop_char:
                break
            else:
                argument.append(char)
        return ''.join(argument), raw_text_read

    @staticmethod
    def try_parse_template_border(char, input_stream, template_border):
        read_sequence = []

        if char == template_border[0]:
            char = input_stream.read(1)
            read_sequence.append(char)

            return char == template_border[1], read_sequence
        else:
            return False, read_sequence
