from classes import *
import copy
import numpy as np
# Global Vars
# Instruction Pointer
ip = 0
# Memory structure
memory = Memory()
# Previous IP to return to
ipPrev = []
ipPrev.append(0)
# Name of program
prog_name = ""
# Current context
cur_func = None
# Stack of previous contexts
prev_func = []
# Used to know in which context to search for values or assign
mem_index = -1
# Used to make sure functions have return statement when not void
ret_flag = False

# GETTYPE
# What: finds the corresponding variable type based on address
# Parameters: The address of the variable of which the type is needed
# Returns the type of variable linked to that address
# When is it used: In the READ function, whenever we want to validate that the user input
# matches the variable's expected type. 
def getType(address):
    if(address < 2000):
        return "int"
    elif(address < 4000):
        return "float"
    elif(address < 6000):
        return "char"
    elif(address < 8000):
        return "int"
    elif(address < 10000):
        return "float"
    elif(address < 12000):
        return "char"
    if(address < 14000):
        return "int"
    elif(address < 16000):
        return "float"
    elif(address < 18000):
        return "char"
    elif(address < 20000):
        return "bool"
    elif(address > 27999):
        return getType(findDirInsidePointer(address))
    else:
        return None


# FIND DIR INSIDE POINTER
# What: This function returns the address stored inside a pointer
# Parameters: The variable's address
# Returns the value stored inside the pointer address
# When is it used: in getType, to know the type of a the value the that's being pointed
def findDirInsidePointer(address):
    if (address < 30000):
        return memory.pointMem.intMem[address-28000]

# FINDMEM
# What: This function returns the value stored in the real memory tipe within memory 
# Parameters: The variable's address in quads
# Returns the value stored in the exact index of the memoryType
# When is it used: in MasterFunc, when the switch is reading the quadruples created in compulilation
#              this real address stores the value.
def FindMem(address, i):
    #The outer if indicate the memoryType, the inner ifs indicate what list within that memoryType
    if (address < 6000):
        if(address < 2000):
            return memory.globMem.intMem[address]
        elif(address < 4000):
            return memory.globMem.floatMem[address-2000]
        else:
            return memory.globMem.charMem[address-4000]
    elif (address < 12000):
        if(address < 8000):
            return memory.locMem[i].intMem[address-6000]
        elif(address < 10000):
            return memory.locMem[i].floatMem[address-8000]
        else:
            return memory.locMem[i].charMem[address-10000]
    elif (address < 20000):
        if(address < 14000):
            return memory.tempMem[i].intMem[address-12000]
        elif(address < 16000):
            return memory.tempMem[i].floatMem[address-14000]
        elif(address < 18000):
            return memory.tempMem[i].charMem[address-16000]
        else:
            return memory.tempMem[i].boolMem[address-18000]
    elif (address < 28000):
        if(address < 22000):
            return memory.constMem.stringMem[address-20000]
        elif(address < 24000):
            return memory.constMem.intMem[address-22000]
        elif(address < 26000):
            return memory.constMem.floatMem[address-24000]
        else:
            return memory.constMem.charMem[address-26000]
    elif (address < 30000):
        return FindMem(memory.pointMem.intMem[address-28000], i)
    else:
        print("Error: Memory out of range")
        quit()

# CHANGEVALMEM
# What: This function assignes the value to the corresponding space in memory
# Parameters: The variable's value and address in quads
# Returns nothing, assignes the value if possible, if not, quits the program
# When is it used: in the main function switch statements when the quadruple's job is to assign
# or calculate a result variable, then that result needs to be stored in the address specified in quad
# this is done by sending the value and result address to this function
def ChangeValMem(val, address, i):
    if (address < 6000):
        if(address < 2000):
            memory.globMem.intMem[address] = val
        elif(address < 4000):
            memory.globMem.floatMem[address-2000] = val
        else:
            memory.globMem.charMem[address-4000]= val
    elif (address < 12000):
        if(address < 8000):
            memory.locMem[i].intMem[address-6000]= val
        elif(address < 10000):
            memory.locMem[i].floatMem[address-8000]= val
        else:
            memory.locMem[i].charMem[address-10000]= val
    elif (address < 20000):
        if(address < 14000):
            memory.tempMem[i].intMem[address-12000]= val
        elif(address < 16000):
            memory.tempMem[i].floatMem[address-14000]= val
        elif(address < 18000):
            memory.tempMem[i].charMem[address-16000]= val
        else:
            memory.tempMem[i].boolMem[address-18000]= val
    elif (address > 27999 and address < 30000):
        ChangeValMem(val, memory.pointMem.intMem[address-28000], i)
    else:
        print("Error: Memory out of range")
        quit()

