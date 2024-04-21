"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing
import re

OP_LIST = ["+", "-", "*", "/", "&", "|", "<", ">", "="]
POSSIBLE_KEYWORDS = ['class', 'constructor', 'function', 'method', 'field', 'static', 'var', 'int',
                     'char', 'boolean', 'void', 'true', 'false', 'null', 'this', 'let', 'do', 'if',
                     'else', 'while', 'return']
POSSIBLE_SIMBOLS = ['{', '}', '(', ')', '[', ']', '.', ',', ';', '+',
                    '-', '*', '/', '&', '|', '<', '>', '=', '~', '^', '#']
UNARY_OP = ['-', '~', '^', '#']


class JackTokenizer:
    """Removes all comments from the input stream and breaks it
    into Jack language tokens, as specified by the Jack grammar.

    # Jack Language Grammar

    A Jack file is a stream of characters. If the file represents a
    valid program, it can be tokenized into a stream of valid tokens. The
    tokens may be separated by an arbitrary number of whitespace characters,
    and comments, which are ignored. There are three possible comment formats:
    /* comment until closing */ , /** API comment until closing */ , and
    // comment until the line’s end.

    - ‘xxx’: quotes are used for tokens that appear verbatim (‘terminals’).
    - xxx: regular typeface is used for names of language constructs
           (‘non-terminals’).
    - (): parentheses are used for grouping of language constructs.
    - x | y: indicates that either x or y can appear.
    - x?: indicates that x appears 0 or 1 times.
    - x*: indicates that x appears 0 or more times.

    ## Lexical Elements

    The Jack language includes five types of terminal elements (tokens).

    - keyword: 'class' | 'constructor' | 'function' | 'method' | 'field' |
               'static' | 'var' | 'int' | 'char' | 'boolean' | 'void' | 'true' |
               'false' | 'null' | 'this' | 'let' | 'do' | 'if' | 'else' |
               'while' | 'return'
    - symbol: '{' | '}' | '(' | ')' | '[' | ']' | '.' | ',' | ';' | '+' |
              '-' | '*' | '/' | '&' | '|' | '<' | '>' | '=' | '~' | '^' | '#'
    - integerConstant: A decimal number in the range 0-32767.
    - StringConstant: '"' A sequence of Unicode characters not including
                      double quote or newline '"'
    - identifier: A sequence of letters, digits, and underscore ('_') not
                  starting with a digit. You can assume keywords cannot be
                  identifiers, so 'self' cannot be an identifier, etc'.

    ## Program Structure

    A Jack program is a collection of classes, each appearing in a separate
    file. A compilation unit is a single class. A class is a sequence of tokens
    structured according to the following context free syntax:

    - class: 'class' className '{' classVarDec* subroutineDec* '}'
    - classVarDec: ('static' | 'field') type varName (',' varName)* ';'
    - type: 'int' | 'char' | 'boolean' | className
    - subroutineDec: ('constructor' | 'function' | 'method') ('void' | type)
    - subroutineName '(' parameterList ')' subroutineBody
    - parameterList: ((type varName) (',' type varName)*)?
    - subroutineBody: '{' varDec* statements '}'
    - varDec: 'var' type varName (',' varName)* ';'
    - className: identifier
    - subroutineName: identifier
    - varName: identifier

    ## Statements

    - statements: statement*
    - statement: letStatement | ifStatement | whileStatement | doStatement |
                 returnStatement
    - letStatement: 'let' varName ('[' expression ']')? '=' expression ';'
    - ifStatement: 'if' '(' expression ')' '{' statements '}' ('else' '{'
                   statements '}')?
    - whileStatement: 'while' '(' 'expression' ')' '{' statements '}'
    - doStatement: 'do' subroutineCall ';'
    - returnStatement: 'return' expression? ';'

    ## Expressions

    - expression: term (op term)*
    - term: integerConstant | stringConstant | keywordConstant | varName |
            varName '['expression']' | subroutineCall | '(' expression ')' |
            unaryOp term
    - subroutineCall: subroutineName '(' expressionList ')' | (className |
                      varName) '.' subroutineName '(' expressionList ')'
    - expressionList: (expression (',' expression)* )?
    - op: '+' | '-' | '*' | '/' | '&' | '|' | '<' | '>' | '='
    - unaryOp: '-' | '~' | '^' | '#'
    - keywordConstant: 'true' | 'false' | 'null' | 'this'

    Note that ^, # correspond to shiftleft and shiftright, respectively.
    """
    """Opens the input stream and gets ready to tokenize it.
            Args:
                input_stream (typing.TextIO): input stream.
            """

    # Your code goes here!
    # A good place to start is to read all the lines of the input:
    # input_lines = input_stream.read().splitlines()
    def __init__(self, input_stream: typing.TextIO) -> None:

        self.input_lines_list = input_stream.read().splitlines()
        self.source = []
        self.comment = False
        for line in range(len(self.input_lines_list)):
            remove_from = self.find_first_occurrence_outside_quotes(self.input_lines_list[line], "//")
            if remove_from != -1:
                self.input_lines_list[line] = self.input_lines_list[line][:remove_from]

            first_remove = self.find_first_occurrence_outside_quotes(self.input_lines_list[line], "/*")
            second_remove = self.find_first_occurrence_outside_quotes(self.input_lines_list[line], "*/")
            if first_remove != -1 and second_remove == -1:
                self.comment = True
            if second_remove != -1:
                self.comment = False
            if self.comment:
                continue
            if first_remove != -1:
                if second_remove != -1:
                    self.input_lines_list[line] = \
                        self.input_lines_list[line][:first_remove] + self.input_lines_list[line][second_remove + 2:]
                else:
                    self.input_lines_list[line] = self.input_lines_list[line] = self.input_lines_list[line][
                                                                                :first_remove]
            elif second_remove != -1:
                self.input_lines_list[line] = self.input_lines_list[line] = self.input_lines_list[line][
                                                                            second_remove + 2:]
            if self.input_lines_list[line] == '\n' or self.input_lines_list[line] == '':
                continue
            elif self.input_lines_list[line][0] == '/':
                continue
            strings = []
            counter = 1
            what_string_need = 0
            tokens_lst = []
            while '"' in self.input_lines_list[line]:
                tokens_lst.append(
                    self.input_lines_list[line][:self.find_nth(self.input_lines_list[line], '"', counter)])
                tokens_lst.append("STRING")
                new_str = self.input_lines_list[line][
                          self.find_nth(self.input_lines_list[line], '"', counter):self.find_nth(
                              self.input_lines_list[line], '"', counter + 1)]
                self.input_lines_list[line] = self.input_lines_list[line][self.find_nth(
                    self.input_lines_list[line], '"', counter + 1):]
                counter += 2
                strings.append(new_str)
            else:
                tokens_lst.extend(self.input_lines_list[line].split())
                for chunk in tokens_lst:
                    if chunk and chunk != '':
                        if chunk == "STRING":
                            self.source.append(strings[what_string_need])
                            what_string_need += 1
                        else:
                            self.source.extend(re.findall(r"[\w]+|[,;~.^{}<>#*-|/&+\[\]()\d=]", chunk))
        while '' in self.source:
            self.source.remove('')
        #print(self.source)
        self.command = -1

    def find_first_occurrence_outside_quotes(self, s, substring):
        inside_quotes = False
        for i, c in enumerate(s):
            if c == '"':
                inside_quotes = not inside_quotes
            elif c == substring[0] and not inside_quotes:
                if s[i:i + len(substring)] == substring:
                    return i
        return -1

    def find_nth(self, str, sub_str, n):
        start = str.find(sub_str)
        while start >= 0 and n > 1:
            start = str.find(sub_str, start + len(sub_str))
            n -= 1
        return start

    def has_more_tokens(self) -> bool:
        """Do we have more tokens in the input?

        Returns:
            bool: True if there are more tokens, False otherwise.
        """
        # Your code goes here!
        return not (len(self.source) - 1 == self.command)

    def advance(self) -> None:
        """Gets the next token from the input and makes it the current token.
        This method should be called if has_more_tokens() is true.
        Initially there is no current token.
        """
        # Your code goes here!
        self.command += 1
        self.current_instruction = self.source[self.command]

    def token_type(self) -> str:
        """
        Returns:
            str: the type of the current token, can be
            "KEYWORD", "SYMBOL", "IDENTIFIER", "INT_CONST", "STRING_CONST"
        """
        # Your code goes here!
        if self.current_instruction in POSSIBLE_KEYWORDS:
            return 'keyword'
        elif self.current_instruction in POSSIBLE_SIMBOLS:
            return 'symbol'
        elif self.current_instruction.isdigit() and int(self.current_instruction) in range(0, 32768):
            return 'integerConstant'
        elif self.current_instruction[0] == "\"":
            return "stringConstant"
        else:
            return "identifier"

    def keyword(self) -> str:
        """
        Returns:
            str: the keyword which is the current token.
            Should be called only when token_type() is "KEYWORD".
            Can return "CLASS", "METHOD", "FUNCTION", "CONSTRUCTOR", "INT",
            "BOOLEAN", "CHAR", "VOID", "VAR", "STATIC", "FIELD", "LET", "DO",
            "IF", "ELSE", "WHILE", "RETURN", "TRUE", "FALSE", "NULL", "THIS"
        """
        # Your code goes here!
        return self.current_instruction.upper()

    def symbol(self) -> str:
        """
        Returns:
            str: the character which is the current token.
            Should be called only when token_type() is "SYMBOL".
            Recall that symbol was defined in the grammar like so:
            symbol: '{' | '}' | '(' | ')' | '[' | ']' | '.' | ',' | ';' | '+' |
              '-' | '*' | '/' | '&' | '|' | '<' | '>' | '=' | '~' | '^' | '#'
        """
        # Your code goes here!
        return self.current_instruction

    def identifier(self) -> str:
        """
        Returns:
            str: the identifier which is the current token.
            Should be called only when token_type() is "IDENTIFIER".
            Recall that identifiers were defined in the grammar like so:
            identifier: A sequence of letters, digits, and underscore ('_') not
                  starting with a digit. You can assume keywords cannot be
                  identifiers, so 'self' cannot be an identifier, etc'.
        """
        # Your code goes here!
        return self.current_instruction

    def int_val(self) -> int:
        """
        Returns:
            str: the integer value of the current token.
            Should be called only when token_type() is "INT_CONST".
            Recall that integerConstant was defined in the grammar like so:
            integerConstant: A decimal number in the range 0-32767.
        """
        # Your code goes here!
        return int(self.current_instruction)

    def string_val(self) -> str:
        """
        Returns:
            str: the string value of the current token, without the double
            quotes. Should be called only when token_type() is "STRING_CONST".
            Recall that StringConstant was defined in the grammar like so:
            StringConstant: '"' A sequence of Unicode characters not including
                      double quote or newline '"'
        """
        # Your code goes here!
        return self.current_instruction[1:-1]
