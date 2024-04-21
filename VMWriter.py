"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing


class VMWriter:
    """
    Writes VM commands into a file. Encapsulates the VM command syntax.
    """

    def __init__(self, output_stream: typing.TextIO) -> None:
        """Creates a new file and prepares it for writing VM commands."""
        # Your code goes here!
        # Note that you can write to output_stream like so:
        # output_stream.write("Hello world! \n")
        self.output_file=output_stream

    def write_push(self, segment: str, index: int) -> None:
        """Writes a VM push command.

        Args:
            segment (str): the segment to push to, can be "CONST", "ARG", 
            "LOCAL", "STATIC", "THIS", "THAT", "POINTER", "TEMP"
            index (int): the index to push to.
        """
        writelist=['push',' ',segment,' ',index]
        for i in writelist:
            self.output_file.write(str(i))
        self.output_file.write('\n')

    def write_pop(self, segment: str, index: int) -> None:
        """Writes a VM pop command.

        Args:
            segment (str): the segment to pop from, can be "CONST", "ARG", 
            "LOCAL", "STATIC", "THIS", "THAT", "POINTER", "TEMP".
            index (int): the index to pop from.
        """
        writelist = ['pop',' ',str(segment),' ',str(index)]
        for i in writelist:
            self.output_file.write(i)
        self.output_file.write('\n')

    def write_arithmetic(self, command: str,sign=None) -> None:
        """Writes a VM arithmetic command.

        Args:
            command (str): the command to write, can be "ADD", "SUB", "NEG", 
            "EQ", "GT", "LT", "AND", "OR", "NOT", "SHIFTLEFT", "SHIFTRIGHT".
        """
        if sign:
            write_arithmetic_dic = {'+': 'add', '-': 'neg', '=': 'eq', '>': 'gt', '<': 'lt', '&': 'and', '|': 'or',
                                    '~': 'not', '^': 'shiftleft', '#': 'shiftright','*': 'call Math.multiply 2','/': 'call Math.divide 2'}
            self.output_file.write(write_arithmetic_dic[command])
            self.output_file.write('\n')
        else:
            write_arithmetic_dic = {'+': 'add', '-': 'sub', '=': 'eq', '>': 'gt', '<': 'lt', '&': 'and', '|': 'or',
                                    '~': 'not', '^': 'shiftleft', '#': 'shiftright','*': 'call Math.multiply 2','/': 'call Math.divide 2'}
            #self.write_arithmetic_dic={'add':'+','sub':'-','eq':'=','gt':'>','lt':'<','and':'&','or':'|'}
            ##איך זה אמור לעבוד אם אנחנו מקבלים את הסמל שלו ולא את המילה??
            self.output_file.write(write_arithmetic_dic[command])
            self.output_file.write('\n')

    def write_label(self, label: str) -> None:
        """Writes a VM label command.

        Args:
            label (str): the label to write.
        """
        self.output_file.write("label "+label)
        self.output_file.write('\n')

    def write_goto(self, label: str) -> None:
        """Writes a VM goto command.

        Args:
            label (str): the label to go to.
        """
        writelist = ['goto',' ',label]
        for i in writelist:
            self.output_file.write(i)
        self.output_file.write('\n')

    def write_if(self, label: str) -> None:
        """Writes a VM if-goto command.

        Args:
            label (str): the label to go to.
        """
        writelist = ['if-goto',' ',label]
        for i in writelist:
            self.output_file.write(i)
        self.output_file.write('\n')


    def write_call(self, name: str, n_args: int) -> None:
        """Writes a VM call command.

        Args:
            name (str): the name of the function to call.
            n_args (int): the number of arguments the function receives.
        """
        # Your code goes here!
        writelist = ['call',' ',str(name),' ',str(n_args)]
        for i in writelist:
            self.output_file.write(i)
        self.output_file.write('\n')

    def write_function(self, name: str, n_locals: int) -> None:
        """Writes a VM function command.

        Args:
            name (str): the name of the function.
            n_locals (int): the number of local variables the function uses.
        """
        writelist = ['function',' ',str(name),' ',str(n_locals)]
        for i in writelist:
            self.output_file.write(i)
        self.output_file.write('\n')

    def write_return(self) -> None:
        """Writes a VM return command."""
        self.output_file.write('return')
        self.output_file.write('\n')