# DELETEMEM
# What: This function resets/deletes all the stored values, locals, parameters and temprary's within a function
# Parameters: The function's name and Function Directory
# Returns nothing, pops the amount of times needed and quits program if the function is not found in scope
# When is it used: in the main function switch statements when the quadruple's job is to assign
# or calculate a result variable, then that result needs to be stored in the address specified in quad
def deleteMem(f_name, dirFunc):
   # the first thing we do is check whether the function's name is the program name, if it is, 
   # then we need to use the global memory
    if(f_name == prog_name):
        mem = memory.globMem
        func = dirFunc.vars[f_name]
        if(func == None):
            print("Error: Function not found "+ f_name)
            quit()
        for i in range(0, func.loc_ints):
            mem.intMem.pop()

        for i in range(0, func.loc_floats):
            mem.floatMem.pop()

        for i in range(0, func.loc_chars):
            mem.charMem.pop()

        memory.tempMem.pop()
    else:
        func = dirFunc.vars[f_name]
        if(func == None):
            print("Error: Function not found "+ f_name)
            quit()
        memory.locMem.pop()
        memory.tempMem.pop()
        

# CONSTRUCT MEM
# What: Constructs memory space needed for current context
# Parameters: The function's name and Function Directory
# Returns nothing, appends the amount of times needed and quits program if the function is not found in scope
# When is it used: in the master when program starts or ERA is called.
def constructMem(f_name, dirFunc):
    if(f_name == prog_name):
        mem = memory.globMem
        func = dirFunc.vars[f_name]
        if(func == None):
            print("Error: function not found "+ f_name)
            quit()
        for i in range(0, func.loc_ints):
            mem.intMem.append(None)

        for i in range(0, func.loc_floats):
            mem.floatMem.append(None)

        for i in range(0, func.loc_chars):
            mem.charMem.append(None)

    else:
        mem = memory.locMem
        func = dirFunc.vars[f_name]
        if(func == None):
            print("Error: function not found "+ f_name)
            quit()
        
        for i in range(0, func.loc_ints):
            mem[-1].intMem.append(None)

        for i in range(0, func.loc_floats):
            mem[-1].floatMem.append(None)

        for i in range(0, func.loc_chars):
            mem[-1].charMem.append(None)

    for i in range(0, func.temp_ints):
        memory.tempMem[-1].intMem.append(None)

    for i in range(0, func.temp_floats):
        memory.tempMem[-1].floatMem.append(None)

    for i in range(0, func.temp_chars):
        memory.tempMem[-1].charMem.append(None)

    for i in range(0, func.temp_bools):
        memory.tempMem[-1].boolMem.append(None)


