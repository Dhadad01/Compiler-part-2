"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import copy
import typing


class SymbolTable:
    """A symbol table that associates names with information needed for Jack
    compilation: type, kind and running index. The symbol table has two nested
    scopes (class/subroutine).
    """
    def __init__(self) -> None:
        """Creates a new empty symbol table."""
        # Your code goes here!
        self.subroutine_list={}
        self.var_counter={}
        self.class_symbol_table = {}

    def start_subroutine(self) -> None:
        """Starts a new subroutine scope (i.e., resets the subroutine's 
        symbol table).
        """
        # Your code goes here!
        self.subroutine_list={}
        new_key=copy.deepcopy(self.var_counter)
        for key in new_key:
            if key in ['argument','local']:
                self.var_counter.pop(key)

        #if type=='method':
            #pass



    def define(self, name: str, type: str, kind: str) -> None:
        """Defines a new identifier of a given name, type and kind and assigns 
        it a running index. "STATIC" and "FIELD" identifiers have a class scope, 
        while "ARG" and "VAR" identifiers have a subroutine scope.

        Args:
            name (str): the name of the new identifier.
            type (str): the type of the new identifier.
            kind (str): the kin--d of the new identifier, can be:
            "STATIC", "FIELD", "ARG", "VAR".
        """
        if kind in ('field','static'):
            self.class_symbol_table[name]=[type,kind,self.var_count(kind)]
            self.var_counter[kind] += 1
        elif kind in ('argument','local'):
            self.subroutine_list[name] =[type, kind, self.var_count(kind)]
            self.var_counter[kind] += 1




    def var_count(self, kind: str) -> int:
        """
        Args:
            kind (str): can be "STATIC", "FIELD", "ARG", "VAR".

        Returns:
            int: the number of variables of the given kind already defined in 
            the current scope.
        """
        # Your code goes here!
        if kind in self.var_counter:
            return self.var_counter[kind]
        else:
            self.var_counter[kind] = 0
            return self.var_counter[kind]

    def kind_of(self, name: str) -> str:
        """
        Args:
            name (str): name of an identifier.

        Returns:
            str: the kind of the named identifier in the current scope, or None
            if the identifier is unknown in the current scope.
        """
        if name in self.subroutine_list:
            return self.subroutine_list.get(name)[1]
        elif name in self.class_symbol_table:
            if self.class_symbol_table[name][1]=='field':
                return 'this'
            else:
                return self.class_symbol_table[name][1]
        else:
            return 'not'


    def type_of(self, name: str) -> str:
        """
        Args:
            name (str):  name of an identifier.

        Returns:
            str: the type of the named identifier in the current scope.
        """
        if name in self.subroutine_list:
            return self.subroutine_list.get(name)[0]
        elif name in self.class_symbol_table:
            return self.class_symbol_table[name][0]


    def index_of(self, name: str) -> int:
        """
        Args:
            name (str):  name of an identifier.

        Returns:
            int: the index assigned to the named identifier.
        """
        if name in self.subroutine_list:
            return self.subroutine_list.get(name)[2]
        elif name in self.class_symbol_table:
            return self.class_symbol_table[name][2]

