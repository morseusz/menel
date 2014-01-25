import unittest
import os
from menel import readers


os.chdir(os.path.abspath(os.path.dirname(__file__)))


class ReaderTestCase(unittest.TestCase):
    def _read(self, reader):
        return [row for row in reader.read()]


class TestCsvReader(ReaderTestCase):
    excel_file = 'excel.csv'
    custom_file = 'custom.csv'

    def test_default(self):
        reader = readers.CsvReader(self.excel_file)
        self.assertEqual(reader.dialect, 'excel')

    def test_excel(self):
        reader = readers.CsvReader(self.excel_file, dialect='excel')
        got = self._read(reader)
        expected = [['a', ','],
                    ['a', ',', '"'],
                    ['a', ',', '"r']]
        self.assertEqual(got, expected)

    def test_custom(self):
        reader = readers.CsvReader(self.custom_file,
                                   delimiter=' ', quotechar='|')
        got = self._read(reader)
        expected = [[' f', '|'],
                    ['a', 'b']]
        self.assertEqual(got, expected)


class TestTextReader(ReaderTestCase):
    source_file = 'custom.csv'

    def test_read(self):
        reader = readers.TextReader(self.source_file)
        got = self._read(reader)
        expected = ['| f| ||||',
                    'a b',]
        self.assertEqual(got, expected)