class FieldOrderException(Exception):

  def __init__(self, order, massage="Incorrect order. Order must be a power of a prime number."):
    self.massage = massage
    self.order = order
    super().__init__(self.massage)
  
  def __str__(self):
    return f'{self.order} -> {self.massage}'

class FieldPrimeOrderException(Exception):

  def __init__(self, order, massage="Incorrect order. Order must be a prime number."):
    self.massage = massage
    self.order = order
    super().__init__(self.massage)
  
  def __str__(self):
    return f'{self.order} -> {self.massage}'

class ZeroCoefficientError(Exception):

  def __init__(self, massage="The coefficient of leading term is zero."):
    self.massage = massage
    super().__init__(self.massage)
  
  def __str__(self):
    return f'{self.massage}'

class DifferentFieldsError(Exception):

  def __init__(self, a, b, f1, f2, massage="Not available to operate with elements from different fields"):
    self.massage = massage
    self.a = a
    self.b = b
    super().__init__(self.massage)
  
  def __str__(self):
    return f'{self.a} from {f1} and {self.b} from {f2} -> {self.massage}'