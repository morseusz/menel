import unittest
import copy
from menel.boilerplate import run

class TestRun(unittest.TestCase):
    def test_get_all_scrappers(self):
        print(dir(run))
        get_all_scrappers = copy.deepcopy(run.get_all_scrappers)