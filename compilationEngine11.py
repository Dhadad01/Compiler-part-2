
from JackTokenizer import *
from SymbolTable import *
from VMWriter import *
write_arithmetic_dic={'+': 'add', '-': 'sub', '=': 'eq', '>': 'gt', '<': 'lt', '&': 'and', '|': 'or', '~': 'not'}
class CompilationEngine:
    def __init__(self, input_file_path, output_path):
        self.indentation = 0
        self.input_stream = input_file_path
        self.output = output_path
        self.vm=VMWriter(self.output)
        self.connum=0
        self.array=False
        self.debug=0
        self.void=False

    def compile_class(self):###
        if self.input_stream.has_more_tokens():
            self.input_stream.advance()
            self.symbol=SymbolTable()
            self.input_stream.advance()
            self.name_of_class=self.input_stream.current_instruction
            self.input_stream.advance()
            self.input_stream.advance()
            while self.input_stream.current_instruction == "static" or \
                    self.input_stream.current_instruction == "field":
                self.compile_class_var_dec()
            while self.input_stream.current_instruction == "constructor" or \
                    self.input_stream.current_instruction == "function" \
                    or self.input_stream.current_instruction == "method":
                self.compile_subroutine()

    def compile_class_var_dec(self):###
        """
        this should only print if there actually are class var decs,
        should run on the recursively
        :return:
        """
        kind = self.input_stream.current_instruction
        self.input_stream.advance()
        type = self.input_stream.current_instruction
        self.input_stream.advance()
        name = self.input_stream.current_instruction
        self.symbol.define(name, type, kind)
        self.input_stream.advance()
        while self.input_stream.current_instruction == ',':
            self.input_stream.advance()
            self.symbol.define(self.input_stream.current_instruction, type, kind)
            self.input_stream.advance()
        self.input_stream.advance()


    def compile_subroutine(self):###
        self.symbol.start_subroutine()###check local static symbol table notsure
        subroutine_type=self.input_stream.current_instruction
        self.input_stream.advance()
        second_word = self.input_stream.current_instruction
        if second_word=='void':
            self.void=True
        if subroutine_type == 'constructor':
            self.current_constructor = self.input_stream.current_instruction##type constructor notsure
            self.input_stream.advance()
            self.name_of_constructor = self.current_constructor + '.' + self.input_stream.current_instruction
            self.input_stream.advance()
            self.input_stream.advance()
        if subroutine_type=='method':
            self.input_stream.advance()
            self.name_of_method = self.name_of_class + '.' + self.input_stream.current_instruction
            self.symbol.define('this',self.name_of_class,'argument')
            self.input_stream.advance()
            self.input_stream.advance()
        if subroutine_type == 'function':
            self.input_stream.advance()
            self.name_of_function= self.name_of_class+'.'+self.input_stream.current_instruction
            self.input_stream.advance()
            self.input_stream.advance()
        self.compile_parameter_list()
        #if subroutine_type=='function':
            #self.vm.write_function(self.name_of_function,self.compile_paramater_list_counter)
        #self.input_stream.advance()  # one time or twice?
        #self.input_stream.advance()
        self.input_stream.advance()  # one time or twice?
        self.input_stream.advance()
        while self.input_stream.current_instruction == "var":
            self.compile_var_dec()
            self.input_stream.advance()
        if subroutine_type == 'function':
            self.vm.write_function(self.name_of_function, self.symbol.var_count('local'))
        elif subroutine_type == 'method':
            self.vm.write_function(self.name_of_method, self.symbol.var_count('local'))
            self.vm.write_push('argument', 0)
            self.vm.write_pop('pointer', 0)
        elif subroutine_type == 'constructor':
            self.vm.write_function(self.name_of_constructor, self.symbol.var_count('local'))
            self.vm.write_push('constant', self.symbol.var_count('field'))
            self.vm.write_call('Memory.alloc', 1)
            self.vm.write_pop('pointer', 0)
        self.compile_statements()
        self.input_stream.advance()
        if self.void:
            self.vm.write_push('constant',0)
            self.vm.write_return()
            self.void=False

    def compile_parameter_list(self):###
        self.compile_paramater_list_counter=0
        while self.input_stream.current_instruction not in POSSIBLE_SIMBOLS:
            self.compile_paramater_list_counter+=1
            type=self.input_stream.current_instruction
            self.input_stream.advance()
            name=self.input_stream.current_instruction
            self.symbol.define(name,type,'argument')
            self.input_stream.advance()
            if self.input_stream.current_instruction==')':
                break
            else:
                self.input_stream.advance()


    def compile_var_dec(self):###
        self.input_stream.advance()
        type=self.input_stream.current_instruction
        self.input_stream.advance()
        name=self.input_stream.current_instruction
        self.symbol.define(name,type,'local')
        self.input_stream.advance()
        while self.input_stream.current_instruction == ',':
            self.input_stream.advance()
            self.symbol.define(self.input_stream.current_instruction, type, 'local')
            self.input_stream.advance()


    #def _compile_type_and_varName(self):
        #self.new_eat()
        #self.input_stream.advance()
        #self.new_eat()
        #self.input_stream.advance()
        #while self.input_stream.current_instruction == ",":
            #self.new_eat()
           #self.input_stream.advance()
            #self.new_eat()
            #self.input_stream.advance()
        #self.new_eat()
        #self.input_stream.advance()

    def compile_statements(self):###
        while self.input_stream.current_instruction in ['let', 'if', 'while', 'do', 'return']:
            if self.input_stream.current_instruction == 'let':
                self.compile_let()
            elif self.input_stream.current_instruction == 'if':
                self.compile_if()
            elif self.input_stream.current_instruction == 'while':
                self.compile_while()
            elif self.input_stream.current_instruction == 'do':
                self.compile_do()
            elif self.input_stream.current_instruction == 'return':
                self.compile_return()

    def compile_do(self):###
        self.input_stream.advance()
        current_token=self.input_stream.current_instruction
        # subroutineCall
        self.input_stream.advance()
        if self.input_stream.symbol() == ".":
            obj = self.symbol.kind_of(current_token)
            if obj !='not':
                self.input_stream.advance()
                if self.input_stream.current_instruction != 'new':## do p1.new('m,p') notsure
                    obj=self.symbol.kind_of(current_token)
                    function_name = self.symbol.type_of(current_token)+'.'+self.input_stream.current_instruction
                    self.input_stream.advance()
                    self.input_stream.advance()
                    self.vm.write_push(obj,self.symbol.index_of(current_token))
                    self.compile_expression_list()
                    self.vm.write_call(function_name, self.compile_expression_list_counter+1)
                    self.input_stream.advance()
                    self.input_stream.advance()
                elif self.input_stream.current_instruction == 'new':## do p1.new('m,p')
                    obj=self.symbol.kind_of(current_token)
                    function_name = self.symbol.type_of(current_token)+'.'+self.input_stream.current_instruction
                    self.input_stream.advance()
                    self.input_stream.advance()
                    self.vm.write_push(obj,self.symbol.index_of(current_token))
                    self.compile_expression_list()
                    self.vm.write_call(function_name, self.compile_expression_list_counter)
                    self.input_stream.advance()
                    self.input_stream.advance()

            else:
                if self.input_stream.current_instruction != 'new':
                    self.input_stream.advance()
                    part_of_function_name=self.input_stream.current_instruction
                    function_name=current_token+'.'+part_of_function_name
                    self.input_stream.advance()
                    self.input_stream.advance()
                    self.compile_expression_list()
                    self.vm.write_call(function_name,self.compile_expression_list_counter)
                    self.input_stream.advance()
                    self.input_stream.advance()
                #elif self.input_stream.current_instruction == 'new':
                    #self.input_stream.advance()
                    #part_of_function_name=self.input_stream.current_instruction
                    #function_name=current_token+'.'+part_of_function_name
                    #self.input_stream.advance()
                    #self.input_stream.advance()
                    #self.compile_expression_list()
                    #self.vm.write_call(function_name,self.compile_expression_list_counter)
                    #self.input_stream.advance()
                    #self.input_stream.advance()
        else:
            self.input_stream.advance()
            self.vm.write_push('pointer', 0)
            self.compile_expression_list()
            self.input_stream.advance()
            call_label=self.name_of_class+'.'+current_token
            self.vm.write_call(call_label, self.compile_expression_list_counter+1)
            self.input_stream.advance()
        self.vm.write_pop('temp', 0)


    def compile_let(self):###
        self.debug+=1
        self.input_stream.advance()
        varname=self.input_stream.current_instruction
        self.input_stream.advance()
        sign=self.input_stream.current_instruction
        if self.input_stream.symbol() == "[":###array how to
            self.input_stream.advance()
            self.compile_expression()
            self.vm.write_push(self.symbol.kind_of(varname), self.symbol.index_of(varname))
            self.array = True
            self.input_stream.advance()
            self.input_stream.advance()
            self.vm.write_arithmetic('+')
            self.compile_expression()
        else:
            self.input_stream.advance()
            self.compile_expression()
            #self.vm.write_pop('pointer',1)
        #self.input_stream.advance()
        if sign=='[':
            self.vm.write_pop('that', 0)
        else:
            self.vm.write_pop(self.symbol.kind_of(varname),self.symbol.index_of(varname))
        self.input_stream.advance()


    def compile_while(self):###
        self.connum+=1
        current_connum=self.connum
        self.vm.write_label('L1'+str(current_connum))
        self.input_stream.advance()
        self.input_stream.advance()
        self.compile_expression()
        self.vm.write_arithmetic('~','sign')
        self.vm.write_if('L2'+str(current_connum))
        self.input_stream.advance()
        self.input_stream.advance()
        self.compile_statements()
        self.vm.write_goto('L1'+str(current_connum))
        self.vm.write_label('L2'+str(current_connum))
        self.input_stream.advance()
        self.connum+=1


    def compile_return(self):###
        if not self.void:
            self.input_stream.advance()
            while self.input_stream.token_type() != "symbol":  ##TODO - check
                self.compile_expression()
            self.vm.write_return()
            self.input_stream.advance()
        if self.void:
            self.input_stream.advance()
            self.input_stream.advance()



    def compile_if(self):###
        self.connum+=1
        current_connum=self.connum
        self.input_stream.advance()
        self.input_stream.advance()
        self.compile_expression()
        self.vm.write_arithmetic('~','sign')
        self.vm.write_if('L1'+str(current_connum))
        self.input_stream.advance()
        self.input_stream.advance()
        self.compile_statements()
        self.input_stream.advance()
        if self.input_stream.token_type() == "keyword" and \
                self.input_stream.current_instruction == "else":
            self.vm.write_goto('L2'+str(current_connum))
            self.vm.write_label('L1'+str(current_connum))
            self.input_stream.advance()
            self.input_stream.advance()
            self.compile_statements()
            self.vm.write_label('L2' + str(current_connum))
            self.input_stream.advance()

        else:
            self.vm.write_goto('L1' + str(current_connum))
            self.vm.write_label('L1' + str(current_connum))
            #self.input_stream.advance()
            #self.input_stream.advance()
            #self.input_stream.advance()
            #print(self.input_stream.current_instruction)
        self.connum+=1

    def compile_expression(self):###
        """
        Note that tokenizer must be advanced before this is called!!!
        :return:
        """
        self.compile_term()
        while self.input_stream.token_type() == "symbol" and \
                self.input_stream.symbol() in OP_LIST:
            arithmethic_math=self.input_stream.current_instruction
            self.input_stream.advance()
            self.compile_term()
            self.vm.write_arithmetic(arithmethic_math)
        if self.array == True:
            self.vm.write_pop('temp',0)
            self.vm.write_pop('pointer',1)
            self.vm.write_push('temp',0)
        self.array=False


    def compile_term(self):##we stop in the array beacuse david should see the videos
        # need to change term in here
        current_token = self.input_stream.current_instruction
        #print(current_token)
        type_current_token = self.input_stream.token_type()
        self.input_stream.advance()
        new_token=self.input_stream.current_instruction
        if type_current_token == "identifier" and self.input_stream.current_instruction == '[':  ###
            self.input_stream.advance()
            past_array=self.array
            self.array=False
            self.compile_expression()
            self.array=past_array
            self.vm.write_push(self.symbol.kind_of(current_token), self.symbol.index_of(current_token)) ## notsure p1=a[8]?
            self.vm.write_arithmetic('+')
            self.vm.write_pop('pointer',1)
            self.vm.write_push('that',0)
            self.input_stream.advance()
        # if type_current_token == "identifier" and self.input_stream.current_instruction == '[' and self.array==True:###
        #     self.input_stream.advance()
        #     self.array=False
        #     self.compile_expression()
        #     self.vm.write_push(self.symbol.kind_of(current_token),self.symbol.index_of(current_token))
        #     self.vm.write_arithmetic('+')
        #     self.vm.write_pop('pointer',1)
        #     self.vm.write_push('that',0)
        #     self.vm.write_pop('temp',0)
        #     self.vm.write_pop('pointer', 1)
        #     self.vm.write_push('temp', 0)
        #     self.input_stream.advance()
        if current_token in UNARY_OP:###
            past_array=self.array
            self.array=False
            self.compile_term() #a[7]=-8 notsure
            self.vm.write_arithmetic(current_token,'sign')
            self.array=past_array

        if type_current_token == "identifier" and self.input_stream.current_instruction == '(':###
            self.input_stream.advance()
            past_array = self.array
            self.array = False
            self.compile_expression_list()
            self.input_stream.advance()
            self.vm.write_call(current_token,self.compile_expression_list_counter)
            self.array = past_array
        if self.input_stream.current_instruction == '.':###
            obj = self.symbol.kind_of(current_token)
            self.input_stream.advance()
            if obj!='not':
                if self.input_stream.current_instruction!='new':
                    function_name = self.symbol.type_of(current_token)+'.'+self.input_stream.current_instruction
                    self.input_stream.advance()
                    self.input_stream.advance()
                    self.vm.write_push(obj,self.symbol.index_of(current_token))
                    past_array = self.array
                    self.array = False
                    self.compile_expression_list()
                    self.array=past_array
                    self.vm.write_call(function_name, self.compile_expression_list_counter+1)
                    self.input_stream.advance()
                elif self.input_stream.current_instruction =='new':
                    function_name = self.symbol.type_of(current_token) + '.' + self.input_stream.current_instruction
                    self.input_stream.advance()
                    self.input_stream.advance()
                    self.vm.write_push(obj, self.symbol.index_of(current_token))
                    past_array = self.array
                    self.array = False
                    self.compile_expression_list()
                    self.vm.write_call(function_name, self.compile_expression_list_counter)
                    self.array = past_array
                    self.input_stream.advance()
            else:
                    part_of_function_name=self.input_stream.current_instruction
                    function_name=current_token+'.'+part_of_function_name
                    self.input_stream.advance()
                    self.input_stream.advance()
                    past_array = self.array
                    self.array = False
                    self.compile_expression_list()
                    self.vm.write_call(function_name,self.compile_expression_list_counter)
                    self.array = past_array
                    self.input_stream.advance()


        if current_token == '(':###
            past_array = self.array
            self.array = False
            self.compile_expression()
            self.input_stream.advance()
            self.array = past_array

        if type_current_token=='keyword':##for return,is there more?
            if current_token=='this':
                self.vm.write_push('pointer',0)
        obj = self.symbol.kind_of(current_token)
        if type_current_token == "identifier" and obj!='not' and new_token!='.' and new_token!='[':
            self.vm.write_push(self.symbol.kind_of(current_token), self.symbol.index_of(current_token))
        if type_current_token == "stringConstant" and obj!='not':
            self.vm.write_push(self.symbol.kind_of(current_token), self.symbol.index_of(current_token))
        if type_current_token == "stringConstant" and obj == 'not':
            len_of_the_word=len(current_token[1:])
            self.vm.write_push('constant',len_of_the_word)
            self.vm.write_call('String.new', 1)
            for i in current_token[1:]:
                self.vm.write_push('constant', ord(i))
                self.vm.write_call('String.appendChar', 2)
        if type_current_token == "integerConstant":##what about string
            self.vm.write_push('constant',current_token)
        if current_token=='true':
            self.vm.write_push('constant', 0)
            self.vm.write_arithmetic('~')
        if current_token == 'false':
            self.vm.write_push('constant', 0)
        if current_token=='null':
            self.vm.write_push('constant',0)


    def compile_expression_list(self):####
        self.compile_expression_list_counter =0
        if self.input_stream.symbol() != ")":
            self.compile_expression_list_counter+=1
            past_counter= self.compile_expression_list_counter
            self.compile_expression()
            self.compile_expression_list_counter=past_counter
            while self.input_stream.token_type() == "symbol" and \
                    self.input_stream.symbol() == ",":
                self.input_stream.advance()
                self.compile_expression_list_counter+=1
                past_counter = self.compile_expression_list_counter
                self.compile_expression()
                self.compile_expression_list_counter = past_counter
        if self.input_stream.symbol() == "(":
            self.compile_expression_list_counter = 1
            past_counter = self.compile_expression_list_counter
            self.compile_expression()
            self.compile_expression_list_counter = past_counter
            while self.input_stream.token_type() == "symbol" and \
                    self.input_stream.symbol() == ",":
                self.compile_expression_list_counter +=1
                self.input_stream.advance()
                past_counter = self.compile_expression_list_counter
                self.compile_expression()
                self.compile_expression_list_counter = past_counter