# MasterFunc
# What: This function is the virtual machine's dirver. It is in charge of reading the quadruples and
# interpreting what to do with that information. It uses all of the functions mentioned above as helper
# functions. 
# Parameters: the list of quads, the constant Memory found in proyecto.py, the function Directory, the 
# program's name and the pointer Memory used to access arrays through indirect referencing
# Returns nothing, calls on other functions oto find and assign values 
# When is it used: it is called by proyecto.py as the connection between the compiler and excecution. This 
# function interprets the quads
def masterFunc(quads, cteMem, dirFunc, nombre_prog, pointMem):
    global ip
    global ipPrev
    global prog_name
    global cur_func
    global prev_func
    global mem_index
    global ret_flag

    # current function is the program name, that is where everything starts
    cur_func = dirFunc.vars[nombre_prog]

    # append a None to previous function because it will help us maintain order with function context
    # later on in the program
    prev_func.append(None)
    
    # the constant memory and pointer memory created in the compiling stage remain the same, so we simply
    # assign them because they were passed on as parameters
    memory.constMem = cteMem
    memory.pointMem = pointMem
    memory.locMem.append(MemoryType())
    memory.tempMem.append(MemoryType())

    prog_name = nombre_prog

    # creation of the global memory
    constructMem(nombre_prog, dirFunc)


    # while loop that traverses the entire list of quads, in order of excecution
    while ip != len(quads):
        # go to case, the actions depend on whether it is go to, go to in True or in False
        # but basically, depending on variable value, it assigns the new ip value or simple adds one
        # if no jump is needed
        if quads[ip].op == "GoTo":
            ip = quads[ip].result
        elif quads[ip].op == "GoToF":
            value = FindMem(quads[ip].operand1, mem_index)
            if value == False:
                ip = quads[ip].result
            else:
                ip = ip + 1
        elif quads[ip].op == "GoToT":
            value = FindMem(quads[ip].operand1, mem_index)
            if value == True:
                ip = quads[ip].result
            else:
                ip = ip + 1

        # write case finds the value stored in the specific address and prints it out as output
        # then adds one to ip counter
        elif quads[ip].op == "WRITE":
            dir = quads[ip].result
            value = FindMem(dir, mem_index)
            print(str(value))
            ip = ip + 1
        
        # the addition case finds the value stored in the operand's addresses, adds both of them and
        # stores it the result address specified in quadruple
        elif quads[ip].op == "+":
            dir1 = quads[ip].operand1
            dir2 = quads[ip].operand2
            val1 = FindMem(dir1, mem_index)
            val2 = FindMem(dir2, mem_index)
            res = val1 + val2
            resDir = quads[ip].result
            ChangeValMem(res, resDir, mem_index)
            ip = ip + 1

        # the +dir case is used to diferenciate the quadruples that are used to calculate where the array
        elif quads[ip].op == "+dir":
            dir1 = quads[ip].operand1
            val2 = quads[ip].operand2
            val1 = FindMem(dir1, mem_index)
            res = val1 + val2
            resDir = quads[ip].result
            memory.pointMem.intMem[resDir-28000] = res
            ip = ip + 1

        # the subtraction case finds the value stored in the operand's addresses, subtracts both of them and
        # stores it the result address specified in quadruple. Then adds one to the ip counter.
        elif quads[ip].op == "-":
            dir1 = quads[ip].operand1
            dir2 = quads[ip].operand2
            val1 = FindMem(dir1, mem_index)
            val2 = FindMem(dir2, mem_index)
            res = val1-val2
            resDir = quads[ip].result
            ChangeValMem(res, resDir, mem_index)
            ip = ip + 1

        # the multiplication case finds the value stored in the operand's addresses, multiplies both of them and
        # stores it the result address specified in quadruple. Then adds one to the ip counter.
        elif quads[ip].op == "*":
            dir1 = quads[ip].operand1
            dir2 = quads[ip].operand2
            val1 = FindMem(dir1, mem_index)
            val2 = FindMem(dir2, mem_index)
            res = val1*val2
            resDir = quads[ip].result
            ChangeValMem(res, resDir, mem_index)
            ip = ip + 1

        # the division case finds the value stored in the operand's addresses, divides both of them and
        # stores it the result address specified in quadruple. Then adds one to the ip counter.
        elif quads[ip].op == "/":
            dir1 = quads[ip].operand1
            dir2 = quads[ip].operand2
            val1 = FindMem(dir1, mem_index)
            val2 = FindMem(dir2, mem_index)
            res = val1/val2
            resDir = quads[ip].result
            ChangeValMem(res, resDir, mem_index)
            ip = ip + 1

        # the greater than case finds the value stored in the operand's addresses, compares both of them and
        # stores the result in the address specified as result in the quadruple. Then adds one to the ip counter
        elif quads[ip].op == ">":
            dir1 = quads[ip].operand1
            dir2 = quads[ip].operand2
            val1 = FindMem(dir1, mem_index)
            val2 = FindMem(dir2, mem_index)
            res = val1 > val2
            resDir = quads[ip].result
            ChangeValMem(res, resDir, mem_index)
            ip = ip + 1
        
        # the less than case finds the value stored in the operand's addresses, compares both of them and
        # stores the result in the address specified as result in the quadruple. Then adds one to the ip counter
        elif quads[ip].op == "<":
            dir1 = quads[ip].operand1
            dir2 = quads[ip].operand2
            val1 = FindMem(dir1, mem_index)
            val2 = FindMem(dir2, mem_index)
            res = val1 < val2
            resDir = quads[ip].result
            ChangeValMem(res, resDir, mem_index)
            ip = ip + 1
        
        # the equalsequals case finds the value stored in the operand's addresses, compares both of them and
        # stores the result in the address specified as result in the quadruple. Then adds one to the ip counter
        elif quads[ip].op == "==":
            dir1 = quads[ip].operand1
            dir2 = quads[ip].operand2
            val1 = FindMem(dir1, mem_index)
            val2 = FindMem(dir2, mem_index)
            res = (val1 == val2)
            resDir = quads[ip].result
            ChangeValMem(res, resDir, mem_index)
            ip = ip + 1

        # the not equal case finds the value stored in the operand's addresses, compares both of them and
        # stores the result in the address specified as result in the quadruple. Then adds one to the ip counter
        elif quads[ip].op == "!=":
            dir1 = quads[ip].operand1
            dir2 = quads[ip].operand2
            val1 = FindMem(dir1, mem_index)
            val2 = FindMem(dir2, mem_index)
            res = (val1 != val2)
            resDir = quads[ip].result
            ChangeValMem(res, resDir, mem_index)
            ip = ip + 1
        
        # The assign case acceses the value in the operand's address, and assigns it to the result address
        # Then adds one to the ip counter
        elif quads[ip].op == "=":
            dir = quads[ip].operand1
            val = FindMem(dir, mem_index)
            resDir = quads[ip].result
            ChangeValMem(val, resDir, mem_index)
            ip = ip + 1

        # the ERA  case reserves the memory needed for a function when the function is called.
        # Then adds one to the ip counter
        elif quads[ip].op == "ERA":
            func_id = quads[ip].result
            func_type = quads[ip].operand1

            if(func_type != "void"):
                ret_flag = True

            prev_func.append(cur_func)
            cur_func = dirFunc.vars[func_id]
            
            memory.locMem.append(MemoryType())
            memory.tempMem.append(MemoryType())
            for i in range(0, cur_func.param_ints):
                memory.locMem[-1].intMem.append(None)
            for i in range(0,cur_func.param_floats):
                memory.locMem[-1].floatMem.append(None)
            for i in range(0,cur_func.param_chars):
                memory.locMem[-1].charMem.append(None)
            constructMem(func_id, dirFunc)
            ip = ip + 1
            mem_index = -2
        
        # the Parameter case recieves the Parameter and a value, it is in charge of assigning that value to the 
        # local function's parameter. Then increments the ip counter by 1
        elif quads[ip].op == "Parameter":
            dir = quads[ip].operand1
            var_name = quads[ip].result
            var = cur_func.param_tb.vars[var_name]
            val = FindMem(dir, mem_index)
            ChangeValMem(val, var.address, -1)
            ip = ip + 1

        # the GoSub case appends the current context as a previous ip and then changes the ip to the address stored
        # in the quadruple's result address
        elif quads[ip].op == "GoSub":
            ipPrev.append(ip + 1)
            ip = quads[ip].result
            mem_index = -1
        
        #the EndFunc case sends you back to the ip address that should be accessed after the function call,
        # deletes the function's memory and then returns the current function context to the previous function
        elif quads[ip].op == "EndFunc":
            if(ret_flag):
                print("Error: Expected return statement")
            ip = ipPrev.pop()
            deleteMem(cur_func.name, dirFunc)
            cur_func = prev_func.pop()

        # the return case finds the return variable created for that function, assigns the return value to that variable
        # and then increments the ip counter by 1    
        elif quads[ip].op == "RETURN":
            ret_flag = False
            var = prev_func[-1].st.vars[cur_func.name]
            val = FindMem(quads[ip].result, mem_index)
            ChangeValMem(val, var.address, mem_index-1)
            ip = ip + 1

        # the verify quadruple checks that the index being accessed in a one or two dimentional variable is within the
        # corresponding node's limits. Then increments the ip counter by one.  
        elif quads[ip].op == "VERIFY":
            val = FindMem(quads[ip].operand1, mem_index)
            limInf = quads[ip].operand2
            limSup = quads[ip].result
            if(val < limInf or val > limSup):
                print("Error: Index out of range")
                quit()
            ip = ip + 1
        
        # the and case finds the value stored in the operand's addresses, compares both of them and
        # stores the and result comparison in the result address specified in quadruple. Then increments the 
        # ip counter by one. 
        elif quads[ip].op == "and":
            val1 = FindMem(quads[ip].operand1, mem_index)
            val2 = FindMem(quads[ip].operand2, mem_index)
            resDir = quads[ip].result
            val = val1 and val2
            ChangeValMem(val, resDir, mem_index)
            ip = ip + 1    

        # the or case finds the value stored in the operand's addresses, compares both of them and
        # stores the or result comparison in the result address specified in quadruple. Then increments the 
        # ip counter by one. 
        elif quads[ip].op == "or":
            val1 = FindMem(quads[ip].operand1, mem_index)
            val2 = FindMem(quads[ip].operand2, mem_index)
            resDir = quads[ip].result
            val = val1 or val2
            ChangeValMem(val, resDir, mem_index)
            ip = ip + 1
        
        # the read case asks the user for an input, and then depending on the address where that value
        # will be stored, compares the expected type to the inputted type, if not compatible, explains 
        # with error message and quits program, if possible, then assigns the new value to that address. 
        # Then increments the ip counter by one. 
        elif quads[ip].op == "READ":
            varAddress = quads[ip].result
            ty = getType(varAddress)
            if(ty == "int"):
                try:
                    inVal = int(input("Input: "))
                except ValueError:
                    print("Error: Not an integer!")
                    quit()
            elif(ty == "float"):
                try:
                    inVal = float(input("Input: "))
                except ValueError:
                    print("Error: Not a float!")
                    quit()
            elif(ty == "char"):
                inVal = input("Input: ")
                if(len(inVal) > 1):
                    print("Error: Strings not supported")
                    quit()
            else:
                print("Error: No variable to read")
                quit()

            ChangeValMem(inVal, varAddress, mem_index)

            ip = ip + 1
        
        # Used to assign structures, it copies the values from the right operand to the left opperand using offset
        elif quads[ip].op == "=dim":
            offset = quads[ip].result
            var = quads[ip].operand1
            result = quads[ip].operand2

            for i in range(0,offset):
                val = FindMem(result + i, mem_index)
                ChangeValMem(val, var + i, mem_index)
            ip = ip + 1

        # Used to verify dimension compatibility
        elif quads[ip].op == "VerifyLS":
            if quads[ip].operand1 != quads[ip].operand2:
                print("Error: Wrong dimensions")
                quit()
            else:
                ip = ip + 1
        
        # Used to add dimensioned variables or structures. Uses information from quads to find and add values
        # then, it stores them in a temp structure using offset.
        elif quads[ip].op == "+dim":
            var1 = quads[ip].operand1
            var2 = quads[ip].operand2
            resultVar = quads[ip].result
            ip = ip + 1
            # there is a mandatory quadruple after +dim that just sends the offset of the temp variable created earlier
            offset = quads[ip].result
            for i in range(0, offset):
                val1 = FindMem(var1 + i, mem_index)
                val2 = FindMem(var2 + i, mem_index)
                valRes = val1 + val2
                ChangeValMem(valRes, resultVar + i, mem_index)
            ip = ip + 1
        
        # Used to subtract dimensioned variables or structures. Uses information from quads to find and substract values
        # then, it stores them in a temp structure using offset.
        elif quads[ip].op == "-dim":
            var1 = quads[ip].operand1
            var2 = quads[ip].operand2
            resultVar = quads[ip].result
            ip = ip + 1
            # there is a mandatory qudruple after -dim that just sends the offset of the temp variable created earlier
            offset = quads[ip].result
            for i in range(0, offset):
                val1 = FindMem(var1 + i, mem_index)
                val2 = FindMem(var2 + i, mem_index)
                valRes = val1 - val2
                ChangeValMem(valRes, resultVar + i, mem_index)
            ip = ip + 1

        # Used to multiply dimensioned variables or structures. Uses information from quads to find and multiply values
        # then, it stores them in a temp structure using row and column info.
        elif quads[ip].op == "*dim":
            var1 = quads[ip].operand1
            var2 = quads[ip].operand2
            resultVar = quads[ip].result
            ip = ip + 1
            # there is a mandatory qudruple after *dim that sends row and column of first matrix
            first_r = quads[ip].operand1 +1
            first_c = quads[ip].operand2 +1
            ip = ip + 1
            # there is a second mandatory qudruple that sends row and column of second matrix
            second_r = quads[ip].operand1 +1 
            second_c = quads[ip].operand2+1

            res_type = getType(resultVar)

            # reconstructing first matrix
            mat1 = np.zeros((first_r,first_c))
            off1 = 0
            for i in range(0, first_r):
                for j in range(0, first_c):
                    mat1[i][j] = FindMem(var1+off1, mem_index)
                    off1 = off1 + 1

            # reconstructing second matrix
            mat2 = np.zeros((second_r, second_c))
            off2 = 0
            for i in range(0, second_r):
                for j in range(0, second_c):
                    mat2[i][j] = FindMem(var2+off2, mem_index)
                    off2 = off2 + 1

            # creating result matrix
            mat3 = np.dot(mat1,mat2)
            if res_type == "int":
                mat3 = mat3.astype(int)
            
             # storing result matrix in memory
            off3 = 0
            for i in range(0, first_r):
                for j in range(0, second_c):
                    ChangeValMem(mat3[i][j], resultVar + off3, mem_index)
                    off3 = off3+1         
            
            ip = ip + 1

        # Used to calculate the determinant of a matrix
        elif quads[ip].op == "DET":
            mat_address = quads[ip].operand1
            det = quads[ip].result
            # there is a mandatory qudruple after DET that sends structure's dimensions (only need one because it's squared)
            ip = ip + 1
            mat_d = quads[ip].operand1 + 1

            # reconstructing matrix
            mat = np.zeros((mat_d, mat_d))
            off = 0
            for i in range(0, mat_d):
                for j in range(0, mat_d):
                    mat[i][j] = FindMem(mat_address+off, mem_index)
                    off = off + 1
            
            det_val = np.linalg.det(mat)
             # storing determinant value
            ChangeValMem(det_val, det, mem_index)
            ip = ip + 1

        # Used to calculate the transpose of a matrix
        elif quads[ip].op == "TRAN":
            mat_address = quads[ip].operand1
            tran = quads[ip].result
            mat_type = getType(mat_address)
            # there is a mandatory quadruple after TRAN that sends the stucture's dimensions
            ip = ip + 1
            mat_r = quads[ip].operand1 + 1
            mat_c = quads[ip].operand2 + 1


            # specific char matrix created to support char transpose
            if mat_type == "char":
                mat = np.chararray((mat_r, mat_c), unicode=True)
            else:
                mat = np.zeros((mat_r, mat_c))
            
            # reconstructing matrix
            off = 0
            for i in range(0, mat_r):
                for j in range(0, mat_c):
                    temp = FindMem(mat_address+off, mem_index)
                    if mat_type == "char":
                        temp = temp[1:2]
                    mat[i][j] = temp
                    off = off + 1

            tran_mat = mat.transpose()

            if mat_type == "int":
                tran_mat = tran_mat.astype(int)

             # storing transposed matrix
            off1 = 0
            for i in range(0, mat_c):
                for j in range(0, mat_r):
                    ChangeValMem(tran_mat[i][j], tran + off1, mem_index)
                    off1 = off1 + 1
            ip = ip + 1
        
        # Used to calculate the inverse of a matrix, but first verifies determinant is not 0 in order to do so.
        elif quads[ip].op == "VerifyDet":

            det = quads[ip].result
            det_val = FindMem(det, mem_index)
            if(det_val == 0.0):
                print("Error: Cannot get inverse if determinant is equal to zero")
                quit()
            
            # there is a mandatory quadruple that sends matrix address and dimensions as well as the result address
            ip = ip + 1
            mat_dim = quads[ip].operand1 + 1
            mat_address = quads[ip].operand2
            res_address = quads[ip].result

            mat = np.zeros((mat_dim, mat_dim))

            # reconstructing matrix
            off = 0
            for i in range(0, mat_dim):
                for j in range(0, mat_dim):
                    mat[i][j] = FindMem(mat_address+off, mem_index)
                    off = off + 1

            inv_mat = np.linalg.inv(mat)

            # storing inverse matrix
            off1 = 0
            for i in range(0, mat_dim):
                for j in range(0, mat_dim):
                    ChangeValMem(inv_mat[i][j], res_address + off1, mem_index)
                    off1 = off1 + 1

            ip = ip + 1
        
        # if the quadruple's operator is something different than all the cases above, there is an error, 
        # explains with error and quits program.  
        else:
            print("Error: Instruction is not supported")
            quit()