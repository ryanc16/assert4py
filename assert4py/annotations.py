import inspect
from types import FunctionType

from assert4py.test_runner import TestRunner


def initializeTestModule(module: str):
	TestRunner.scanned[module] = {
		'beforeAll': None,
		'beforeEach': None,
		'afterEach': None,
		'afterAll': None,
		'tests': {},
		'focus': False
	}

def test(methodOrClass: FunctionType):
	"""
	Mark a test suite to be included or a function as a test to be ran in the test suite
	"""
	if methodOrClass == None:
		return
	name = methodOrClass.__module__
	if inspect.isclass(methodOrClass):
		clazz = methodOrClass
		TestRunner.tests[clazz] = TestRunner.scanned[name]
	else:
		method = methodOrClass
		if name not in TestRunner.scanned:
			initializeTestModule(name)
		if method not in TestRunner.scanned[name]['tests']:
			TestRunner.scanned[name]['tests'][method] = {'skip': False, 'focus': False}
	return methodOrClass

def skip(methodOrClass: FunctionType):
	"""
	Mark a test suite to be skipped or a function as a test that should be skipped in the test suite 
	"""
	if methodOrClass == None:
		return
	name = methodOrClass.__module__
	if inspect.isclass(methodOrClass):
		clazz = methodOrClass
		for test in TestRunner.scanned[name]['tests']:
			TestRunner.scanned[name]['tests'][test]['skip'] = True
		TestRunner.tests[clazz] = TestRunner.scanned[name]
	else:
		method = methodOrClass
		if name not in TestRunner.scanned:
			initializeTestModule(name)
		if method not in TestRunner.scanned[name]['tests']:
			TestRunner.scanned[name]['tests'][method] = {'skip': True, 'focus': False}
		else:
			TestRunner.scanned[name]['tests'][method]['skip'] = True
	return methodOrClass

def focus(methodOrClass: FunctionType):
	"""
	Mark a test suite or a function as a test to be exclusively ran, while ignoring all other tests.
	If more than one usage of focus is found, all of the focused items will be ran.
	"""
	if methodOrClass == None:
		return
	name = methodOrClass.__module__
	if inspect.isclass(methodOrClass):
		clazz = methodOrClass
		TestRunner.scanned[name]['focus'] = True
		TestRunner.tests[clazz] = TestRunner.scanned[name]
	else:
		method = methodOrClass
		if name not in TestRunner.scanned:
			initializeTestModule(name)
		if method not in TestRunner.scanned[name]['tests']:
			TestRunner.scanned[name]['tests'][method] = {'skip': False, 'focus': True}
		else:
			TestRunner.scanned[name]['tests'][method]['focus'] = True
	return methodOrClass

def beforeAll(method: FunctionType):
	"""
	Mark a function in a test suite to be ran first before any tests are ran
	"""
	if method == None:
		return
	moduleName = method.__module__
	if moduleName not in TestRunner.scanned:
		initializeTestModule(moduleName)
	TestRunner.scanned[moduleName]['beforeAll'] = method

def beforeEach(method: FunctionType):
	"""
	Mark a function in a test suite to be ran before each test is ran
	"""
	if method == None:
		return
	moduleName = method.__module__
	if moduleName not in TestRunner.scanned:
		initializeTestModule(moduleName)
	TestRunner.scanned[moduleName]['beforeEach'] = method

def afterEach(method: FunctionType):
	"""
	Mark a function in a test suite to be ran after each test has ran
	"""
	if method == None:
		return
	moduleName = method.__module__
	if moduleName not in TestRunner.scanned:
		initializeTestModule(moduleName)
	TestRunner.scanned[moduleName]['afterEach'] = method

def afterAll(method: FunctionType):
	"""
	Mark a function in a test suite to be ran last after all tests have ran
	"""
	if method == None:
		return
	moduleName = method.__module__
	if moduleName not in TestRunner.scanned:
		initializeTestModule(moduleName)
	TestRunner.scanned[moduleName]['afterAll'] = method