# coding=utf-8

# Cordelia López A01194295
# Daniela Guajardo A00823050
# Compilers Final Project

from classes import *
from vm import masterFunc

## GLOBAL VARS
# To fill symbol tables in DirFunc
pos = 0
sym_table_stack = []

# Gives you the index to search for in the sem_cube
is_arithmetic = {'+': 0, '-': 0, '*': 0, '/': 0, '>': 1, '<': 1, '!=': 1, '==': 1,'=': 1}
# Gives you the second and third indexes to complete the search in the sem_cube
operand_type = {'int': 0, 'float': 1, 'char': 2}
sem_cube = [[["int", "float", "NONE"], ["float", "float", "NONE"], ["NONE", "NONE", "NONE"]],
        [["bool", "NONE", "NONE"], ["NONE", "bool", "NONE"], ["NONE", "NONE", "bool"]]]

# Map of symbol table name and actual symbol tables for quick access
sym_tb_finder = {}

# We use context to identify where to look for variables; it changes depending on the current scope
context = []
context.append("GLOBAL")

# Saves the name of the program to use as GLOBAL as the Symbol Table name in the Function Directory
nombre_programa = ""

# Used to pass into the VM both cteMem is passed with values while pointMem only passes the correct size needed
cteMem = MemoryType()
pointMem = MemoryType()

## HELPER VARS
# Variable only used in Factor state to save the id and look for the function afterwards
factor_id = ""

# Used to save the vars used as parameters in the current function being parsed. It is a map (v_name : var)
param_vars = {}
# Used to verify the number of parameters sent to the function equal the number of parameters in the function declaration
param_cont = 0
# Used to construct the variable that stores the return value of the function
func_var = None

# QUAD VARIABLES
# Saves quadruples
quads = []
# Keeps track of quadruple counter
quadPos = 0
# Used to save operands
pila_operandos = []
# Used to save types
pila_tipo = []
# Used to save operators
pila_operadores = []
# Used to fill and re-access jumps
pila_saltos = []
# Stores previous dimention; used in arrays and matrices
pila_dim = []
# Stores True or False, True represents a variable pushed into pila_operadores that is dimensioned and is indexed. 
# Will be used to manage matrix and array operations
pila_indexed = []


## MEMORY VARS
# Counters that keep track of memory used to identify scope and variable type in VM

# memory alloc global
glob_int = 0 # lim 1999
glob_float = 2000 # lim 3999
glob_char = 4000 # lim 5999

# memory alloc local
loc_int = 6000 # lim 7999
loc_float = 8000 # lim 9999
loc_char = 10000 # lim 11999

# memory alloc temp
temp_int = 12000 # lim 13999
temp_float = 14000 # lim 15999
temp_char = 16000 # lim 17999
temp_bool = 18000 # lim 19999

# const memory
const_string = 20000 #lim 21999
const_int = 22000 # lim 23999
const_float = 24000 # lim 25999
const_char = 26000 # lim 27999

# memory pointers
mem_point = 28000


## HELPER FUNCTIONS

# CHECK SPACE
# What: Checks if there is space available before constructing new variable
# Parameters: size needed for variable and variable's address
# Prints error if there is no space and quits program
# # When is it used: In this same module when memory counters are being incremented
def checkSpace(offset, address):
# The outer if indicate the Kind (global, local), the inner ifs indicate type (int, float)
    if (address < 6000):
        if(address < 2000):
            if(glob_int + offset > 1999):
                print("Error: not enough space for glob_int")
                quit()
        elif(address < 4000):
            if(glob_float + offset > 3999):
                print("Error: not enough space for glob_float")
                quit()
        else:
            if(glob_char + offset > 5999):
                print("Error: not enough space for glob_char")
                quit()
    elif (address < 12000):
        if(address < 8000):
            if(loc_int + offset > 7999):
                print("Error: not enough space for loc_int")
                quit()
        elif(address < 10000):
            if(loc_float + offset > 9999):
                print("Error: not enough space for loc_float")
                quit()
        else:
            if(loc_char + offset  > 11999):
                print("Error: not enough space for loc_char")
                quit()
    elif (address < 20000):
        if(address < 14000):
            if(temp_int + offset  > 13999):
                print("Error: not enough space for temp_int")
                quit()
        elif(address < 16000):
            if(temp_float + offset  > 15999):
                    print("Error: not enough space for temp_float")
                    quit()
        elif(address < 18000):
            if(temp_char + offset  > 17999):
                print("Error: not enough space for temp_char")
                quit()
        else:
            if(temp_bool + offset  > 19999):
                print("Error: not enough space for temp_bool")
                quit()
    elif (address < 28000):
        if(address < 22000):
            if(const_string + offset > 21999):
                print("Error: not enough space for const_string")
                quit()
        elif(address < 24000):
            if(const_int + offset > 23999):
                print("Error: not enough space for const_int")
                quit()
        elif(address < 26000):
            if(const_float + offset > 25999):
                print("Error: not enough space for const_float")
                quit()
        else:
            if(const_char + offset > 27999):
                print("Error: not enough space for const_char")
                quit()
    elif (address < 30000):
        if(mem_point + offset > 27999):
                print("Error: not enough space for mem_point")
                quit()
    else:
        print("Error: Memory out of range")
        quit()


# CONSTANT VALUE ASSIGN
# What: Assigns value to cteMem (Constant Memory)
# Parameters: The value it wants assigned and the address it will assign it to
# It does not return anything, but quits if the memory is out of range and saves it if it's not
# When is it used: Whenever a constant value is seen in code
def ConstantValueAssign(val, address):
    if (address < 28000 and address > 19999):
        if(address < 22000):
            cteMem.stringMem.append(val)
        elif(address < 24000):
            cteMem.intMem.append(val)
        elif(address < 26000):
            cteMem.floatMem.append(val)
        else:
            cteMem.charMem.append(val)
    else:
        print("Error: Memory out of range")
        quit()

# FIND CONST VAL
# What: It finds a value in cteMem (Constant Memory)
# Parameters: The address the constant is in
# It returns the value in that address or quits if the address is not within range
# When is it used: To find the constant previously stored and use it to construct matrices and arrays
def findConstVal(address):
    if (address < 28000 and address > 19999):
        if(address < 22000):
            return cteMem.stringMem[address - 20000]
        elif(address < 24000):
            return cteMem.intMem[address - 22000]
        elif(address < 26000):
            return cteMem.floatMem[address - 24000]
        else:
            return cteMem.charMem[address-26000]
    else:
        print("Error: Memory out of range")
        quit()


# ADD VAR
# What: Adds variable to current symbol table
# Parameters: The object variable it wants to add
# It quits if the variable already exists within scope. Otherwise saves the address of the new var and the object in ST
# When is it used: Whenever a new variable is being constructed, whenever a user declares a new variable
def AddVar(var):
    global context
    global glob_int
    global glob_char
    global glob_float
    global loc_int
    global loc_char
    global loc_float
    table = sym_table_stack[-1]

    # Checks if variable is already declared in scope
    if var.name in table.vars:
        print("Error: variable already declared " + str(var.name))
        quit()

    offset = 1
    # Adds the address to the variable depending on the type and kind
    if(len(sym_table_stack) == 2):
        if(var.type == "int"):
            var.address = glob_int

            # Calculates space needed for that variable
            if var.dimention is None:
                checkSpace(0, glob_int)
            else:
                checkSpace(var.dimention.arrayOffset-1, glob_int)
                offset = var.dimention.arrayOffset

            glob_int = glob_int + offset
        elif(var.type == "float"):
            var.address = glob_float

            # Calculates space needed for that variable
            if var.dimention is None:
                checkSpace(0, glob_float)
            else:
                checkSpace(var.dimention.arrayOffset-1, glob_float)
                offset = var.dimention.arrayOffset

            glob_float = glob_float + offset
        elif(var.type == "char"):
            var.address = glob_char

            # Calculates space needed for that variable
            if var.dimention is None:
                checkSpace(0, glob_char)
            else:
                checkSpace(var.dimention.arrayOffset-1, glob_char)
                offset = var.dimention.arrayOffset

            glob_char = glob_char + offset
    else:
        if(var.type == "int"):
            var.address = loc_int

            # Calculates space needed for that variable
            if var.dimention is None:
                checkSpace(0, loc_int)
            else:
                checkSpace(var.dimention.arrayOffset-1, loc_int)
                offset = var.dimention.arrayOffset

            loc_int = loc_int + offset
        elif(var.type == "float"):
            var.address = loc_float

            # Calculates space needed for that variable
            if var.dimention is None:
                checkSpace(0, loc_float)
            else:
                checkSpace(var.dimention.arrayOffset-1, loc_float)
                offset = var.dimention.arrayOffset

            loc_float = loc_float + offset
        elif(var.type == "char"):
            var.address = loc_char

            # Calculates space needed for that variable
            if var.dimention is None:
                checkSpace(0, loc_char)
            else:
                checkSpace(var.dimention.arrayOffset-1, loc_char)
                offset = var.dimention.arrayOffset

            loc_char = loc_char + offset
    table.vars[var.name] = var

# ADD FUNC
# What: Adds function to function directory
# Parameters: The object function it wants to add
# It quits if the function already exists within program. Otherwise adds it to the directory
# When is it used: Whenever a new function is being constructed, whenever a user declares a new function
def AddFunc(func):
    table = sym_table_stack[0]
    # Checks if function is already declared in program
    if func.name in table.vars:
         print("Error: function already declared " + str(var.name))
         quit()
    table.vars[func.name] = func

