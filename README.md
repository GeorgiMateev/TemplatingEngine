# Templating Engine Documentation
The following engine reads a text stream and outputs the processed template in another stream.
The included command line script provides an easy way to run the engine for input and output files.

## Requirements
Python 3.7 is required to run the code because the new data classes feature is used. It provides easier way of creating data objects with built in way to compare them.

## How to use the engine

### From the command line
Run `main.py -h` for getting parameter details.

You can use the _main.py_ script like:  

`main.py -i ./sample_template.txt -o ./output.txt --variables={\"name\":\"MyTemplate\",\"vars\":[\"apple\",\"banana\"]}`

Where required parameters are:
 - **-i** is the path to the input template
 - **-o** is the path to the output file
 - **-v** is a json containing the variables used in the template
 
Additionally you can configure how the engine parses the template:

`main.py -i ./sample_template.txt -o ./output.txt --variables={\"name\":\"MyTemplate\",\"vars\":[\"apple\",\"banana\"]} --raise --func-open=# --func-close=* --template-open=## --template-close=##`  

 - **--template-open** defines the two characters that start a template. Default is _{{_ .
 - **--template-close** defines the two characters that close a template. Default is _}}_ .
 - **--func-open** one character that starts a function like _loop_. Default is _#_ .
 - **--func-close** one character that end a function like _loop_. Default is _/_ .
 - **--raise** raises error when there is invalid syntax like _{{arg} not closed_ . Without this flag the invalid syntax will be printed as is.
 
### Use as a package
1.  import the class **from src.engine.engine import TemplatingEngine** .
2. Instantiate new _TemplatingEngine_ . The required param is **global_variables**. You have to provide a dictionary with variables which will be used in the template. For variables used in loops provide a List.
3. call the **process** method with:
- **input_stream** - a text stream.
- **output_stream** - a text stream.  
Make sure to use buffering in the streams to improve the performance and reduce the IO operations in the underlying stream implementation.

## Supported template examples
### Print a variable
Just use `{{myvar}}` to print the value of the variable.

### Loops
You can define single or nested loops like:

`My breakfast could be :  
 {{#loop fruits fruit}}  
    {{#loop drinks drink}}  
       {{fruit}} with {{drink}} 
    {{/loop}}
 {{/loop}}`
 
### Invalid syntax
Invalid syntax like:  
`Invalid closing {{var}`  
or  
`just {{ brackets`  
or  
`loop {{#loop items}} with not enought args`  
or  
`loop close {{/loop args}} with args`

Will be just printed. If the **--raise** flag is provided an error will be thrown.

## Implementation details

### Real time stream processing
The templating engine works with streams which means that ones the engine process is started it will read characters one by one or hang until new characters appear in the stream.  
Each read character will be directly written to the output stream unless it is part of a template syntax and more characters are needed to parse the template.  
For example if a loop is initiated nothing will be written to the output until the whole loop body is read from the input.

### Template parser
The module **src.engine.parser** defines a string parser that produces tokens with information about what has been read. The token include:
- function name - print, loop, raw or error
- arguments in that function
- whether the function defines new scope of variables like (on loop start) or returns from such scope (on loop end)

### Engine
The module **src.engine.engine** uses the parser to interpret the input text and constructs a syntax tree where each syntax node is a function with arguments and a body containing collection of syntax nodes.

### Syntax tree processor
The module **src.engine.syntax_tree_processor** defines a processor that accepts a syntax tree and recursively traverse its nodes and executes each type of function with arguments. The execution converts single syntax node to the actual string output.