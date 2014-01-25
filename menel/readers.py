import csv


"""Collection of Reader classes used to feed scrappers with data.

   The Reader class has to implement read() generator method. All setup
   (establishing db connection, opening a file) and cleanup (closing a
   connection, closing a file) is implemented by the reader class.
   Results yielded by read() method will be used in multiple threads, but
   the method is called synchronously and doesn't have to be thread safe.
"""


class BaseReader:
    """Base class for readers."""
    def read(self):
        """Method called by scrappers to obtain input data (most commonly
        website urls).
        """
        pass


class FileReader(BaseReader):
    """Base class for reader classes accessing files on disk."""
    def __init__(self, file_path):
        """Class initializer.

        Arguments:
        file_path - path to source file (absolute or relative to
        <project>/data
        """
        self.file_path = file_path

    def _read_file(self, source_file):
        """Abstract generator method reading from file object. Logic
        for dealing with specific file types goes here.

        Arguments:
        source_file - file object opened for reading
        """
        pass

    def read(self):
        """Safely opens the source file and yields input data to scrappers."""
        with open(self.file_path) as source_file:
            yield from self._read_file(source_file)


class TextReader(FileReader):
    """Reader class for reading unstructured text files."""
    def _read_file(self, source_file):
        """Yields a line without the trailing newline character.

        Arguments:
        source_file - file object opened for reading
        """
        for line in source_file:
            yield line.rstrip('\n')


class CsvReader(FileReader):
    """Reader class for csv files."""
    def __init__(self, file_path, dialect='excel', **kwargs):
        """Object initializer.

        Arguments:
        file_path - source file path passed to superclass initializer

        Keyword arguments:
        dialect - csv dialect (delimiter + quote char) of source file,
        available by default: excel, excel-tab, unix
        delimiter - character used as cell delimiter in source file
        quotechar - character used to escape special characters (delimiter and
        quotechar) inside cells
        """
        super().__init__(file_path)
        self.dialect = dialect
        self.kwargs = kwargs

    def _read_file(self, source_file):
        """Yields a list of cells for each line in the source csv file.

        Arguments:
        source_file - file object opened for reading
        """
        reader = csv.reader(source_file, dialect=self.dialect, **self.kwargs)
        yield from reader