# GET FUNC
# What: Looks for a function within the function directory
# Parameters: The name of the function it's looking for
# Returns the function object that matches the name or None
# When is it used: When adding variables to a function and creating the return variable for a function
def GetFunc(f_name):
    global nombre_programa
    # sym_table_stack[0] = Function Directory
    if f_name == "GLOBAL":
        f_name = nombre_programa
    table = sym_table_stack[0]
    return table.vars[f_name]


# CONSTRUCT VAR
# What: Constructs all vars in a vars statement (Var tipo : id, id, id ;)
# Parameters: The type and the list of ids
# It separates each id, creates a variable with that info,
# adds all dimention information and calls AddVar
# When is it used: When declaring variables
def ConstructVar(v_type, v_list):
    global const_int
    splitted = v_list.split(',')
    # For each id and var info in the list
    for v in splitted:
        Node1 = None
        stringByWord = v.split(' ')
        varId = stringByWord[0]
        # Indicates if it has dimentions
        if stringByWord[1] == "si":
            Node1 = Node(int(stringByWord[2]) - 1)
            n1_vr = Node1.limiteSuperior + 1
            ConstantValueAssign(n1_vr, const_int)
            Node1.valorR = const_int
            const_int = const_int + 1
            # Indicates whether it has two dimentions
            # Inside these ifs we calculate R and M values accordingly
            if stringByWord[3] != "endarray":
                Node2 = Node(int(stringByWord[3]) - 1)
                Node1.nextDim = Node2
                n2_vr = int(n1_vr * (Node2.limiteSuperior + 1))
                ConstantValueAssign(n2_vr, const_int)
                Node2.valorR = const_int
                const_int = const_int + 1
                n1_vm = int(n2_vr / (Node1.limiteSuperior + 1))
                ConstantValueAssign(n1_vm, const_int)
                Node1.valorM = const_int
                const_int = const_int + 1
                n2_vm = int(n1_vm / (Node2.limiteSuperior + 1))
                ConstantValueAssign(n2_vm, const_int)
                Node2.valorM = const_int
                const_int = const_int + 1
                Node1.arrayOffset = n2_vr
                Node1.arrayDim = 2
            else: # Indicates it has only one dimention
                n1_vm = int(n1_vr / (Node1.limiteSuperior + 1))
                ConstantValueAssign(n1_vm, const_int)
                Node1.valorM = const_int
                const_int = const_int + 1
                Node1.arrayOffset = n1_vr
                Node1.arrayDim = 1
        # Constructs variable object, adds dimention
        new_var = Var(varId, v_type)
        new_var.dimention = Node1
        AddVar(new_var)

# CONSTRUCT FUNC
# What: Constructs the function object
# Parameters: The type and name of the function
# Returns nothing, it constructs the object and calls AddFunc
# When is it used: When declaring new functions
def ConstructFunc(f_type, f_name):
    new_func = Func(f_name, f_type)
    AddFunc(new_func)


# FIND VAR
# What: Looks for a variable within the specific scope and/or Global scope
# Parameters: The name of the variable it's looking for
# Returns the variable object that matches the name or None
# When is it used: When looking for the address of a variable with a specific name
def FindVar(v_name):
    global context
    if(context[-1] != "GLOBAL"):
        st = sym_tb_finder[context[-1]]
        if v_name in st.vars:
            var = st.vars[v_name]
            return var
    st = sym_table_stack[1]
    if v_name in st.vars:
        var = st.vars[v_name]
        return var
    st1 = sym_table_stack[0]
    if v_name in st1.vars:
        var = st1.vars[v_name]
        return var
    return None

# FILL
# What: Fills in specified quadruple pending jumps
# Parameters: quad object and the quad number it will jump to
# Returns nothing
# When is it used: When we have a pending jump in our jump stack (pila_saltos).
# Used in quadruple creation
def Fill(quad, cont):
    quad.result = cont

# FIND VAR IN ADDRESS
# What: Finds a variable in a specific address
# Parameters: The variable's address
# Returns the variable object with that address or none
# When is it used: When needing dimention information the operand stack has the
# variable address but the object is needed
def FindVarInAddress(address):
    global context
    if context[-1] == "GLOBAL":
        for v in sym_table_stack[1].vars:
            var = sym_table_stack[1].vars[v]
            if var.address == address:
                return var
    else:
        dirfunc = sym_table_stack[0].vars
        for v in dirfunc[context[-1]].st.vars:
            var = dirfunc[context[-1]].st.vars[v]
            if var.address == address:
                return var
    return None

# CREATE NODE FOR TEMP
# What: Creates dimension information for temporary structures
# Parameters: number of rows and columns
# Returns the node object created
# When is it used: In this same module when temporary structures are being created
def createNodeForTemp(r, c):
    global const_int
    Node1 = Node(r)
    Node2 = Node(c)
    Node1.nextDim = Node2

    n1_vr = Node1.limiteSuperior + 1
    ConstantValueAssign(n1_vr, const_int)
    Node1.valorR = const_int
    const_int = const_int + 1

    n2_vr = int(n1_vr * (Node2.limiteSuperior + 1))
    ConstantValueAssign(n2_vr, const_int)
    Node2.valorR = const_int
    const_int = const_int + 1
    n1_vm = int(n2_vr / (Node1.limiteSuperior + 1))
    ConstantValueAssign(n1_vm, const_int)
    Node1.valorM = const_int
    const_int = const_int + 1
    n2_vm = int(n1_vm / (Node2.limiteSuperior + 1))
    ConstantValueAssign(n2_vm, const_int)
    Node2.valorM = const_int
    const_int = const_int + 1
    Node1.arrayOffset = n2_vr
    Node1.arrayDim = 2

    return Node1



# IMPORTED LIBRARIES (PLY)
import sys
import ply.lex as lex
import ply.yacc as yacc

### TOKENS AND REGULAR EXPRESSIONS

# RESERVED WORDS
reserved = {
    'program': 'PROGRAM',
    'var': 'VAR',
    'if': 'IF',
    'else': 'ELSE',
    'float': 'FLOAT',
    'int': 'INT',
    'for' : 'FOR',
    'while': 'WHILE',
    'char' : 'CHAR',
    'or' : 'OR',
    'and' : 'AND',
    'main' : 'MAIN',
    'void' : 'VOID',
    'module' : 'MODULE',
    'return': 'RETURN',
    'read': 'READ',
    'write': 'WRITE',
    'do':'DO',
    'to':'TO',
    'then' : 'THEN',
}

# TOKENS
tokens = [
'ID', 'SEMICOLON', 'COLON', 'LBRACE',
'RBRACE', 'COMMA', 'EQUALS', 'EQEQ', 'GRTR', 'LESS', 'NOTEQ', 'PLUS', 'MINUS', 'TIMES',
'DIV', 'LPAREN', 'RPAREN', 'LBRACK', 'RBRACK', 'INTCTE', 'FLOATCTE', 'STRINGCTE', 'CHARCTE', 'DET', 'TRAN', 'INV'] + list(reserved.values())

# REGULAR EXPRESSIONS DESCRIBING EACH TOKEN
t_SEMICOLON = r'\;'
t_COLON = r'\:'
t_LBRACE = r'\{'
t_RBRACE = r'\}'
t_COMMA = '\,'
t_EQUALS = '\='
t_EQEQ = '\=='
t_GRTR = '>'
t_LESS = '<'
t_NOTEQ = '\!='
t_PLUS = '\+'
t_MINUS = '\-'
t_TIMES = '\*'
t_DIV = '\/'
t_LPAREN = '\('
t_RPAREN = '\)'
t_LBRACK = '\['
t_RBRACK = '\]'
t_STRINGCTE = r'\".*\"'
t_CHARCTE = r'\'.\''
t_AND = 'and'
t_OR = 'or'
t_DET = '\$'
t_TRAN = '\¡'
t_INV = '\?'
t_ignore = " \t"

def t_ID(t):
    r'[A-Za-z]([A-Za-z] | [0-9])*'
    if t.value in reserved:
        t.type = reserved[ t.value ]
    return t

def t_FLOATCTE(t):
    r'-?[0-9]+\.[0-9]+'
    t.value = float(t.value)
    return t

def t_INTCTE(t):
    r'-?[0-9]+'
    t.value = int(t.value)
    return t

def t_error(t):
     t.lexer.skip(1)

# LEXER CONSTRUCTION
lexer = lex.lex()


#### GRAMMAR

# PROGRAMA
# Structure of entire program with actions if parsing succeeds it will output "APROPIADO"
def p_programa(p):
  '''programa : PROGRAM add_DirFunc SEMICOLON programa1 MAIN LPAREN RPAREN add_main_jump_ac bloque calc_temp_ac'''
  p[0] = "APROPIADO"

# Option in program to add global variables and functions
def p_programa1(p):
  '''programa1 : vars add_calc_vars_ac go_to_main_ac funcion'''

# Action: fills jump to main in the first quadruple
def p_add_main_jump_ac(p):
    '''add_main_jump_ac : empty'''
    global quadPos
    global temp_int
    global temp_float
    global temp_char
    global temp_bool
    global const_string
    main_jump = pila_saltos.pop()
    Fill(quads[main_jump], quadPos)

    name_f = sym_table_stack[1].name
    fun = GetFunc(name_f)
    fun.temp_ints = temp_int
    fun.temp_floats = temp_float
    fun.temp_chars = temp_char
    fun.temp_bools = temp_bool
    fun.const_strings = const_string

