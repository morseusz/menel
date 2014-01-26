import unittest
import imp
from menel.boilerplate import run
from menel.test import fake_scrappers


class TestRun(unittest.TestCase):
    def setUp(self):
        self.fake_scrappers = imp.reload(fake_scrappers)
        self.runner = run.Runner(self.fake_scrappers)

    def test_get_all_scrappers(self):
        got = self.runner.scrappers
        expected = [fake_scrappers.ScrapperA(), fake_scrappers.ScrapperB(),
                    fake_scrappers.ScrapperC(), fake_scrappers.ScrapperD()]
        self.assertEqual(got, expected)

    def test_independent_true(self):
        got = self.runner.get_independent()
        expected = [fake_scrappers.ScrapperA()]
        self.assertEqual(got, expected)

    def test_independent_false(self):
        self.runner.scrappers.pop(0)
        got = self.runner.get_independent()
        expected = []
        self.assertEqual(got, expected)

    def test_unblock_dependencies_check_requires(self):
        self.runner.unblock_dependencies(fake_scrappers.ScrapperA())
        for scrapper in self.runner.scrappers:
            self.assertNotIn(fake_scrappers.ScrapperA, scrapper.requires)

        self.runner.unblock_dependencies(fake_scrappers.ScrapperB())
        for scrapper in self.runner.scrappers:
            self.assertNotIn(fake_scrappers.ScrapperB, scrapper.requires)

    def test_unblock_dependencies_check_queue(self):
        q = self.runner.queue
        self.runner.scrappers.remove(fake_scrappers.ScrapperA())

        self.runner.unblock_dependencies(fake_scrappers.ScrapperA())
        ready = []
        for i in range(q.qsize()):
            ready.append(q.get())
        self.assertIn(fake_scrappers.ScrapperB(), ready)
        self.assertIn(fake_scrappers.ScrapperC(), ready)
        self.assertEqual(len(ready), 2)

        self.runner.unblock_dependencies(fake_scrappers.ScrapperB())
        ready = []
        for i in range(q.qsize()):
            ready.append(q.get())
        self.assertEqual(ready, [])

        self.runner.unblock_dependencies(fake_scrappers.ScrapperC())
        ready = []
        for i in range(q.qsize()):
            ready.append(q.get())
        self.assertIn(fake_scrappers.ScrapperD(), ready)
        self.assertEqual(len(ready), 1)

    def test_unblock_dependencies_no_dependency(self):
        self.runner.unblock_dependencies(fake_scrappers.ScrapperD())
        self.assertIn(fake_scrappers.ScrapperA(), self.runner.scrappers)
        self.assertIn(fake_scrappers.ScrapperB(), self.runner.scrappers)
        self.assertIn(fake_scrappers.ScrapperC(), self.runner.scrappers)
        self.assertIn(fake_scrappers.ScrapperD(), self.runner.scrappers)
        self.assertEqual(self.runner.queue.qsize(), 0)

    def test_unblock_dependencies_not_all(self):
        self.runner.unblock_dependencies(fake_scrappers.ScrapperB())
        self.assertIn(fake_scrappers.ScrapperD(), self.runner.scrappers)

    def test_unblock_dependencies_empty(self):
        self.runner.scrappers = []
        self.runner.unblock_dependencies(fake_scrappers.ScrapperB())

    def test_run(self):
        self.runner.run()
        lst = self.fake_scrappers.ScrapperA.lst
        self.assertEqual(lst.pop(), 'D')
        self.assertIn(lst.pop(), ('B', 'C'))
        self.assertIn(lst.pop(), ('B', 'C'))
        self.assertEqual(lst.pop(), 'A')
        self.assertEqual(len(lst), 0)
