import glob
import importlib
import inspect
import os
import traceback
from dataclasses import dataclass
from datetime import datetime
from types import FunctionType
from functools import reduce

from assert4py.test_context import TestContext


@dataclass
class TestRunnerConfig:
	fileGlob: str
	verbosity: str = "INFO"
class TestRunner:
	scanned = {}
	tests = {}
	mocks = []
	def __init__(self, config: TestRunnerConfig):
		self.config = config
		self._scanTests()
		self.total = 0
		self.success = 0
		self.fail = 0
		self.skipped = 0

	def run(self):
		self.total = 0
		self.success = 0
		self.fail = 0
		self.skipped = 0
		percent = lambda x: "{:3.2f}".format(x*100)+"%"
		print("Starting tests")
		if self.config.verbosity != "SUMMARY":
			print("")
		focused_suites = {}
		focus_skipped = 0
		for suite in self.tests:
			suite_meta = TestRunner.tests[suite]
			if suite_meta['focus'] == True:
				print(f"!!! {suite.__name__} is a focused test suite")
				focused_suites[suite] = suite_meta
			elif any(list(map(lambda x: suite_meta['tests'][x]['focus'] == True, suite_meta['tests']))):
				print(f"!!! {suite.__name__} contains focused tests")
				focused_suites[suite] = suite_meta
			else:
				focus_skipped += len(suite_meta['tests'])
		if len(focused_suites.keys()) == 0:
			focused_suites = self.tests
		else:
			self.total += focus_skipped
			self.skipped += focus_skipped
		start = datetime.now()
		for suite in focused_suites:
			results = self.runSuite(suite)
			self.total += results[0]
			self.success += results[1]
			self.fail += results[2]
			self.skipped += results[3]
		stop = datetime.now()
		if self.config.verbosity != "VERBOSE":
			print("")
		print("Tests complete")
		print(f"{self.total} Total, {self.success} Pass, {self.fail} Fail, {self.skipped} Skipped. ({percent(self.success/((self.total-self.skipped)+1e-9))})")
		print(f"Took {stop-start}")
		return self.fail == 0

	def runSuite(self, suite):
		if self.config.verbosity != "SUMMARY":
			print(f"Starting: {suite.__name__}")
		suite_meta = TestRunner.tests[suite]
		tests = suite_meta['tests']
		total = 0
		success = 0
		fail = 0
		skipped = 0
		percent = lambda x: "{:3.2f}".format(x*100)+"%"
		focused_tests = {}
		focus_skipped = 0
		for test in tests:
			if tests[test]['focus'] == True:
				focused_tests[test] = tests[test]
			else:
				focus_skipped+=1
		if len(focused_tests.keys()) == 0:
			focused_tests = tests
		else:
			total += focus_skipped
			skipped = focus_skipped
		ctx = TestContext()
		self._beforeAll()
		if suite_meta['beforeAll'] is not None:
			suite_meta['beforeAll'](ctx)
		for test in focused_tests.keys():
			result = self.runOne(suite, test, ctx)
			if result == True:
				success+=1
			elif result == None:
				skipped+=1
			else:
				fail+=1
			total+=1
		if suite_meta['afterAll'] is not None:
			suite_meta['afterAll'](ctx)
		self._afterAll()
		if self.config.verbosity != "SUMMARY":
			print(f"{total} Total, {success} Pass, {fail} Fail, {skipped} Skipped. ({percent(success/((total-skipped)+1e-9))})")
		if self.config.verbosity == "VERBOSE":
			print("")
		return (total, success, fail, skipped)
	
	def runOne(self, suite, test: FunctionType, ctx: TestContext) -> bool:
		test_name = test.__name__
		if self.config.verbosity == "VERBOSE":
			print(f"  {test_name}", end="\r")
		if TestRunner.tests[suite]['tests'][test]['skip'] == True:
			if self.config.verbosity == "VERBOSE":
				print(f"  {test_name}", "SKIP")
			return None
		suite_meta = TestRunner.tests[suite]
		self._beforeEach()
		if suite_meta['beforeEach'] is not None:
				suite_meta['beforeEach'](ctx)
		result = None
		try:
			if 'ctx' in inspect.getargspec(test).args:
				pre_ctx = ctx.__dict__.copy()
				test(ctx)
				if ctx.__dict__.keys() != pre_ctx.keys():
					raise Exception('Do add or remove items from test context within a test method')
			else:
				test()
			if self.config.verbosity == "VERBOSE":
				print(f"  {test_name}", "PASS")
			result = True
		except Exception as reason:
			if self.config.verbosity == "VERBOSE":			
				print(f"  {test_name}", "FAIL")
			traceback.print_exception(reason, reason, reason.__traceback__)
			result = False
		if suite_meta['afterEach'] is not None:
			suite_meta['afterEach'](ctx)
		self._afterEach()
		return result

	def _beforeAll(self):
		pass
	def _beforeEach(self):
		pass
	def _afterEach(self):
		for mock in TestRunner.mocks:
			mock.restore()
		TestRunner.mocks = []
	def _afterAll(self):
		pass

	def _scanTests(self):
		if self.config.verbosity == "VERBOSE":
			print("Scanning for tests")
		files = []
		if self.config is not None:
			files = glob.glob(self.config.fileGlob, recursive=True)
		else:
			files = glob.glob("src/test/**/*_test.py", recursive=True)
		if self.config.verbosity == "VERBOSE":
			print(f"Found {len(files)} test files")
		for file_path in files:
			mod_path = file_path.replace(os.path.sep, '/').replace('/', '.').replace('.py', '')
			importlib.import_module(mod_path)
			# The annotations take care of the rest
		if self.config.verbosity == "VERBOSE":
			suites = len(TestRunner.scanned.keys())
			tests = reduce(
				lambda a,b: a+b,
				list(
					map(
						lambda suite: len(TestRunner.scanned[suite]['tests'].keys()),
						TestRunner.scanned.keys()
					)
				)
			)
			print(f"Loaded {suites} test suites with {tests} tests")
