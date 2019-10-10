import getopt
import json
import sys

from src.engine.engine import TemplatingEngine


def main(argv):
    input_file = ''
    output_file = ''
    variables_json = ''
    try:
        opts, args = getopt.getopt(argv,
                                   "hi:o:v:",
                                   ["input-file=", "output-file=", "variables="])
    except getopt.GetoptError:
        print('test.py -i <inputfile> -o <outputfile> -v <variables json>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('test.py -i <inputfile> -o <outputfile> -v <variables json>')
            sys.exit()
        elif opt in ("-i", "--input-file"):
            input_file = arg
        elif opt in ("-o", "--output-file"):
            output_file = arg
        elif opt in ("-v", "--variables"):
            variables_json = arg
            
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

    engine = TemplatingEngine(variables)

    with open(input_file, 'r', 5120, 'utf-8') as input_stream:
        with open(output_file, 'w', 5120, 'utf-8') as output_stream:
            engine.process(input_stream, output_stream)


if __name__ == "__main__":
    main(sys.argv[1:])
