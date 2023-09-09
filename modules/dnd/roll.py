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
    
    def roll(self, dice, advantage = 0): # -1 -> dis, 1 -> adv, 2 -> elven accuracy
        rolls = [(self.rnd.random() * dice) + 1]
        if abs(advantage) > 0: rolls.append((self.rnd.random() * dice) + 1)
        if advantage > 1: rolls.append((self.rnd.random() * dice) + 1)

        return min(rolls) if advantage < 0 else max(rolls)

    def rollMany(self, times, dice, advantage=0): 
        rolls = [self.roll(dice, advantage) for _ in range(times)]          
        print(rolls)
        return sum(rolls)
    
    def evalRoll(self, roll: str, advantage = 0) -> int:
        if not self.checkValid(roll):
            return None

        roll = self.replaceWhitespace(roll, "").replace("^","**")
        print(roll)
        roll = re.sub("([0-9]+)d([0-9]+)",r"self.rollMany(\1,\2," + str(advantage) + ")",roll)
        roll = re.sub("d([0-9]+)",r"self.roll(\1," + str(advantage) + ")",roll)
        
        print(roll)
        ret = eval(roll)
        print(ret)

        return ret