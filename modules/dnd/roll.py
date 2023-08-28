import re
from numpy.random import SeedSequence, PCG64DXSM, Generator
from time import time_ns

class DiceRoller:
    operators = ['+','-','*','/','^','d',]   
    whitespace = [" ","\n","\r","\t"]  

    def __init__(self):
        tm = time_ns() // 1000000
        ss = SeedSequence(tm)
        generator = PCG64DXSM(ss)

        self.rnd = Generator(generator)
        
    
    def checkValid(self, text: str) -> bool:
        op_db = 0
        cl_db = 0

        for c in text:
            if c == '(': op_db += 1
            elif c == ')': cl_db += 1
            elif c not in [str(n) for n in range(10)] and c not in self.operators and c not in self.whitespace:
                return False

        return op_db == cl_db 

    def replaceWhitespace(self, text: str, replace: str):
        for l in self.whitespace:
            text = text.replace(l, replace)
        return text
    
    def roll(self, times, dice):
        rolls = [int((self.rnd.random() * dice) + 1) for _ in range(times)]
        print(rolls)
        return sum(rolls)
    
    def evalRoll(self, roll: str) -> int:
        if not self.checkValid(roll):
            return None

        roll = self.replaceWhitespace(roll, "").replace("^","**")
        print(roll)
        roll = re.sub("([0-9]+)d([0-9]+)",r"self.roll(\1,\2)",roll)
        roll = re.sub("d([0-9]+)",r"self.roll(1,\1)",roll)
        
        print(roll)
        ret = eval(roll)
        print(ret)

        return ret