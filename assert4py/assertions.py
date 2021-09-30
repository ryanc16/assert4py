from __future__ import annotations
import math
from typing import Callable, Iterable, Type


class Assertion:
	def __init__(self, actual):
		self.actual = actual
		self.comparator = None

	def whenComparedUsing(self, comparator):
		self.comparator = comparator
		return self

	def isEqualTo(self, expected, comparator=None):
		if comparator != None:
			assert comparator(self.actual, expected), f"Expected {self.actual} to equal {expected}"
		elif self.comparator != None:
			assert self.comparator(self.actual, expected), f"Expected {self.actual} to equal {expected}"
		else:
			assert self.actual == expected, f"Expected {self.actual} to equal {expected}"

	def isNotEqualto(self, expected):
		assert self.actual != expected, f"Expected {self.actual} not to equal {expected}"
	
	def isCloseTo(self, expected, tolerance):
		assert math.isclose(self.actual, expected, abs_tol=tolerance), f"Expected {self.actual} to be close to {expected} by {tolerance}"

	def isTrue(self):
		assert self.actual == True, f"Expected {self.actual} to be True"

	def isFalse(self):
		assert self.actual == False, f"Expected {self.actual} to be False"

	def isNone(self):
		assert self.actual == None, f"Expected {self.actual} to be None"

	def isNotNone(self):
		assert self.actual != None, f"Expected {self.actual} not to be None"

	def hasLengthOf(self, expected: int):
		assert len(self.actual) == expected, f"Expected iterable of length {len(self.actual)} to be of length {expected} in {str(self.actual)}"

	def isTypeOf(self, expected: Type):
		assert type(self.actual) == expected, f"Expected type {type(self.actual)} of {self.actual} to be of type {type(expected)}"

	def isInstanceOf(self, expected: Type):
		assert isinstance(self.actual, expected), f"Expected type {type(self.actual)} of {self.actual} to be an instance of {type(expected)}"
	
	def contains(self, expected: Iterable):
		for i in range(len(expected)):
			assert expected[i] in self.actual, f"Expected {[str(item) for item in self.actual]} to contain {str(expected[i])}"

	def each(self, assertion_fn: Callable[[Assertion, int], bool]):
		itr = None
		try:
				itr = iter(self.actual)
		except TypeError as te:
				print(self.actual, 'is not iterable')
		if itr is not None:
			count=0
			for element in itr:
				assertion_fn(assertThat(self.actual[count]), count)
				count+=1

def assertThat(actual):
	return Assertion(actual)
