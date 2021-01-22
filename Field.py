from abc import ABC, abstractmethod

class Field(ABC):

  @abstractmethod
  def getOrder(self):
    pass

  @abstractmethod
  def getCharacteristic(self):
    pass

  @abstractmethod
  def __eq__(self, other):
    pass

  @abstractmethod
  def rdivmod(self, other):
    pass

  @abstractmethod
  def add(self, a, b):
    pass

  @abstractmethod
  def sub(self, a, b):
    pass

  @abstractmethod
  def mul(self, a, b):
    pass

  @abstractmethod
  def div(self, a, b):
    pass

  @abstractmethod
  def __str__(self):
    pass