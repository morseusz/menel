from queue import Queue
from concurrent.futures import ThreadPoolExecutor as Pool


class BaseScrapper:
    reader = None
    writer = None

    def scrape_all(self):
        with self.writer as writer:
            for url in self.reader.read():
                writer.write(self.scrape(url))

    def scrape(self, url):
        pass


class ConcurrentScrapper(BaseScrapper):
    from settings import THREAD_NO

    def __init__(self):
        self.results = Queue(maxsize=self.THREAD_NO)

    def scrape_all(self):
        with Pool(max_workers=self.THREAD_NO) as pool, self.writer as writer:
            for result in pool.map(self.scrape, self.reader.read()):
                writer.write(result)