from threading import Thread, Lock
from queue import Queue
import os
import scrappers
from menel.scrappers import BaseScrapper


"""
Executable python module which collects scrappers from scrappers.py and
runs them concurrently according to specified dependencies.
"""


class Runner:
    """Main class which collects scrappers and runs them."""
    def __init__(self, scrapper_module):
        """
        Arguments:
        scrapper_module - module containing scrapper classes

        Attributes:
        scrappers - list of collected scrappers
        scrappers_lock - lock guarding scrappers list
        queue - queue of scrappers ready to run
        """
        self.scrappers = []
        self.get_all_scrappers(scrapper_module)
        self.scrappers_lock = Lock()
        self.queue = Queue()

    def get_all_scrappers(self, scrapper_module):
        """Retrieves all classes subclassing BaseScrapper
        from self.scrapper_module"""
        attrs = [getattr(scrapper_module, x) for x in dir(scrapper_module)]
        for attr in attrs:
            try:
                if issubclass(attr, BaseScrapper):
                    self.scrappers.append(attr())
            except TypeError:
                pass

    def get_independent(self):
        """Returns all scrappers with no dependencies and removes them from
        scrappers list."""
        independent = []
        for scrapper in self.scrappers:
            if not scrapper.requires:
                independent.append(scrapper)

        for i in independent:
            self.scrappers.remove(i)

        return independent

    def unblock_dependencies(self, to_unblock):
        """Traverses the scrappers list in search of scrappers dependent
        on given scrapper. The given scrapper is then removed from requires
        list of all scrappers. Scrappers with empty requires list are pushed
        to self.queue.

        Arguments:
        to_unblock - scrapper which is supposed to be removed from requires
        lists
        """
        cls = type(to_unblock)
        with self.scrappers_lock:
            for scrapper in reversed(self.scrappers):
                if cls not in scrapper.requires:
                    continue
                scrapper.requires.remove(cls)
                if not scrapper.requires:
                    self.queue.put(scrapper)
                    self.scrappers.remove(scrapper)

    def run_and_unblock_dependencies(self, scrapper):
        """Runs the given scrapper and removes it from requires lists of
        other scrappers when the run is finished.

        Arguments:
        scrapper - scrapper to run
        """
        try:
            scrapper.scrape_all()
        finally:
            self.unblock_dependencies(scrapper)

    def run(self):
        """Runs all scrappers scrape() methods in correct order."""
        threads = []
        for i in self.get_independent():
            self.queue.put(i)

        while True:
            scrapper = self.queue.get(1)
            thread = Thread(target=self.run_and_unblock_dependencies(scrapper))
            thread.start()
            threads.append(thread)
            if not self.scrappers and not self.queue.qsize():
                break

        for thread in threads:
            thread.join()


if __name__ == '__main__':
    os.chdir(os.path.abspath(os.path.dirname(__file__)))
    Runner.run(scrappers)