# Action: Calculates temporal variables used in main
def p_calc_temp_ac(p):
    '''calc_temp_ac : empty'''
    global temp_int
    global temp_float
    global temp_char
    global temp_bool
    global const_string


    name_f = sym_table_stack[1].name
    fun = GetFunc(name_f)
    fun.temp_ints = temp_int - fun.temp_ints
    fun.temp_floats = temp_float - fun.temp_floats
    fun.temp_chars = temp_char - fun.temp_chars
    fun.temp_bools = temp_bool - fun.temp_bools
    fun.const_strings = const_string - fun.const_strings

    #clearing temp variables when program ends
    temp_int = temp_int - fun.temp_ints
    temp_float = temp_float - fun.temp_floats
    temp_bool = temp_bool - fun.temp_bools
    temp_char = temp_char - fun.temp_chars
    const_string = const_string - fun.const_strings

# Action: Registers all space needed for each type of variable within global scope
def p_add_calc_vars_ac(p):
    '''add_calc_vars_ac : empty'''
    global nombre_programa
    fun = GetFunc(nombre_programa)
    vars = fun.st.vars
    for v in vars:
        var = vars[v]
        if var.type is not None:
            offset = 1
            if var.dimention is not None:
                offset = var.dimention.arrayOffset
            if var.type == 'int':
                fun.loc_ints = fun.loc_ints + offset
            elif var.type == 'float':
                fun.loc_floats = fun.loc_floats + offset
            elif var.type == 'char':
                fun.loc_chars = fun.loc_chars + offset

# Action: Creates GoTo quadruple to jump to main
def p_go_to_main_ac(p):
    '''go_to_main_ac : empty'''
    global quadPos
    quad = Quadruple(quadPos, "GoTo", "", "", "")
    quads.append(quad)
    quadPos = quadPos + 1
    pila_saltos.append(quadPos-1)

# Action: Creates Function Directory (as type SymbolTable) and adds global as void function
def p_add_DirFunc(p):
    '''add_DirFunc : ID'''
    global pos
    global nombre_programa
    st = SymbolTable()
    st.pos = pos
    pos = pos + 1
    st.name = "DIRFUNC"
    sym_table_stack.append(st)
    ConstructFunc("VOID", p[1])
    st1 = SymbolTable()
    st1.pos = pos
    pos = pos + 1
    st1.name = p[1]
    var = GetFunc(p[1])
    var.st = st1
    sym_table_stack.append(st1)
    nombre_programa = p[1]


# BLOQUE
# Structure of content of a function whether user declared or main
def p_bloque(p):
  '''bloque : LBRACE bloque1 return RBRACE'''

# Option to have multiple statements within a block
def p_bloque1(p):
    '''bloque1 : estatuto bloque1
                        | empty'''
# RETURN
# Option to add a return within a block
def p_return(p):
  '''return : RETURN LPAREN expresion RPAREN SEMICOLON return_ac
                        | empty'''

# Action: Checks that return type is the same as expression result and creates
# return quadruple
def p_return_ac(p):
    '''return_ac : empty'''
    global context
    global quadPos
    ret = pila_operandos[-1]
    retType = pila_tipo[-1]
    func = GetFunc(context[-1])
    if (func.type != retType):
        print ("Error: function return type mismatch")
        quit()
    else:
        quad = Quadruple(quadPos, "RETURN", "", "", ret)
        quads.append(quad)
        quadPos = quadPos + 1

 # TIPO
 # Allowed variable types; returns the chosen type
def p_tipo(p):
  '''tipo : INT
             | FLOAT
             | CHAR'''
  p[0] = p[1]

# TIPO FUNCION
# Allowed function types; returns the chosen type
def p_tipo_funcion(p):
    ''' tipo_funcion : tipo
                        | VOID'''
    p[0] = p[1]

# DIM
# Structure to express dimensions and construct arrays or matrices with respective actions
# It adds the information of the dimension to a string used to construct vars
def p_dim(p):
    '''dim : LBRACK exp RBRACK dim1 
                            | empty'''
    if p[1] == "[":
        typeDim = pila_tipo.pop()
        if typeDim != "int":
            print("Error: array dimension must be of type INT")
            quit()
        else:
            p[0] = " si " + str(findConstVal(pila_operandos.pop())) + " " + p[4] + "endarray"
            pila_indexed.pop()
    else:
        p[0] = " no"

# Option to add another dimension
# It also adds the information of the current dimension to the string
def p_dim1(p):
    '''dim1 : LBRACK exp RBRACK 
                            | empty'''
    if p[1] == "[":
        typeDim = pila_tipo.pop()
        if typeDim != "int":
            print("Error: array dimension must be of type INT")
            quit()
        else:
            p[0] = str(findConstVal(pila_operandos.pop())) + " "
            pila_indexed.pop()
    else:
        p[0] = ""

# DIM ACCESS
# Structure to access variables with dimensions with respective actions
def p_dim_access(p):
    '''dim_access : verify_dims_ac exp RBRACK verify_range_ac dim_access1 calc_virtual_addess_ac
                            | empty'''

# Action: Verifies that variable being accessed has dimensions, adds fake bottom
# and appends Node into dimension stack (pila_dim)
def p_verify_dims_ac(p):
    '''verify_dims_ac : LBRACK'''
    global const_int
    varAddress = pila_operandos.pop()
    pila_indexed.pop()
    var = FindVarInAddress(varAddress)
    varType = pila_tipo.pop()
    if var.dimention is not None:
        dim = var.dimention.arrayDim
        Node1 = var.dimention
        Node1.base_address = varAddress
        pila_dim.append(Node1)
        pila_operadores.append("FB")
    else:
        print("Error: variable not dimensioned")
        quit()

# Action: Creates verify quadruple. If it not the last dimension, it creates
# quadruple to update M value
def p_verify_range_ac(p):
    '''verify_range_ac : empty'''
    global quadPos
    global temp_int
    Node1 = pila_dim[-1]
    quad = Quadruple(quadPos, "VERIFY", pila_operandos[-1], Node1.limiteInferior, Node1.limiteSuperior)
    quads.append(quad)
    quadPos = quadPos + 1
    # Checks if it has another dimension
    if Node1.nextDim is not None:
        aux = pila_operandos.pop()
        aux_type = pila_tipo.pop()
        pila_indexed.pop()
        if aux_type != "int":
            print("Error: dimension access must be with type INT")
            quit()
        checkSpace(0, temp_int)
        # Creates quadruple to multiply exp result with M
        quad1 = Quadruple(quadPos, "*", aux, Node1.valorM, temp_int)
        pila_operandos.append(temp_int)
        pila_indexed.append(False)
        pila_tipo.append("int")
        quads.append(quad1)
        quadPos = quadPos +1
        temp_int = temp_int +1

# Action: Creates quadruple to calculate address of dimension variables
def p_calc_virtual_addess_ac(p):
    '''calc_virtual_addess_ac : empty'''
    global quadPos
    global mem_point
    aux1 = pila_operandos.pop()
    aux1_type = pila_tipo.pop()
    pila_indexed.pop()
    Node = pila_dim.pop()
    if aux1_type != "int":
        print("Error: dimension access must be with type INT")
        quit()
    # The result of this quadruple has inside it another address that it has to access
    quad = Quadruple(quadPos, "+dir", aux1, Node.base_address, mem_point)
    quads.append(quad)
    pila_operandos.append(mem_point)
    pila_indexed.append(True)
    var = FindVarInAddress(Node.base_address)
    pila_tipo.append(var.type)
    quadPos = quadPos + 1
    mem_point = mem_point + 1
    pointMem.intMem.append(None)
    pila_operadores.pop()

# Option to access a matrix, checks whether it does have another dimension
def p_dim_access1(p):
    '''dim_access1 : LBRACK exp RBRACK dim_2_ac
                            | empty'''
    if p[1] != "[":
        if (pila_dim[-1].arrayDim == 2):
            print("Error: missing dimension")
            quit()

# Action: Checks whether the variable has two dimensions, creates verify quadruple
# to know whether result is in bounds, Creates add quadruple for the result of
# the previous operation with the result of the expression
def p_dim_2_ac(p):
    '''dim_2_ac : empty'''
    global quadPos
    global temp_int
    dim = pila_dim[-1].arrayDim
    if(dim < 2):
        print("Error: variable not a matrix")
        quit()
    Node2 = pila_dim[-1].nextDim
    quad = Quadruple(quadPos, "VERIFY", pila_operandos[-1], Node2.limiteInferior, Node2.limiteSuperior)
    quads.append(quad)
    quadPos = quadPos + 1

    aux2 = pila_operandos.pop()
    aux2_type = pila_tipo.pop()
    pila_indexed.pop()
    aux1 = pila_operandos.pop()
    aux1_type = pila_tipo.pop()
    pila_indexed.pop()
    quad = Quadruple(quadPos, "+", aux1, aux2, temp_int)
    quads.append(quad)
    pila_operandos.append(temp_int)
    pila_indexed.append(False)
    pila_tipo.append("int")
    temp_int = temp_int + 1
    quadPos = quadPos + 1



