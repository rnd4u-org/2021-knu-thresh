from Field import Field
from Exceptions import *
import itertools
import random
from math import ceil, log

def MillerRabinPrimalityTest(number):
    if number == 2:
        return True
    elif number == 1 or number % 2 == 0:
        return False

    oddPartOfNumber = number - 1

    timesTwoDividNumber = 0

    while oddPartOfNumber % 2 == 0:
        oddPartOfNumber = oddPartOfNumber / 2
        timesTwoDividNumber = timesTwoDividNumber + 1 

    for time in range(3):

        while True:
            randomNumber = random.randint(2, number)-1
            if randomNumber != 0 and randomNumber != 1:
                break
       
        randomNumberWithPower = pow(randomNumber, oddPartOfNumber) % number
        
        if (randomNumberWithPower != 1) and (randomNumberWithPower != number - 1):
            iterationNumber = 1
        
            while (iterationNumber <= timesTwoDividNumber - 1) and (randomNumberWithPower != number - 1):
                randomNumberWithPower = pow(randomNumberWithPower, 2, number)
                iterationNumber = iterationNumber + 1
            if (randomNumberWithPower != (number - 1)):
                return False
    return True 

class QuotientRingField(Field):

  def __init__(self, order, primalityTest=MillerRabinPrimalityTest):
    if not primalityTest(order):
      raise FieldPrimeOrderException(order)
    self.__order = order
    self.__characteristic = order

  def getOrder(self):
    return self.__order

  def getCharacteristic(self):
    return self.__characteristic

  def __eq__(self, other):
    if(self.__order == other.getOrder() and self.__characteristic == other.__characteristic):
      return True
    return False

  def rdivmod(self, other):
    return int(other % self.getOrder())

  def add(self, a, b):
    return int((a + b) % self.getOrder())

  def sub(self, a, b):
    return int((a - b) % self.getOrder())

  def mul(self, a, b):
    return int((a * b) % self.getOrder())

  def div(self, a, b):
    if b==0:
      raise ZeroDivisionError
    for i in range(1, self.getOrder()):
      if (a * i) % self.getOrder() == b:
        return int(i)

  def __str__(self):
    return "F"+str(self.getOrder())