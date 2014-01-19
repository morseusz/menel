from queue import Queue, Empty
from threading import Thread, Event


class BaseWriter:
    def write(self):
        pass


class ConcurrentWriter(BaseWriter):
    def __init__(self):
        self.queue = Queue()
        self.commit_thread = Thread(target=self._commit_from_queue)
        self.stop_writing = Event()

    def _commit_from_queue(self):
        while True:
            try:
                self.commit(self.queue.get(True, 1))
            except Empty:
                pass
            if self.stop_writing.is_set():
                break

    def commit(self, to_commit):
        pass

    def write(self, to_write):
        self.queue.put(to_write)

    def __enter__(self):
        self.commit_thread.start()

    def __exit__(self, *args):
        self.stop_writing.set()
        self.commit_thread.join()


class FileWriter(ConcurrentWriter):
    def __init__(self, file_path):
        super().__init__()
        self.file_path = file_path
        self.file = None

    def __enter__(self):
        super().__enter__()
        self.file = open(self.file_path, 'w')
        return self

    def __exit__(self, *args):
        super().__exit__()
        self.file.close()

    def commit(self, to_commit):
        self.file.write(to_commit + '\n')


class MultilineFileWriter(FileWriter):
    def write(self, to_write):
        for elem in to_write:
            self.queue.put(elem)