# VARS
# Structure of variable declaration
# It constructs all vars
def p_vars(p):
  '''vars : vars_order vars
                        | empty'''

# Declaration of one or more variables of the same type
def p_vars_order(p):
  '''vars_order : VAR tipo COLON vars0 SEMICOLON'''
  if len(p) > 3:
    ConstructVar(p[2], p[4])

# Returns list of all ids used to construct variables
def p_vars0(p):
    '''vars0 : ID dim vars1'''
    if p[3] is None:
      p[0] = p[1] + "" + p[2]
    else:
      p[0] = p[1] + "" + p[2] + "" + p[3]

# Option to add multiple ids, it also adds them to the list
def p_vars1(p):
  '''vars1 : COMMA ID dim vars1
                    | empty'''
  if len(p) != 2:
    if p[4] is not None:
      p[0] = p[1] + "" + p[2] +  "" + p[3] + "" + p[4]
    else:
      p[0] = p[1] + "" + p[2] + "" + p[3]
  else:
    p[0] = None

# FUNCION
# Structure to declare multiple functions
def p_funcion(p):
    '''funcion : funcion2 funcion
                                | empty'''

# It constructs a function object with a new SymbolTable
def p_funcion1(p):
    '''funcion1 : tipo_funcion MODULE ID'''
    ConstructFunc(p[1],p[3])
    global pos
    global quadPos
    global context
    st1 = SymbolTable()
    st1.pos = pos
    pos = pos + 1
    st1.name = p[3]
    var = GetFunc(p[3])
    var.st = st1
    # Where a function call needs to jump to
    var.address = quadPos
    sym_table_stack.append(st1)
    sym_tb_finder[p[3]] = st1
    # Changes context to current function
    context.append(p[3])
    p[0] = p[3]

# Declaration of a single function
# After whole function is declared, it adds the name attaches the Function object
# to the SymbolTable constructed and changes context back to GLOBAL
def p_funcion2(p):
  '''funcion2 : funcion1 LPAREN vars add_param_tb_ac RPAREN SEMICOLON vars add_cont_vars_ac add_init_quad_temp_count_ac bloque end_func_ac'''
  global context
  sym_table_stack[-1].name = p[1]
  var = GetFunc(p[1])
  var.st = sym_table_stack[-1]
  sym_tb_finder[p[1]] = pos-1
  context.pop()

# Action: Stores the initial value of quadPos and all temp addresses later used
# to calculate temporal memory needed and jumps to function
def p_add_init_quad_temp_count_ac(p):
    '''add_init_quad_temp_count_ac : empty'''
    global quadPos
    global temp_int
    global temp_float
    global temp_char
    global temp_bool
    global const_string

    name_f = sym_table_stack[-1].name
    fun = GetFunc(name_f)
    fun.init_quad = quadPos
    fun.temp_ints = temp_int
    fun.temp_floats = temp_float
    fun.temp_chars = temp_char
    fun.temp_bools = temp_bool
    fun.const_strings = const_string

# Action: Creates EndFunc quadruple and finishes calculating temporal space needed
def p_end_func_ac(p):
    '''end_func_ac : empty'''
    global quadPos
    global temp_int
    global temp_float
    global temp_char
    global temp_bool
    global const_string
    global loc_int
    global loc_float
    global loc_char
    name_f = sym_table_stack[-1].name
    fun = GetFunc(name_f)
    fun.st = {}
    quad = Quadruple(quadPos, "EndFunc", "", "", "")
    quads.append(quad)
    quadPos = quadPos + 1
    fun.temp_ints = temp_int - fun.temp_ints
    fun.temp_floats = temp_float - fun.temp_floats
    fun.temp_chars = temp_char - fun.temp_chars
    fun.temp_bools = temp_bool - fun.temp_bools
    fun.const_strings = const_string - fun.const_strings

    #Resets temps after function
    temp_int = temp_int - fun.temp_ints
    temp_float = temp_float - fun.temp_floats
    temp_bool = temp_bool - fun.temp_bools
    temp_char = temp_char - fun.temp_chars
    const_string = const_string - fun.const_strings

    #Resets locals after function
    loc_int = loc_int - fun.loc_ints - fun.param_ints
    loc_float = loc_float - fun.loc_floats - fun.param_floats
    loc_char = loc_char - fun.loc_chars - fun.param_chars

# Action: Creates Parameter Table and adds the variables declared and constructed
def p_add_param_tb_ac(p):
    '''add_param_tb_ac : empty'''
    curr_sym = sym_table_stack[-1]
    name_f = sym_table_stack[-1].name
    par_tb = ParamTable()
    par_tb.vars = curr_sym.vars.copy()
    fun = GetFunc(name_f)
    fun.param_tb = par_tb
    for p in par_tb.vars:
        var = par_tb.vars[p]
        if var.type is not None:
            if var.type == 'int':
                fun.param_ints = fun.param_ints + 1
            elif var.type == 'float':
                fun.param_floats = fun.param_floats + 1
            elif var.type == 'char':
                fun.param_chars = fun.param_chars + 1
    fun.st.vars = {}

# Action: Adds the count of each type variable to the function class
def p_add_cont_vars_ac(p):
    '''add_cont_vars_ac : empty'''
    curr_sym = sym_table_stack[-1]
    name_f = sym_table_stack[-1].name
    fun = GetFunc(name_f)

    for v in curr_sym.vars:
        var = curr_sym.vars[v]
        if var.type is not None:
            offset = 1
            if var.dimention is not None:
                offset = var.dimention.arrayOffset
            if var.type == 'int':
                fun.loc_ints = fun.loc_ints + offset
            elif var.type == 'float':
                fun.loc_floats = fun.loc_floats + offset
            elif var.type == 'char':
                fun.loc_chars = fun.loc_chars + offset

    fun.st.vars.update(fun.param_tb.vars)

# ESTATUTO
# Structre of statements
def p_estatuto(p):
  '''estatuto : asignacion
                | condicion
                | write
                | read
                | forloop
                | whileloop
                | llamar_funcion'''


# ASIGNACION
# Structure of assignment
# Makes sure the result of the expression and the variable are from the same type and creates the assignment quadruple.
# If both sides are structures (array or matrix) creates quadruple that verifies same dimensions and creates =dim quadruple.
# If not structures creates normal assignment quadruple.
def p_asignacion(p):
  '''asignacion : push_id_assign dim_access EQUALS expresion SEMICOLON'''
  global quadPos
  resultado = pila_operandos.pop()
  indexed1 = pila_indexed.pop()
  tipoResultado = pila_tipo.pop()
  var_address = pila_operandos.pop()
  indexed2 = pila_indexed.pop()
  var_type = pila_tipo.pop()
  if tipoResultado != var_type:
      print ("Error: type mismatch in variable value assignment")
      quit()
  else:
    var = FindVarInAddress(var_address)
    resultVar = FindVarInAddress(resultado)
    if indexed1 != True and indexed2 != True and var is not None and resultVar is not None:
        if var.dimention is not None and resultVar.dimention is not None:
            if var.dimention.arrayDim == resultVar.dimention.arrayDim:
                quad = Quadruple(quadPos, 'VerifyLS', var.dimention.limiteSuperior, resultVar.dimention.limiteSuperior, "")
                quads.append(quad)
                quadPos = quadPos + 1
                if var.dimention.arrayDim == 2:
                    quad = Quadruple(quadPos, 'VerifyLS', var.dimention.nextDim.limiteSuperior, resultVar.dimention.nextDim.limiteSuperior, "")
                    quads.append(quad)
                    quadPos = quadPos + 1
                quad1 = Quadruple(quadPos, '=dim', var.address, resultVar.address, var.dimention.arrayOffset)
                quads.append(quad1)
                quadPos = quadPos + 1
            else:
                print("Error: cannot assign structures with different dimensions to each other")
                quit()
        else:
            quad = Quadruple(quadPos,'=', resultado, '', var_address)
            quads.append(quad)
            quadPos = quadPos + 1
    else:
      quad = Quadruple(quadPos,'=', resultado, '', var_address)
      quads.append(quad)
      quadPos = quadPos + 1


# EXPRESION
# Highest level with possibility of AND/OR Expressions
def p_expresion(p):
  '''expresion : expresion_cmp expresion1'''

# Option to add multiple AND/OR expressions
def p_expresion1(p):
  '''expresion1 : push_and_or_ac expresion_cmp validar_and_or_ac expresion1
                | empty'''

# Action: Pushes the operator AND or OR
def p_push_and_or_ac(p):
    '''push_and_or_ac : AND
                        | OR'''
    pila_operadores.append(p[1])

# Action: Checks that both operands are boolean and creates new quadruple of the and/or operation.
# It saves the result in a temporal boolean space.
def p_validar_and_or_ac(p):
    '''validar_and_or_ac : empty'''
    global temp_bool
    global quadPos
    checkSpace(0, temp_bool)
    expr_cmp2 = pila_operandos.pop()
    pila_indexed.pop()
    expr_cmp1 = pila_operandos.pop()
    pila_indexed.pop()
    tipo2 = pila_tipo.pop()
    tipo1 = pila_tipo.pop()
    op = pila_operadores.pop()
    if tipo1 != "bool" or tipo2 != "bool":
        print("Error: cannot make non bool comparison")
        quit()
    else:
        result_type = "bool"
        pila_tipo.append(result_type)
        pila_operandos.append(temp_bool)
        pila_indexed.append(False)
        quad = Quadruple(quadPos, op, expr_cmp1, expr_cmp2, temp_bool)
        quads.append(quad)
        quadPos = quadPos + 1
        temp_bool = temp_bool + 1

