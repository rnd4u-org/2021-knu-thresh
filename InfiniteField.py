from Field import Field
import numpy as np

class InfiniteField(Field):

  def __init__(self):
    self.__order = np.inf
    self.__characteristic = 0

  def getOrder(self):
    return self.__order

  def getCharacteristic(self):
    return self.__characteristic

  def __eq__(self, other):
    if(self.__order == other.getOrder() and self.__characteristic == other.__characteristic):
      return True
    return False

  def rdivmod(self, other):
    res = other
    if int(res) == res:
      return int(res)
    return res

  def add(self, a, b):
    res = (a + b)
    if int(res) == res:
      return int(res)
    return res

  def sub(self, a, b):
    res = (a - b)
    if int(res) == res:
      return int(res)
    return res

  def mul(self, a, b):
    res = (a * b)
    if int(res) == res:
      return int(res)
    return res

  def div(self, a, b):
    if b==0:
      raise ZeroDivisionError()
    res = (a/b)
    if int(res) == res:
      return int(res)
    return res

  def __str__(self):
    return "R"