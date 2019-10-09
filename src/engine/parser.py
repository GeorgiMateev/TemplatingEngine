from typing import TextIO

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

    def parse_single_token(self, input_stream: TextIO):
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
                args = []
                for i in range(3):
                    if i == 2:
                        char_end = self.template_closing[0]
                        invalid_char_end = " "
                    else:
                        char_end = " "
                        invalid_char_end = self.template_closing[0]

                    has_argument, argument, raw_text_read = self.try_parse_argument(
                        input_stream,
                        char_end,
                        invalid_char_end)

                    read_sequence += raw_text_read

                    if not has_argument:
                        return ParsedToken(
                            False,
                            'error',
                            [''.join(read_sequence)],
                            ScopeAction.NONE,
                            raw_text=read_sequence)

                    args.append(argument)

                last_char = read_sequence[-1]
                has_template_close, current_read_sequence = self.try_parse_template_border(
                    last_char,
                    input_stream,
                    self.template_closing)
                read_sequence += current_read_sequence

                if has_template_close:
                    function_name, argument1, argument2 = args
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
                has_function_name, function_name, raw_text_read = self.try_parse_argument(
                    input_stream,
                    self.template_closing[0],
                    " ")

                read_sequence += raw_text_read

                if not has_function_name:
                    return ParsedToken(
                        False,
                        'error',
                        [''.join(read_sequence)],
                        ScopeAction.NONE,
                        raw_text=read_sequence)

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
                has_argument, argument, raw_text_read = self.try_parse_argument(
                    input_stream,
                    self.template_closing[0],
                    " ")
                argument = char + argument
                read_sequence += raw_text_read

                if not has_argument:
                    return ParsedToken(
                        False,
                        'error',
                        [''.join(read_sequence)],
                        ScopeAction.NONE,
                        raw_text=read_sequence)

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
    def try_parse_argument(input_stream, stop_char, invalid_char):
        argument = []
        raw_text_read = []
        while True:
            char = input_stream.read(1)
            raw_text_read.append(char)

            if char == stop_char:
                break
            elif char == invalid_char:
                return False, ''.join(argument), raw_text_read
            else:
                argument.append(char)
        return True, ''.join(argument), raw_text_read

    @staticmethod
    def try_parse_template_border(char, input_stream, template_border):
        read_sequence = []

        if char == template_border[0]:
            char = input_stream.read(1)
            read_sequence.append(char)

            return char == template_border[1], read_sequence
        else:
            return False, read_sequence
