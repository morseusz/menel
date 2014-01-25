from threading import Thread, Lock
from queue import Queue
from scrappers import *
from menel.scrappers import BaseScrapper


class Runner:
    def __init__(self):
        self.scrappers = []
        self.get_all_scrappers()
        self.scrappers_lock = Lock()
        self.queue = Queue()

    def get_all_scrappers(self):
        globs = globals()
        for g in globs:
            cls = globs[g]
            try:
                if issubclass(cls, BaseScrapper):
                    self.scrappers.append(cls())
            except TypeError:
                pass

    def get_independent(self):
        independent = []
        for scrapper in self.scrappers:
            if not scrapper.requires:
                independent.append(scrapper)

        for i in independent:
            self.scrappers.remove(i)

        return independent

    def unblock_dependencies(self, to_unblock):
        cls = type(to_unblock)
        with self.scrappers_lock:
            for scrapper in self.scrappers:
                if cls not in scrapper.requires:
                    continue
                scrapper.requires.remove(cls)
                if not scrapper.requires:
                    self.queue.put(scrapper)
                    self.scrappers.remove(scrapper)

    def run_and_unblock_dependencies(self, scrapper):
        try:
            scrapper.scrape_all()
        finally:
            self.unblock_dependencies(scrapper)

    def run(self):
        threads = []
        for i in self.get_independent():
            self.queue.put(i)

        while True:
            scrapper = self.queue.get(1)
            thread = Thread(target=self.run_and_unblock_dependencies(scrapper))
            thread.start()
            threads.append(thread)
            if not self.scrappers:
                break

        for thread in threads:
            thread.join()


if __name__ == '__main__':
    Runner.run()