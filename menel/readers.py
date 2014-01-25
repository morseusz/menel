import csv


class BaseReader:
    def read(self):
        pass


class FileReader(BaseReader):
    def __init__(self, file_path):
        self.file_path = file_path

    def _read_file(self, source_file):
        pass

    def read(self):
        with open(self.file_path) as source_file:
            yield from self._read_file(source_file)


class TextReader(FileReader):
    def _read_file(self, source_file):
        for line in source_file:
            yield line.rstrip('\n')


class CsvReader(FileReader):
    def __init__(self, file_path, dialect='excel', **kwargs):
        super().__init__(file_path)
        self.dialect = dialect
        self.kwargs = kwargs

    def _read_file(self, source_file):
        reader = csv.reader(source_file, dialect=self.dialect, **self.kwargs)
        yield from reader