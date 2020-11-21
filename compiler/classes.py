# Memory Structure

# Class that stores all information regarding the node of the dimension that the user is currently in
# We chose to create a structure to group data
# The first node contains more information for quick access
class Node:
    # Lower limit of access bounds
    limiteInferior = None
    # Uper limit of access bounds
    limiteSuperior = None
    # M value of the current node
    valorM = None
    # Pointer to next dimension
    nextDim = None
    # R value of the current node
    valorR = None

    # The following variables only have values in the first dimension
    # Total offset of the structure (array or matrix)
    arrayOffset = None
    # Number of dimensions in the structure
    arrayDim = None
    # Base address of the structure
    base_address = None

    def __init__(self, limSuperior):
        self.limiteInferior = 0
        self.limiteSuperior = limSuperior

# Structure that aids in memory architecture
# Separates a memory by type being accessed. The type is identified with ranges
# For a deeper explanation of its use, read the explanation of the following class.
# If the memory kind doesn't have a certain memory type (ej. Local Memory does not have Bools or Strings),
# those arrays will remain empty
class MemoryType:

    def __init__(self):
        # Int Memory
        self.intMem = []
        # Float Memory
        self.floatMem = []
        # Char Memory
        self.charMem = []
        # Bool Memory
        self.boolMem = []
        # String Memory
        self.stringMem = []

# Structure used as memory
# We divided the memory into each potential kind (global, local, temporal, constant, pointer)
# In order to translate memory address with actual address in a quick way (ej. Global variables are ranged from 0-5999
# if the address is within that range we know we should store it in globMem section)
# Each kind of memory has the value of another structure that is basically the division of variable type (int, float, char, bool, string)
# We decided this was the best way to access and store values because of it's simplicity and logic.
#
# Complete Example of Memory Access:
# Memory being accessed: 2010
# Because we know the upper and lower bounds of each kind of memory we know that globals are stored from 0-5999 (see proyecto.py Line 66)
# Therefore in the object memory we will access the object globMem
# We also know that for global memory floats are stored from 2000-3999 which is why we know that the value being accessed is a float
# Since we know that floats start from 2000, we know that the index 0 of floatMem is actually 2000 which is why 2010 is the 10th
# element of float mem.
# Address = 2010
# The access is as follows: memory.globMem.floatMem[Address-2000]
class Memory:
    def __init__(self):
        # Global Memory
        self.globMem = MemoryType()
        # Local Memory
        self.locMem = []
        # Temporal Memory
        self.tempMem = []
        # Constant Memory
        self.constMem = MemoryType()
        # Pointer Memory
        self.pointMem = MemoryType()



# Structure used to construct Symbol Tables
# They store the name (ID) of the table, the position it has in the symbol table stack and 
# the variables inside that ST.
# We used vars as a map in order to have quick access to the variables used.
class SymbolTable:
    name = None
    pos = None
    # The key is the variable name and the value is the actual Var object.
    vars = {}

    def __init__(self, vars = None):
        if vars is None:
            self.vars = {}

# Structure used to store variable information
# We decided to create this structure to group data and for quick access
class Var:
    # Variable ID
    name = None
    # Int, Float or Char
    type = None
    # Pending Adjustment: CHECA SI LO USAMOS
    value = None
    # The address the variable is stored in
    address = None
    # If the variable has dimentions, this will point to the first node
    # If it doesn't, it will always be None
    dimention = None

    def __init__(self, n, t):
        self.name = n
        self.type = t

# Structure used to store function information
# We decided to create this structure to group data about a function for quick access
class Func:
    # Function ID
    name = None
    # Int, Float, Char or Void
    type = None
    # Function's Symbol Table
    st = None
    # Function's Parameter Table
    param_tb = None
    # Pending Adjustment: CHECA SI LO USAMOS
    address = None
    # Quadruple where the function starts
    init_quad = None
    # Int space needed for parameters
    param_ints = 0
    # Float space needed for parameters
    param_floats = 0
    # Char space needed for parameters
    param_chars = 0
    # Int space needed for local variables
    loc_ints = 0
    # Float space needed for local variables
    loc_floats = 0
    # Char space needed for local variables
    loc_chars = 0
    # Int space needed for temporal variables
    temp_ints = 0
    # Float space needed for temporal values
    temp_floats = 0
    # Char space needed for temporal values
    temp_chars = 0
    # Bool space needed for temporal values
    temp_bools = 0
    # Strings space needed for constant values
    const_strings = 0

    def __init__(self, n, t):
        self.name = n
        self.type = t

# Structure that holds all quadruple information
# This is used for quadruple formation
class Quadruple:
    # Number of quadruple
    pos = None
    # Operator
    op = None
    operand1 = None
    operand2 = None
    result = None

    def __init__(self, p, o, o1, o2, r):
        self.pos = p
        self.op = o
        self.operand1 = o1
        self.operand2 = o2
        self.result = r

# Structure used as Parameter Table used in functions
# Stores all parameters
# We used vars as a map in order to have quick access to the variables used.
class ParamTable:
    # The key is the variable name and the value is the actual Var object.
    vars = {}
    def __init__(self, vars = None):
        if vars is None:
            self.vars = {}