# EXPRESION CMP
# Possibility of comparisons
def p_expresion_cmp(p):
    '''expresion_cmp : exp expresion_cmp1'''

# Option to do a comparison
def p_expresion_cmp1(p):
    '''expresion_cmp1 : push_cmp_ac exp validar_comparacion_ac
                  | empty'''

# Action: Pushes operator
def p_push_cmp_ac(p):
    ''' push_cmp_ac : GRTR
                        | LESS
                        | EQEQ
                        | NOTEQ'''
    pila_operadores.append(p[1])

# Action: Checks semantic cube for result type and creates quadruple with comparison.
# It then saves the result in a temporal boolean space.
def p_validar_comparacion_ac(p):
    '''validar_comparacion_ac : empty'''
    global temp_bool
    global quadPos
    checkSpace(0, temp_bool)
    exp2 = pila_operandos.pop()
    pila_indexed.pop()
    exp1 = pila_operandos.pop()
    pila_indexed.pop()
    tipo2 = pila_tipo.pop()
    tipo1 = pila_tipo.pop()
    op = pila_operadores.pop()
    result_type = sem_cube[is_arithmetic[op]][operand_type[tipo1]][operand_type[tipo2]]
    pila_tipo.append(result_type)
    pila_operandos.append(temp_bool)
    pila_indexed.append(False)
    quad = Quadruple(quadPos, op, exp1, exp2, temp_bool)
    quads.append(quad)
    quadPos = quadPos+1
    temp_bool = temp_bool + 1

# EXP
# posibility of adding one or more term (termino) and corresponding actions
def p_exp(p):
  '''exp : termino check_op_exp exp1'''

#EXP 1
# calls push action to read and push operator and posibility of adding another exp
def p_exp1(p):
  '''exp1 : push_op_exp exp
            | empty'''

#PUSH OP EXP
#pushes the corresponding operator into the stack (pila_operadores)
def p_push_op_exp(p):
    '''push_op_exp : PLUS
            | MINUS'''
    pila_operadores.append(p[1])

# Action: is gets the operator and both operands included in an exp type statement, then 
# checks if operand types and operator are compatible with the semantic cube, if they are
# compatible, gets result type, checks space, and creates corresponding quadruple
# Also supports structures, creates quadruples that verifies compatibility of dimensions.
def p_check_op_exp(p):
    '''check_op_exp : empty'''
    global quads
    global quadPos
    global temp_int
    global temp_float
    global temp_char
    global context

    if len(pila_operadores) > 0:
        if pila_operadores[-1] == "+" or pila_operadores[-1] == "-":
            right_op = pila_operandos.pop() 
            indexed1= pila_indexed.pop()
            left_op = pila_operandos.pop() 
            indexed2 = pila_indexed.pop()
            right_t = pila_tipo.pop()
            left_t = pila_tipo.pop()
            operator = pila_operadores.pop()
            result_type = sem_cube[is_arithmetic[operator]][operand_type[left_t]][operand_type[right_t]]
            if result_type != "NONE":
                res = None
                var = FindVarInAddress(right_op)
                resultVar = FindVarInAddress(left_op)
                if indexed1 != True and indexed2 != True and var is not None and resultVar is not None:
                    if var.dimention is not None and resultVar.dimention is not None:
                        if var.dimention.arrayDim == resultVar.dimention.arrayDim:
                            quad = Quadruple(quadPos, 'VerifyLS', var.dimention.limiteSuperior, resultVar.dimention.limiteSuperior, "")
                            quads.append(quad)
                            quadPos = quadPos + 1
                            if result_type == "int" :
                                res = temp_int
                                checkSpace(var.dimention.arrayOffset-1, res)
                                temp_int = temp_int + var.dimention.arrayOffset
                            elif result_type == "float":
                                res = temp_float
                                checkSpace(var.dimention.arrayOffset-1, res)
                                temp_float = temp_float + var.dimention.arrayOffset
                            elif result_type == "char":
                                res = temp_char
                                checkSpace(var.dimention.arrayOffset-1, res)
                                temp_char = temp_char + var.dimention.arrayOffset
                            if var.dimention.arrayDim == 2:
                                quad = Quadruple(quadPos, 'VerifyLS', var.dimention.nextDim.limiteSuperior, resultVar.dimention.nextDim.limiteSuperior, "")
                                quads.append(quad)
                                quadPos = quadPos + 1
                            temp_var = Var(str(res), result_type)
                            temp_var.address = res
                            temp_var.dimention = var.dimention
                            pila_tipo.append(result_type)
                            pila_operandos.append(res)
                            pila_indexed.append(False)
                            func = GetFunc(context[-1])
                            func.st.vars[temp_var.name] = temp_var 
                            if operator == "+":
                                quad1 = Quadruple(quadPos, '+dim', resultVar.address, var.address, temp_var.address)
                            else:
                                quad1 = Quadruple(quadPos, '-dim', resultVar.address, var.address, temp_var.address)
                            quads.append(quad1)
                            quadPos = quadPos + 1
                            quad2 = Quadruple(quadPos, "offset", "", "", temp_var.dimention.arrayOffset)
                            quads.append(quad2)
                            quadPos = quadPos + 1
                        else:
                            print("Error: cannot add/subtract structures with different dimensions to each other")
                            quit()
                    else:
                        if result_type == "int" :
                            res = temp_int
                            checkSpace(0, res)
                            temp_int = temp_int + 1
                        elif result_type == "float":
                            res = temp_float
                            checkSpace(0, res)
                            temp_float = temp_float + 1
                        elif result_type == "char":
                            res = temp_char
                            checkSpace(0, res)
                            temp_char = temp_char + 1
                        quad = Quadruple(quadPos,operator,left_op, right_op, res)
                        quads.append(quad)
                        pila_tipo.append(result_type)
                        pila_operandos.append(res)
                        pila_indexed.append(False)
                        quadPos = quadPos + 1
                else:
                    if result_type == "int" :
                        res = temp_int
                        checkSpace(0, res)
                        temp_int = temp_int + 1
                    elif result_type == "float":
                        res = temp_float
                        checkSpace(0, res)
                        temp_float = temp_float + 1
                    elif result_type == "char":
                        res = temp_char
                        checkSpace(0, res)
                        temp_char = temp_char + 1
                    quad = Quadruple(quadPos,operator,left_op, right_op, res)
                    quads.append(quad)
                    pila_tipo.append(result_type)
                    pila_operandos.append(res)
                    pila_indexed.append(False)
                    quadPos = quadPos + 1
            else:
                print("Error: types are not compatible for operation")
                quit()

# TERMINO
# option to add terms that will be used by other states to multiply or divide
def p_termino(p):
  '''termino : factor check_op_term termino1'''

# TERMINO 1
# option to read another term 
def p_termino1(p):
  '''termino1 : push_op_term termino
                    | empty'''

# PUSH OP TERM
# read and push the * or / operation into stack (pila_operadores)
def p_push_op_term(p):
    '''push_op_term : TIMES
            | DIV'''
    pila_operadores.append(p[1])

