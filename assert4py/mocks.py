from inspect import getmembers, isfunction, ismethod
from assert4py.test_runner import TestRunner


class BaseMockFn:

  def __init__(self, class_instance: object, method: str):
    self._original_class = class_instance
    self._original_method = method
    self._original_func = getattr(class_instance, method)
    self._calls = []

  def reset(self):
    self._calls = []

  def restore(self):
    setattr(self._original_class, self._original_method, self._original_func)

class MockFn(BaseMockFn):

  def __init__(self, class_instance: object, method: str):
    super().__init__(class_instance, method)
    setattr(class_instance, method, lambda *args: self._invoke(*args))
    self._mockAction = None
    self._returnVal = None

  def _invoke(self, *args):
    returnVal = None
    if self._mockAction is not None:
      returnVal = self._mockAction.__call__(*args)
    if returnVal is None:
      returnVal = self._returnVal
    self._calls.append((args, returnVal))
    return returnVal

  def __call__(self, *args):
    return self._invoke(*args)

  def thenDo(self, fn):
    self._mockAction = fn.__call__
    return self

  def thenCallOriginal(self):
    self._mockAction = self._original_method
    return self

  def thenReturn(self, value):
    self._returnVal = value

class SpyFn(BaseMockFn):

  def __init__(self, class_instance: object, method: str):
    super().__init__(class_instance, method)
    setattr(class_instance, method, lambda *args: self._invoke(*args))

  def _invoke(self, *args):
    returnVal = self._original_func.__call__(*args)
    self._calls.append((args, returnVal))
    return returnVal

  def __call__(self, *args):
    return self._invoke(*args)

class BaseMock:
  def __init__(self, class_instance: object):
    self.mocks = []
    self._original_class = class_instance

  def reset(self):
    for m in self.mocks:
      m.reset()
  
  def restore(self):
    for m in self.mocks:
      m.restore()

class Mock(BaseMock):

  def __init__(self, class_instance: object):
    super().__init__(class_instance)
    self.mocks = list(map(lambda fn: mockMethod(class_instance, fn[0]), getmembers(class_instance, lambda member: isfunction(member) or ismethod(member))))
    for m in self.mocks:
      setattr(self, m._original_method, m)

  def when(self, method: str) -> MockFn:
    return list(filter(lambda m: m._original_method == method, self.mocks))[0]

class Spy(BaseMock):

  def __init__(self, class_instance: object):
    super().__init__(class_instance)
    self.mocks = list(map(lambda fn: spyMethod(class_instance, fn[0]), getmembers(class_instance, lambda member: isfunction(member) or ismethod(member))))
    for m in self.mocks:
      setattr(self, m._original_method, m)

class MockFnAssertion:
  def __init__(self, mock: BaseMockFn):
    self.mock = mock

  def toHaveBeenCalled(self) -> bool:
    assert len(self.mock._calls) > 0, f"Expected {self.mock._original_class.__name__}.{self.mock._original_method} to have been called"

  def toHaveBeenCalledTimes(self, times: int) -> bool:
    assert len(self.mock._calls) == times, f"Expected {self.mock._original_class.__name__}.{self.mock._original_method} to have been called {times} times, but was actually called {len(self.mock._calls)} times"
  
  def toHaveBeenCalledWith(self, arg) -> bool:
    calls = list(map(lambda invocation: invocation[0], self.mock._calls))
    assert arg in calls, f"Expected {self.mock._original_class.__name__}.{self.mock._original_method} to have been called with {arg}.\nActual calls include {calls}"

  def toHaveLastBeenCalledWith(self, arg) -> bool:
    call = list(map(lambda invocation: invocation[0], self.mock._calls))[len(self.mock._calls)-1]
    assert call == arg, f"Expected {self.mock._original_class.__name__}.{self.mock._original_method} to have last been called with {arg}.\nActual last call was {call}"

  def toHaveReturned(self, value) -> bool:
    calls = list(map(lambda invocation: invocation[1], self.mock._calls))
    assert value in calls, f"Expected {self.mock._original_class.__name__}.{self.mock._original_method} to have returned {value}.\nActual returned values include {calls}"

  def toHaveLastReturned(self, value) -> bool:
    call = list(map(lambda invocation: invocation[1], self.mock._calls))[len(self.mock._calls)-1]
    assert call == value, f"Expected {self.mock._original_class.__name__}.{self.mock._original_method} to have last returned {value}.\nActual last returned value was {call}"

def mockMethod(class_instance: object, method: str) -> MockFn:
  m = MockFn(class_instance, method)
  TestRunner.mocks.append(m)
  return m

def mock(class_instance: object) -> Mock:
  m = Mock(class_instance)
  TestRunner.mocks.append(m)
  return m

def spyMethod(class_instance: object, method: str) -> SpyFn:
  s = SpyFn(class_instance, method)
  TestRunner.mocks.append(s)
  return s

def spy(class_instance: object) -> Spy:
  s = Spy(class_instance)
  TestRunner.mocks.append(s)
  return s

def assertMock(mock: BaseMock or BaseMockFn, method: str = None) -> MockFnAssertion:
  if (issubclass(type(mock), BaseMock) and method is not None):
    mockFn = list(filter(lambda m: m._original_method == method, mock.mocks))[0]
    return MockFnAssertion(mockFn)
  else:
    return MockFnAssertion(mock)