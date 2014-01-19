class BaseReader:
    def read(self):
        pass


class FileReader(BaseReader):
    def __init__(self, file_path):
        self.file_path = file_path

    def read(self):
        with open(self.file_path) as source_file:
            for line in source_file:
                yield line.rstrip('\n')