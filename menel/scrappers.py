from queue import Queue
from concurrent.futures import ThreadPoolExecutor as Pool


"""Collection of scrapper classes which glue all the other framework components
together.
"""


class BaseScrapper:
    """Base class for other scrappers.

    Class variables:
    reader - reader object, implementing generator method read(), which
    provides input data for scrapping
    writer - writer object, implementing thread safe method write(), which
    allows to store scrapped data
    errors - writer object for storing errors
    requires - list of scrapper classes which are required to run before
    """

    reader = None
    writer = None
    errors = writer
    requires = []

    def scrape_all(self):
        """Takes all the data from the reader, processes it and passes to
        writer."""
        with self.writer as writer:
            for url in self.reader.read():
                self.write(self.scrape(url))

    def scrape(self, url):
        """Abstract method retrieving the data from url and processing it.

        Arguments:
        url - url to be scrapped
        """
        pass

    def write(self, result):
        """Writes the result to writer or error depending on success of
        scraping.

        Arguments:
        result - tuple containing boolean scraping result as first element and
        processed data or error message as second
        """
        status, data = result
        if status is True:
            self.writer.write(data)
        else:
            self.errors.write(data)


class ConcurrentScrapper(BaseScrapper):
    """Multithreaded scrapper."""
    from settings import THREAD_NO

    def __init__(self):
        self.results = Queue(maxsize=self.THREAD_NO)

    def scrape_all(self):
        """Takes all the data from the reader, processes it and passes to
        writer. Scrapping takes place concurrently in number of threads based
        on THREAD_NO value insettings.py."""
        with Pool(max_workers=self.THREAD_NO) as pool, self.writer as writer:
            for result in pool.map(self.scrape, self.reader.read()):
                self.write(result)