# Action: is gets the operator and both operands included in an exp type statement, then 
# checks if operand types and operator are compatible with the semantic cube, if they are
# compatible, gets result type, checks space, and creates corresponding quadruple
# Also supports structures, creates quadruples that verifies compatibility of dimensions.
def p_check_op_term(p):
    '''check_op_term : empty'''
    global quads
    global quadPos
    global temp_int
    global temp_float
    global temp_char

    if len(pila_operadores) > 0:
        if pila_operadores[-1] == "*" or pila_operadores[-1] == "/":
            right_op = pila_operandos.pop()
            indexed1 = pila_indexed.pop()
            left_op = pila_operandos.pop() 
            indexed2 = pila_indexed.pop()
            right_t = pila_tipo.pop()
            left_t = pila_tipo.pop()
            operator = pila_operadores.pop()
            result_type = sem_cube[is_arithmetic[operator]][operand_type[left_t]][operand_type[right_t]]
            if result_type != "NONE":
                res = None
                var = FindVarInAddress(right_op)
                resultVar = FindVarInAddress(left_op)
                if indexed1 != True and indexed2 != True and var is not None and resultVar is not None:
                    if var.dimention is not None and resultVar.dimention is not None:
                        if var.dimention.arrayDim == resultVar.dimention.arrayDim:
                            if var.dimention.arrayDim == 2:
                                quad = Quadruple(quadPos, 'VerifyLS', resultVar.dimention.nextDim.limiteSuperior, var.dimention.limiteSuperior, "")
                                quads.append(quad)
                                quadPos = quadPos + 1
                                tempNode = createNodeForTemp(resultVar.dimention.limiteSuperior, var.dimention.nextDim.limiteSuperior)
                                if result_type == "int" :
                                    res = temp_int
                                    checkSpace(tempNode.arrayOffset-1, res)
                                    temp_int = temp_int + tempNode.arrayOffset
                                elif result_type == "float":
                                    res = temp_float
                                    checkSpace(tempNode.arrayOffset-1, res)
                                    temp_float = temp_float + tempNode.arrayOffset
                                elif result_type == "char":
                                    res = temp_char
                                    checkSpace(tempNode.arrayOffset-1, res)
                                    temp_char = temp_char + tempNode.arrayOffset
                                
                                temp_var = Var(str(res), result_type)
                                temp_var.address = res
                                temp_var.dimention = tempNode
                                pila_tipo.append(result_type)
                                pila_operandos.append(res)
                                pila_indexed.append(False)
                                func = GetFunc(context[-1])
                                func.st.vars[temp_var.name] = temp_var 
                                if operator == "*":
                                    quad1 = Quadruple(quadPos, '*dim', resultVar.address, var.address, temp_var.address)
                                    quads.append(quad1)
                                    quadPos = quadPos + 1
                                    quad2 = Quadruple(quadPos, "first", resultVar.dimention.limiteSuperior, resultVar.dimention.nextDim.limiteSuperior, "")
                                    quads.append(quad2)
                                    quadPos = quadPos + 1
                                    quad3 = Quadruple(quadPos, "second", var.dimention.limiteSuperior, var.dimention.nextDim.limiteSuperior, "")
                                    quads.append(quad3)
                                    quadPos = quadPos + 1
                                else:
                                    print("Error: Cannot divide structures")
                                    quit()
                            else:
                                print("Error: Cannot multiply arrays")
                                quit()
                        else:
                            print("Error: Cannot multiply structures with non-compatible dimensions")
                            quit()
                    else:
                        if result_type == "int" :
                            res = temp_int
                            checkSpace(0, res)
                            temp_int = temp_int + 1
                        elif result_type == "float":
                            res = temp_float
                            checkSpace(0, res)
                            temp_float = temp_float + 1
                        elif result_type == "char":
                            res = temp_char
                            checkSpace(0, res)
                            temp_char = temp_char + 1
                        quad = Quadruple(quadPos,operator,left_op, right_op, res)
                        quads.append(quad)
                        pila_tipo.append(result_type)
                        pila_operandos.append(res)
                        pila_indexed.append(False)
                        quadPos = quadPos + 1
                else:
                    if result_type == "int" :
                        res = temp_int
                        checkSpace(0, res)
                        temp_int = temp_int + 1
                    elif result_type == "float":
                        res = temp_float
                        checkSpace(0, res)
                        temp_float = temp_float + 1
                    elif result_type == "char":
                        res = temp_char
                        checkSpace(0, res)
                        temp_char = temp_char + 1
                    quad = Quadruple(quadPos,operator,left_op, right_op, res)
                    quads.append(quad)
                    pila_tipo.append(result_type)
                    pila_operandos.append(res)
                    pila_indexed.append(False)
                    quadPos = quadPos + 1
            else:
                print("Error: types are not compatible for operation")
                quit()

# FACTOR
# Option to start another expression or go to a terminal variable with corresponding actions
def p_factor(p):
  '''factor : LPAREN expresion RPAREN
                    | varCte
                    | push_id factor1'''

# Option to call a function or access dimentions
def p_factor1(p):
  '''factor1 : llamar_funcion_factor
            | dim_access
            | DET det_ac
            | TRAN tran_ac
            | INV inv_ac'''

# Action: Checks that it is a structure and it complies with requirements necessary
# to calculate the determinant (square dimensions, not char)
# creates DET quadruple
def p_det_ac(p):
    '''det_ac : empty'''
    global quadPos
    global temp_float
    mat_address = pila_operandos.pop()
    mat_type = pila_tipo.pop()
    indexed = pila_indexed.pop()
    varMat = FindVarInAddress(mat_address)
    if mat_type == "char":
        print("Error: Cannot calculate determinant of char matrix")
        quit()
    if varMat is None or varMat.dimention is None or varMat.dimention.arrayDim != 2:
        print("Error: Cannot calculate determinant")
        quit()
    quad = Quadruple(quadPos, 'VerifyLS', varMat.dimention.limiteSuperior, varMat.dimention.nextDim.limiteSuperior, "")
    quads.append(quad)
    quadPos = quadPos + 1

    quad1 = Quadruple(quadPos, "DET", mat_address, "", temp_float)
    checkSpace(0, temp_float)
    pila_operandos.append(temp_float)
    pila_tipo.append("float")
    pila_indexed.append(False)
    temp_float = temp_float + 1
    quads.append(quad1)
    quadPos = quadPos + 1

    quad2 = Quadruple(quadPos, "matInfo", varMat.dimention.limiteSuperior, "", "")
    quads.append(quad2)
    quadPos = quadPos + 1

# Action: Checks that it is a structure and it complies with requirements necessary
# to calculate the inverse (calls det_ac to verify det is not zero in VM)
# creates INV quadruple
def p_inv_ac(p):
    '''inv_ac : push_id_inv det_ac'''
    global quadPos
    global temp_float
    det = pila_operandos.pop()
    det_tipo = pila_tipo.pop()
    inx = pila_indexed.pop()

    mat_address = pila_operandos.pop()
    mat_type = pila_tipo.pop()
    indexed = pila_indexed.pop()
    varMat = FindVarInAddress(mat_address)

    quad = Quadruple(quadPos, "VerifyDet", "", "", det)
    quads.append(quad)
    quadPos = quadPos + 1

    tempNode = createNodeForTemp(varMat.dimention.limiteSuperior, varMat.dimention.nextDim.limiteSuperior)
    checkSpace(tempNode.arrayOffset-1, temp_float)

    res = temp_float
    temp_float = temp_float + tempNode.arrayOffset

    temp_var = Var(str(res), mat_type)
    temp_var.address = res
    temp_var.dimention = tempNode
    pila_tipo.append("float")
    pila_operandos.append(res)
    pila_indexed.append(False)
    func = GetFunc(context[-1])
    func.st.vars[temp_var.name] = temp_var 

    quad1 = Quadruple(quadPos, "INV", varMat.dimention.limiteSuperior, mat_address, res)
    quads.append(quad1)
    quadPos = quadPos + 1
    

# Action: Pushes mat address, type and indexed again to be able
# to use det_ac accordingly
def p_push_id_inv(p):
    '''push_id_inv : empty'''
    mat_address = pila_operandos[-1]
    mat_type = pila_tipo[-1]
    indexed = pila_indexed[-1]

    pila_operandos.append(mat_address)
    pila_tipo.append(mat_type)
    pila_indexed.append(indexed)

# Action: Checks that it is a structure and it complies with requirements necessary
# to calculate the transpose (matrix)
# creates TRAN quadruple
def p_tran_ac(p):
    '''tran_ac : empty '''
    global quadPos
    global temp_int
    global temp_float
    global temp_char
    mat_address = pila_operandos.pop()
    mat_type = pila_tipo.pop()
    indexed = pila_indexed.pop()
    varMat = FindVarInAddress(mat_address)
    res = None
    tempNode = createNodeForTemp(varMat.dimention.nextDim.limiteSuperior, varMat.dimention.limiteSuperior)
    if varMat.dimention.arrayDim == 2:
        if mat_type == "int" :
            res = temp_int
            checkSpace(tempNode.arrayOffset-1, res)
            temp_int = temp_int + tempNode.arrayOffset
        elif mat_type == "float":
            res = temp_float
            checkSpace(tempNode.arrayOffset-1, res)
            temp_float = temp_float + tempNode.arrayOffset
        elif mat_type == "char":
            res = temp_char
            checkSpace(tempNode.arrayOffset-1, res)
            temp_char = temp_char + tempNode.arrayOffset
        temp_var = Var(str(res), mat_type)
        temp_var.address = res
        temp_var.dimention = tempNode
        pila_tipo.append(mat_type)
        pila_operandos.append(res)
        pila_indexed.append(False)
        func = GetFunc(context[-1])
        func.st.vars[temp_var.name] = temp_var 

        quad = Quadruple(quadPos, "TRAN", mat_address, "", res)
        quads.append(quad)
        quadPos = quadPos + 1
        quad1 = Quadruple(quadPos, "mat_info", varMat.dimention.limiteSuperior, varMat.dimention.nextDim.limiteSuperior, "")
        quads.append(quad1)
        quadPos = quadPos + 1 
    else:
        print("Error: cannot transpose if variable does not have 2 dimensions")
        quit()


# Reads the variable ID. Finds that variable's address and pushes it into stack (pila_operandos)
# pushes variable type into type stack (pila_tipo) and returns the id for further use
def p_push_id(p):
    '''push_id : ID'''
    global factor_id
    var = FindVar(p[1])
    if var is None:
        print("Error: " + str(p[1]) + " not declared")
        quit()
    pila_operandos.append(var.address)
    pila_indexed.append(False)
    pila_tipo.append(var.type)
    factor_id = p[1]

# Action: Finds the variable and records the address for further use.
def p_push_id_assign(p):
    '''push_id_assign : ID'''
    var = FindVar(p[1])
    if var is None:
        print("Error: " + str(p[1]) + " not declared")
        quit()
    pila_operandos.append(var.address)
    pila_indexed.append(False)
    pila_tipo.append(var.type)

