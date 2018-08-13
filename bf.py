''' A simple Brainfuck Interpreter written in Python 3.6
Copyright 2018 LiquidFox1776

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included
in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS 
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

usage: bf.py [-h] --file FILE [--number_of_cells NUMBER_OF_CELLS]
             [--max_cells MAX_CELLS]

optional arguments:
  -h, --help            show this help message and exit
  --file FILE, -f FILE  Program file to run
  --number_of_cells NUMBER_OF_CELLS, -n NUMBER_OF_CELLS
                        Number of cells to start off with, default is 30000, not affected by max_cells
  --max_cells MAX_CELLS, -m MAX_CELLS
                        Limits the number of cells that can be created after number_of_cells is defined
'''
import sys
import traceback
import os
import argparse

class BFI :
    '''Brainfuck Interpreter Class'''
    def __init__(self, number_of_cells=30000, max_cells=0, program='') :
        self.number_of_cells = self.validate_number_of_cells(number_of_cells)
        self.max_cells = self.validate_max_cells(max_cells)
        
        self.cell_pointer = 0
        self.instruction_pointer = 0
        self.cells = [0] * self.number_of_cells
        self.while_stack = []
        self.tmp_while_stack = []
        self.program = program

    def validate_number_of_cells(self, number_of_cells) :
        ''' Checks if number_of_cells is a valid int and greater than 0
        it then returns 30000 if number_of_cells is None'''
        if number_of_cells != None :
            try :
                number_of_cells = int(number_of_cells)
            except ValueError :
                print("Number of cells must be an integer")
                exit(1)

            if number_of_cells < 1 :
                print("Number of cells must be greater than 0")
                exit(1)
            
            return int(number_of_cells)
        else :
            return 30000
            
    def validate_max_cells(self, max_cells) :
        ''' Checks if max_cells is a valid int and greater than 0
        it then returns 0 if max_cells is None'''
        if max_cells != None :
            try :
                max_cells = int(max_cells)
            except ValueError :
                print("Number of cells must be an integer")
                exit(1)

            if max_cells < 1 :
                print("Number of cells must be greater than 0")
                exit(1)
                
            return int(max_cells)        
        else :
            return -1 #don't impose a limit
    def increase_cell_array(self) :
        ''' Determines if the cell array needs to be increased and will increase the cell array as needed'''
        try :
            if (self.cell_pointer > self.max_cells) and (self.max_cells != -1):
                print("Cannot increase the number of cells due to the user imposed max_cells limit.")
                exit(1)
 
            if self.cell_pointer > (len(self.cells) - 1) : #Allocate extra cells as needed
                self.cells.extend([0] * (self.cell_pointer - (len(self.cells) -1 )))
        except Exception as ex :
            traceback.print_exc()
            exit(1)

    def increase_cell_pointer(self) :
        '''Increases the cell_pointer by 1'''
        self.instruction_pointer += 1
        self.cell_pointer += 1

    def decrease_cell_pointer(self) :
        '''Decreases cell_pointer by one, limits cell_pointer to a minimum value of zero if a negative value occurs'''
        self.instruction_pointer += 1
        
        if self.cell_pointer > 0 : #Can't go negative in the cell array
            self.cell_pointer -= 1
        else :
            self.cell_pointer = 0

    def increase_cell_value(self) :
        '''Increases the value in the current cell, wraps around to 0 when the cell value is 255'''
        self.instruction_pointer += 1

        self.increase_cell_array()
        if self.cells[self.cell_pointer] == 255 : #Do a wrap around if true
            self.cells[self.cell_pointer] = 0
        else :
            self.cells[self.cell_pointer] += 1

    def decrease_cell_value(self) :
        '''Decreases the value in the current cell, wraps around to 255 when the cell value is 0'''
        self.instruction_pointer += 1
        self.increase_cell_array()
                
        if self.cells[self.cell_pointer] == 0 :
            self.cells[self.cell_pointer] = 255 #Do a wrap around if true
        else :
            self.cells[self.cell_pointer] -= 1

    def print_char(self) :
        '''Prints a single character'''
        print(chr(self.cells[self.cell_pointer]), end='')
        self.instruction_pointer += 1

    def get_char(self) :
        '''Reads a single character'''
        self.cells[self.cell_pointer] = ord(sys.stdin.read(1))
        self.instruction_pointer += 1

    def while_begin(self) :
        '''Handles the [ instruction, exits if n unbalanced [] is detected'''
        if ( self.cells[self.cell_pointer] == 0 ): #If the current cell = 0 skip to the next matching ]
            for i in range(self.instruction_pointer, len(self.program)) : #Loop from the current point in the program to the end
                if self.program[i] == ']' :
                    self.tmp_while_stack.remove(self.tmp_while_stack[-1])
                    if len(self.tmp_while_stack) == 0 : #if true we have reached the matching ]
                        self.instruction_pointer = i + 1
                        break
                elif self.program[i] == '[' :
                    self.tmp_while_stack.append(i)
            if len(self.tmp_while_stack) > 0 :
                print("Unbalanced [ detected")
                exit(1)
        else :
            self.while_stack.append(self.instruction_pointer) # add the current location to the stack
            self.instruction_pointer += 1

    def while_end(self) :
        '''Handles the ] instruction, exits if n unbalanced [] is detected'''
        if(self.cells[self.cell_pointer] != 0) :
            if len(self.while_stack) > 0 :
                self.instruction_pointer = self.while_stack[-1] + 1
            else :
                print("Unbalanced ] detected")
                exit(1)
        else :
            self.instruction_pointer += 1
            if len(self.while_stack) > 0 :
                self.while_stack.remove(self.while_stack[-1])
            else :
                print("Unbalanced ] detected")
                exit(1)

    def run(self) :
        '''Executes the Brainfuck program'''
        while self.instruction_pointer < len(self.program) :
            if self.program[self.instruction_pointer] == '>' :
                self.increase_cell_pointer()
            elif self.program[self.instruction_pointer] == '<' :
                self.decrease_cell_pointer()
            elif self.program[self.instruction_pointer] == '+' :
                self.increase_cell_value()
            elif self.program[self.instruction_pointer] == '-' :
                self.decrease_cell_value()
            elif self.program[self.instruction_pointer] == '.' :
                self.print_char()
            elif self.program[self.instruction_pointer] == ',' :
                self.get_char()
            elif self.program[self.instruction_pointer] == '[' :
                self.while_begin()
            elif self.program[self.instruction_pointer] == ']' :
                self.while_end()
            else : #ignore all other characters
                self.instruction_pointer += 1
                
def load_file(file_name) :
    '''Loads a program from disk into memory'''
    if os.path.isfile(file_name) : #make sure the file exists
        try :
            with open(file_name, "r") as file :
                return file.read()
        except IOError:
            print("Cannot read " + file_name)
            return ''
    else :
        print(file_name + ' does not exist')
        return ''

if __name__ == '__main__' :
    parser = argparse.ArgumentParser()
    parser.add_argument('--file', '-f' ,help='Program file to run', required=True)
    parser.add_argument('--number_of_cells', '-n', help='Number of cells to start off with, default is 30000, not affected by max_cells', required=False)
    parser.add_argument('--max_cells', '-m', help='Limits the number of cells that can be created after number_of_cells is defined', required=False)
    args = parser.parse_args()
    
    program = load_file(args.file)
    if program != '' :
        #number_of_cells = validate_number_of_cells(args.number_of_cells)
        #max_cells = validate_max_cells(args.max_cells)
        bf = BFI(number_of_cells=args.number_of_cells, program=program, max_cells=args.max_cells)
        bf.run()
