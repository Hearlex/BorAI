import string
import math

def convertNumberToLetter(number):
    letters_length = len(string.ascii_uppercase)
    
    number_of_letters = 1
    if number > 0:
        number_of_letters = math.floor(math.log(number, letters_length)) + 1
    
    letters = ""
    for _ in range(number_of_letters):
        letters = string.ascii_uppercase[number % letters_length] + letters
        number = math.floor(number / letters_length) - 1
        
    return letters