# Creates GoSub quadruple with corresponding information. Checks space needed for return value
# for that function. Adds one to the specific return type's counter and creates assignment quadruple.
def p_llamar_funcion_factor(p):
    '''llamar_funcion_factor : verificar_funcion_ac_factor llamar_funcion1 RPAREN validate_num_param_ac'''
    global quadPos
    global func_var
    global temp_int
    global temp_float
    global temp_char
    quad = Quadruple(quadPos, "GoSub", p[1].name, "", p[1].address)
    quads.append(quad)
    quadPos = quadPos + 1
    pila_operadores.pop()
    
    if func_var.type == "int":
        address = temp_int
        checkSpace(0, address)
        temp_int = temp_int + 1
    elif func_var.type == "float":
        address = temp_float
        checkSpace(0, address)
        temp_float = temp_float + 1
    elif func_var.type == "char":
        address = temp_char
        checkSpace(0, address)
        temp_char = temp_char + 1


    quadT = Quadruple(quadPos, "=", func_var.address, "", address)
    quads.append(quadT)
    quadPos = quadPos + 1
    pila_operandos.append(address)
    pila_indexed.append(False)
    pila_tipo.append(func_var.type)

# Whenever a funciton is called, this checks if the function is declared in scope, quits if it is not
# Then depending of context and return type (if it is not void), creates the return variable and assigns address
# creates the ERA quadruple and copies the corresponding param_vars stores earlier to specific function.
def p_verificar_funcion_ac_factor(p):
    '''verificar_funcion_ac_factor : LPAREN'''
    global quadPos
    global param_vars
    global func_var
    global loc_int
    global loc_float
    global loc_char
    global glob_int
    global glob_float
    global glob_char

    func = GetFunc(factor_id)
    if (func is None):
        print("Error: function not declared in scope")
        quit()
    else:
        if func.type != "void":
            if context[-1] == "GLOBAL":
                if sym_table_stack[1].vars.get(func.name) is None:
                    contextFunc = sym_table_stack[0].vars[nombre_programa]
                    var = Var(func.name, func.type)
                    func_var = var
                    sym_table_stack[1].vars[var.name] = var
                    if var.type == "int":
                        var.address = glob_int
                        glob_int = glob_int + 1
                        contextFunc.loc_ints = contextFunc.loc_ints +1
                    elif var.type == "float":
                        var.address = glob_float
                        glob_float = glob_float + 1
                        contextFunc.loc_floats = contextFunc.loc_floats +1
                    elif var.type == "char":
                        var.address = glob_char
                        glob_char = glob_char + 1
                        contextFunc.loc_chars = contextFunc.loc_chars +1

                else:
                    func_var = sym_table_stack[1].vars.get(func.name)
            else:
                if sym_table_stack[0].vars[context[-1]].st.vars.get(func.name) is None: #agregamos el st.
                    var = Var(func.name, func.type)
                    func_var = var
                    contextFunc = GetFunc(context[-1])
                    contextFunc.st.vars[var.name] = var #agregamos el st.
                    if var.type == "int":
                        var.address = loc_int
                        loc_int = loc_int + 1
                        contextFunc.loc_ints = contextFunc.loc_ints +1
                    elif var.type == "float":
                        var.address = loc_float
                        loc_float = loc_float + 1
                        contextFunc.loc_floats = contextFunc.loc_floats +1
                    elif var.type == "char":
                        var.address = loc_char
                        loc_char = loc_char + 1
                        contextFunc.loc_chars = contextFunc.loc_chars + 1
                else:
                    func_var = sym_table_stack[0].vars[context[-1]].st.vars.get(func.name)

        quad = Quadruple(quadPos, "ERA", func.type, "", factor_id)
        quads.append(quad)
        quadPos = quadPos + 1
        param_vars = func.param_tb.vars.copy()
        pila_operadores.append("FB")

    pila_operandos.pop()
    pila_indexed.pop()
    pila_tipo.pop()
    p[0] = func

# VARCTE
# Calls the corresponding state to construct a constant of type int, float or char
def p_varCte(p):
   '''varCte : constructIntCons
            | constructFloatCons
            | constructCharCons'''

#CONSTRUCT INT CONS
# Reads the constant INT, checks space in memory, appends as operant and type in corresponding
# stacks and calls constatValueAssign to assign the constant value to the address that was just
# assigned
def p_constructIntCons(p):
    '''constructIntCons : INTCTE'''
    global const_int
    checkSpace(0, const_int)
    pila_operandos.append(const_int)
    pila_indexed.append(False)
    pila_tipo.append("int")
    ConstantValueAssign(p[1], const_int)
    const_int = const_int + 1

# CONSTRUCT FLOAT CONS
# Reads the constant FLOAT, checks space in memory, appends as operant and type in corresponding
# stacks and calls constatValueAssign to assign the constant value to the address that was just
# assigned
def p_constructFloatCons(p):
    '''constructFloatCons : FLOATCTE'''
    global const_float
    checkSpace(0, const_float)
    pila_operandos.append(const_float)
    pila_indexed.append(False)
    pila_tipo.append("float")
    ConstantValueAssign(p[1], const_float)
    const_float = const_float +1

# CONSTRUCT CHAR CONS
# Reads the constant CHAR, checks space in memory, appends as operant and type in corresponding
# stacks and calls constatValueAssign to assign the constant value to the address that was just
# assigned
def p_constructCharCons(p):
    '''constructCharCons : CHARCTE'''
    global const_char
    checkSpace(0, const_char)
    pila_operandos.append(const_char)
    pila_indexed.append(False)
    pila_tipo.append("char")
    ConstantValueAssign(p[1], const_char)
    const_char = const_char +1

# LLAMAR FUNCIONES

# LLAMAR FUNCION
# Creates GoSub quadruple used to call a function and calls for corresponding actions
def p_llamar_funcion(p):
    '''llamar_funcion : verificar_funcion_ac llamar_funcion1 RPAREN validate_num_param_ac SEMICOLON'''
    global quadPos
    quad = Quadruple(quadPos, "GoSub", p[1].name, "", p[1].address)
    quads.append(quad)
    quadPos = quadPos + 1

# LLAMAR FUNCION1
# Option to read the exp sent as parameter in the function calling and calls further actions to procede
# with verification of paremeters
def p_llamar_funcion1(p):
  '''llamar_funcion1 : exp validate_params_ac llamar_funcion2
                | empty'''

# LLAMAR FUNCION2
# Option to read the second, third...n parameter in function call and procede to corresponding
# actions to validate the parameters
def p_llamar_funcion2(p):
  '''llamar_funcion2 : COMMA exp validate_params_ac llamar_funcion2
                | empty'''

# checks is function claled is declared in scope and creates its corresponding ERA quadruple
def p_verificar_funcion_ac(p):
    '''verificar_funcion_ac : ID LPAREN'''
    global context
    global quadPos
    global param_vars
    global func_var
    func = GetFunc(p[1])
    if (func is None):
        print("Error: Function not declared in scope")
        quit()
    elif (func.type != "void"):
        print("Error: Expected return value")
        quit()
    else:
        quad = Quadruple(quadPos, "ERA", func.type, "", p[1])
        quads.append(quad)
        quadPos = quadPos + 1
        param_vars = func.param_tb.vars.copy()
    p[0] = func

# VALIDATE PARAMS AC
# Action: validates that the number and type of the parameters in the function call are not more than
# those of the function declatation
def p_validate_params_ac(p):
    '''validate_params_ac : empty'''
    global quadPos
    global param_cont
    if (len(param_vars) != 0 and param_cont >= len(param_vars)):
        print ("Error: number of parameters doesn't match declaration")
        quit()
    else:
        param = pila_operandos.pop()
        pila_indexed.pop()
        paramType = pila_tipo.pop()
        param_vars_list = list(param_vars)
       # param_vars_list.reverse()
        paramName = param_vars_list[param_cont]
        if (paramType != param_vars[paramName].type):
            print ("Error: parameter type mismatch")
            quit()
        else:
            quad = Quadruple(quadPos, "Parameter", param, "", paramName)
            quads.append(quad)
            quadPos = quadPos + 1
            param_cont = param_cont + 1

# VALIDATE NUM PARAMS AC
# Action: validates that the number of parameters in function call matches the number in function 
# declaration
def p_validate_num_param_ac(p):
    '''validate_num_param_ac : empty'''
    global param_cont
    if (param_cont != len(param_vars)):
        print ("Error: number of parameters doesn't match declaration")
        quit()
    else:
        param_cont = 0

# READ
# Read structure
def p_read(p):
    '''read : READ LPAREN read1 RPAREN SEMICOLON'''

# READ1
# First element read
def p_read1(p):
    '''read1 : push_id dim_access read_ac read2'''

# READ2
# Allows multiple reads
def p_read2(p):
    '''read2 : COMMA push_id dim_access read_ac read2
                                    | empty'''

# Action: Finds Variable that will store the user input in read, then creates the quadruple that will make this happen
def p_read_ac(p):
    '''read_ac : empty'''
    global quadPos
    var_address = pila_operandos.pop()
    var_tipo = pila_tipo.pop()
    indexed = pila_indexed.pop()

    quad = Quadruple(quadPos, "READ", "", "", var_address)
    quads.append(quad)
    quadPos = quadPos + 1

# WRITE
# creates write quadruple and calls for corresponding actions
def p_write(p):
  '''write : WRITE LPAREN write1 write2 RPAREN SEMICOLON'''
  

# WRITE1
# Option to call for expression within write or add a constant string 
def p_write1(p):
    '''write1 : expresion
              | agregarStringCTE'''
    global quadPos
    result = pila_operandos.pop()
    pila_indexed.pop()
    resultTipo = pila_tipo.pop()
    quad = Quadruple(quadPos, "WRITE", "", "", result)
    quads.append(quad)
    quadPos = quadPos + 1

