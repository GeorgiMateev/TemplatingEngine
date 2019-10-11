import getopt
import json
import sys

from src.engine.engine import TemplatingEngine


def main(argv):
    try:
        opts, args = getopt.getopt(argv,
                                   "hi:o:v:",
                                   ["input-file=",
                                    "output-file=",
                                    "variables=",
                                    "template-open=",
                                    "template-close=",
                                    "func-open=",
                                    "func-close=",
                                    "raise"])
    except getopt.GetoptError:
        print_help()
        sys.exit(2)

    input_file = ''
    output_file = ''
    variables_json = ''
    additional_params = {}

    for opt, arg in opts:
        if opt == '-h':
            print_help()
            sys.exit()
        elif opt in ("-i", "--input-file"):
            input_file = arg
        elif opt in ("-o", "--output-file"):
            output_file = arg
        elif opt in ("-v", "--variables"):
            variables_json = arg
        elif opt == '--template-open':
            additional_params['template_open'] = arg
        elif opt == '--template-close':
            additional_params['template_close'] = arg
        elif opt == '--func-open':
            additional_params['function_open'] = arg
        elif opt == '--func-close':
            additional_params['function_close'] = arg
        elif opt == '--raise':
            additional_params['throw_invalid'] = True
            
    if not input_file:
        print("Please provide input file with -i or --input-file")
        sys.exit(2)

    if not output_file:
        print("Please provide input file with -o or --output-file")
        sys.exit(2)

    if not variables_json:
        print("Please provide template variables as json with -v or --variables")
        sys.exit(2)

    print('Input file is ', input_file)
    print('Output file is ', output_file)
    print('Variables: ', variables_json)

    variables = json.loads(variables_json)
    additional_params['global_variables'] = variables

    engine = TemplatingEngine(**additional_params)

    with open(input_file, 'r', 5120, 'utf-8') as input_stream:
        with open(output_file, 'w', 5120, 'utf-8') as output_stream:
            engine.process(input_stream, output_stream)


def print_help():
    print('main.py -i <inputfile> -o <outputfile> -v <variables json>')
    print('Optional params:')
    print('--template-open=<two characters for starting template, default: {{>')
    print('--template-close=<two characters for closing template, default: }}>')
    print('--func-open=<one character for starting special function, default: #>')
    print('--func-close=<one character for ending special function, default: />')
    print('--raise to raise error on invalid syntax')


if __name__ == "__main__":
    main(sys.argv[1:])
