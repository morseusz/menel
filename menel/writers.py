from queue import Queue, Empty
from threading import Thread, Event


class BaseWriter:
    """Base class for writers."""
    def write(self):
        pass


class ConcurrentWriter(BaseWriter):
    """Base class for thread safe writers. Uses synchronized queue for passing
    data between producer threads and consumer (single thread implementing
    writing to storage)."""
    def __init__(self):
        self.queue = Queue()
        self.commit_thread = Thread(target=self._commit_from_queue)
        self.stop_writing = Event()

    def _commit_from_queue(self):
        """Pops the data from queue and writes it in a way specified in write()
        method until terminated by other thread. Setting self.stop_writing
        events terminates the loop."""
        while True:
            try:
                self.commit(self.queue.get(True, 1))
            except Empty:
                pass
            if self.stop_writing.is_set():
                break

    def commit(self, to_commit):
        """Abstract method implementing writing data to storage
        (file, db etc.).

        Arguments:
        to_commit - scrapped data to be written
        """
        pass

    def write(self, to_write):
        """Puts the data on top of the queue, from where it is fetched and
        writen by commit thread.

        Arguments:
        to_write - scrapped data to be written
        """
        self.queue.put(to_write)

    def __enter__(self):
        """Starts the commit thread, which pops the data from queue and writes
        it."""
        self.commit_thread.start()

    def __exit__(self, *args):
        """Tells the commit thread to terminate and waits until it does."""
        self.stop_writing.set()
        self.commit_thread.join()


class FileWriter(ConcurrentWriter):
    """Class implementing thread safe writing to a file."""
    def __init__(self, file_path):
        """Initializer method.

        Arguments:
        file_path - path to a file where results are going to be written
        """
        super().__init__()
        self.file_path = file_path
        self.file = None

    def __enter__(self):
        """Opens the file for writing."""
        super().__enter__()
        self.file = open(self.file_path, 'w')
        return self

    def __exit__(self, *args):
        """Closes the file."""
        super().__exit__()
        self.file.close()

    def commit(self, to_commit):
        """Writes the scrapped data as a line in the file.

        Arguments:
        to_commit - scrapped data
        """
        self.file.write(str(to_commit) + '\n')


class MultilineFileWriter(FileWriter):
    """Extended version of FileWriter which allows to write several lines at
    a time."""
    def write(self, to_write):
        """Puts every element from the collection of scraped data to queue.

        Arguments:
        to_write - collection of scrapped_data
        """
        for elem in to_write:
            self.queue.put(elem)