#AGREGAR STRING CTE
# Pushes the constant string to the operand stack (pila_operandos), then calls Constant
# ValueAssign to assign the constant value to that variable and finally pushes the type
# into type stacks
def p_agregarStringCTE(p):
    '''agregarStringCTE : STRINGCTE'''
    global const_string
    checkSpace(0, const_string)
    pila_operandos.append(const_string)
    pila_indexed.append(False)
    ConstantValueAssign(p[1], const_string)
    const_string = const_string + 1
    pila_tipo.append("StringCTE")

# WRITE2
# Option to add a second.....n write within the same write expression divided by a comma
def p_write2(p):
  '''write2 : COMMA write1 write2
                | empty'''


# CONDICION
# General structure for the if-else statements and their corresponding actions. 
def p_condicion(p):
  '''condicion : IF LPAREN expresion RPAREN checkIfBool THEN bloque condicion1 endIf SEMICOLON'''

#CHECK IF BOOL
# Verifies that the conditional expression within the if statement is of type Bool
# Creates quadruple that sets up the goTo in case the condition is not met, and sets
# up the jump stack to be filled by appending the current quadruple position
def p_checkIfBool(p):
    '''checkIfBool : empty'''
    global quadPos
    expType = pila_tipo.pop()
    if expType != "bool":
        print ("Error: type mismatch in if condition")
        quit()
    else:
        result = pila_operandos.pop()
        pila_indexed.pop()
        quad = Quadruple(quadPos, "GoToF", result, "", "")
        quads.append(quad)
        pila_saltos.append(quadPos)
        quadPos = quadPos +1

# ENDIF
# Action: Fills the missing information (jump value) in corresponding quadruple when if ends
def p_endIf(p):
    '''endIf : empty'''
    global quadPos
    end = pila_saltos.pop()
    quad = quads[end]
    Fill(quad, quadPos)

# CONDICION1
# Sets up the possible structure of an else statement after an if and sends corresponding
# actions.
def p_condicion1(p):
  '''condicion1 : ELSE elseJump bloque
                    | empty'''

# ELSE JUMP
# Action_ creates GoTo quadruple after else statement and Fills in the information of the jump
# the pending jump that is popped from the jump stack (pila saltos)
def p_elseJump(p):
    '''elseJump : empty'''
    global quadPos
    quad = Quadruple(quadPos, "GoTo", "", "", "")
    quads.append(quad)
    quadPos = quadPos +1
    false = pila_saltos.pop()
    pila_saltos.append(quadPos -1)
    Fill(quads[false], quadPos)


# WHILELOOP
# General structure of a While loop and calling for further actions needed within the loop
def p_whileloop(p):
    ''' whileloop : WHILE push_return_ac expresion handle_exp_ac DO bloque end_while_ac'''

#PUSH RETURN AC
# Action: Append the current quadPosition counter to the jump stack (pila_saltos), this
# will help later on when a jump quadruple will be created (breadcrumbs)
def p_push_return_ac(p):
    '''push_return_ac : empty'''
    global quadPos
    pila_saltos.append(quadPos)

# HANDLE EXP
# Action: Checks that the expression within the condition of a while loop is of type Bool
# If it is bool, creates the GoToF quadruple and stores the current quadPos in the jump
# stack so we can fill the jump information later (breadcrumbs)
def p_handle_exp_ac(p):
    '''handle_exp_ac : empty'''
    global quadPos
    res_type = pila_tipo.pop()
    res = pila_operandos.pop()
    pila_indexed.pop()
    if res_type != "bool":
        print("Error: Type mismatch in While loop, need a Bool condition")
        quit()
    else:
        quad = Quadruple(quadPos, "GoToF", res, "", "")
        quads.append(quad)
        quadPos = quadPos + 1
        pila_saltos.append(quadPos-1)

# END WHILE
# Action: When whileloop ends, it needs to go back to the condition to check if it needs to 
# go into the loop again. Therefore, we create a GoTo quadruple going back to before the evaluation
# of the condition (the position was stored in jump stack, so we get it from there)
def p_end_while_ac(p):
    '''end_while_ac : empty'''
    global quadPos
    end = pila_saltos.pop()
    ret = pila_saltos.pop()
    quad = Quadruple(quadPos, "GoTo", "", "", ret)
    quads.append(quad)
    quadPos = quadPos + 1
    Fill(quads[end], quadPos)

# FORLOOP
# General structure for a for loop implementation and call to further actions required
def p_forloop(p):
    '''forloop : FOR asignacion_for_ac TO exp DO do_ac bloque for_end_ac'''

# ASIGNACION FOR AC
# Checks if the counter variable is declared and is of type int. Then checks if the 
# value assigned to this variable will be of type int. Then, created the assign quadruple
# to make this happen
def p_asignacion_for_ac(p):
  '''asignacion_for_ac : ID EQUALS expresion'''
  global quadPos
  var = FindVar(p[1])

  if var is None:
      print("Error: Counter variable in For Loop is not declared")
      quit()

  resultado = pila_operandos.pop()
  pila_indexed.pop()
  tipoResultado = pila_tipo.pop()
  if tipoResultado != 'int' or var.type != 'int':
      print ("Error: Type mismatch in for assignment with variable " + var.name)
      quit()
  else:
      var.value = resultado
      quad = Quadruple(quadPos,'=',resultado, '', var.address)
      pila_operandos.append(var.address)
      pila_indexed.append(False)
      pila_tipo.append(var.type)
      quads.append(quad)
      quadPos = quadPos + 1

# DO AC
# ACTION WITHIN FOR LOOP
# Action: Checks if the values used the for loops conditions are comparable by calling
# the semantic cube. Then, creates the quadruple for the comparison and the GoTo that will
# send the program to another quadruple when the condition is not met
def p_do_ac(p):
    '''do_ac : empty'''
    global quadPos
    global temp_bool
    pila_saltos.append(quadPos)
    exp = pila_operandos.pop()
    pila_indexed.pop()
    ide = pila_operandos.pop()
    pila_indexed.pop()
    exp_type = pila_tipo.pop()
    id_type = pila_tipo.pop()

    if(sem_cube[1][operand_type[id_type]][operand_type[exp_type]] == "NONE"):
        print("Error: For loop is using non-comparable types")
        quit()

    checkSpace(0, temp_bool)
    quad = Quadruple(quadPos, '>', ide, exp, temp_bool)
    quads.append(quad)
    quadPos = quadPos + 1
    quad1 = Quadruple(quadPos, "GoToT", temp_bool, "", "")
    quads.append(quad1)
    quadPos = quadPos + 1
    temp_bool = temp_bool + 1
    pila_saltos.append(quadPos-1)
    pila_operandos.append(ide)
    pila_indexed.append(False)
    pila_operandos.append(exp)
    pila_indexed.append(False)
    pila_tipo.append(id_type)
    pila_tipo.append(exp_type)

# FOR END AC
# Action: Creates a constant with value 1 and then quadruple that will add 1 to the 
# for loops's counter variable. Then, create the quadruple that will assign this new
# value to the counter variable, and finally, the GoTo quadruple and Fills that will
# tell the program where to jump next and maintain the loop's functionality
def p_for_end_ac(p):
    '''for_end_ac : empty'''
    global const_int
    global quadPos
    global temp_int
    end = pila_saltos.pop()
    ret = pila_saltos.pop()
    exp = pila_operandos.pop()
    pila_indexed.pop()
    ide = pila_operandos.pop()
    pila_indexed.pop()
    exp_type = pila_tipo.pop()
    id_type = pila_tipo.pop()
    checkSpace(0, const_int)
    checkSpace(0, temp_int)
    ConstantValueAssign(1,const_int)
    quad_add = Quadruple(quadPos, '+', ide, const_int, temp_int)
    const_int = const_int + 1
    quads.append(quad_add)
    quadPos = quadPos + 1
    quad_assign = Quadruple(quadPos, '=', temp_int, "", ide)
    quads.append(quad_assign)
    quadPos = quadPos + 1
    temp_int = temp_int + 1

    quad_ret = Quadruple(quadPos, "GoTo", "", "", ret)
    quads.append(quad_ret)
    quadPos = quadPos + 1
    Fill(quads[end], quadPos)

# EMPTY
# Empty structure that allows us to use the empty state in previous states
def p_empty(p):
    '''empty :'''
    pass

# ERROR
# Prints out the error whenever a Parsing Error is found, used in the Lexer
def p_error(p):
    # get formatted representation of stack
    stack_state_str = ' '.join([symbol.type for symbol in parser.symstack][1:])

    print('Syntax error in input! Parser State:{} {} . {}'
          .format(parser.state,
                  stack_state_str,
                  p))

# Construccion de parser
parser = yacc.yacc()

x = input('Titulo del archivo a leer: ')
file = x
fileAnalyzed = open(file, 'r')
data = fileAnalyzed.read()
fileAnalyzed.close()

# Prints intermediate code and calls VM
if parser.parse(data) == "APROPIADO":
    for quad in quads:
        print ("quad: " + str(quad.pos) + " " + quad.op + " " + str(quad.operand1) + " " + str(quad.operand2) + " " + str(quad.result))

    masterFunc(quads, cteMem, sym_table_stack[0],nombre_programa, pointMem)