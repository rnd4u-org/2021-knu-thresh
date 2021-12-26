from Exceptions import *

class Coefficient:

  def __init__(self, number, field):
    self.__field = field
    self.__number = field.rdivmod(number)

  def getNumber(self):
    return self.__number

  def getField(self):
    return self.__field

  def isZero(self):
    return self.getNumber() == 0

  def __add__(self, other):
    if self.getField() != other.getField():
      raise DifferentFieldsError(self.getNumber(), other.getNumber(), self.getField(), other.getField())
    return self.getField().add(self.getNumber(), other.getNumber())

  def __sub__(self, other):
    if self.getField() != other.getField():
      raise DifferentFieldsError(self.getNumber(), other.getNumber(), self.getField(), other.getField())
    return self.getField().sub(self.getNumber(), other.getNumber())

  def __mul__(self, other):
    if self.getField() != other.getField():
      raise DifferentFieldsError(self.getNumber(), other.getNumber(), self.getField(), other.getField())
    return self.getField().mul(self.getNumber(), other.getNumber())

  def __truediv__(self, other):
    if self.getField() != other.getField():
      raise DifferentFieldsError(self.getNumber(), other.getNumber(), self.getField(), other.getField())
    return self.getField().div(self.getNumber(), other.getNumber())

  def __str__(self):
    return str(self.getNumber())

  def __eq__(self, other):
    if self.getField() != other.getField():
      raise DifferentFieldsError(self.getNumber(), other.getNumber(), self.getField(), other.getField())
    return self.getNumber() == other.getNumber()