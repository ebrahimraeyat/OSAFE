from pathlib import Path


class SafeReader():

    def __init__(self, file_path, mode='r') -> None:
        self.file_path = file_path
        self.__mode = mode
        self.__file_object = None
        self.tables_contents = None

    def __enter__(self):
        self.__file_object = open(self.file_path, self.__mode)
        return self.__file_object

    def __exit__(self, type, val, tb):
        self.__file_object.close()

    def get_tables_contents(self):
        with SafeReader(self.file_path) as reader:
            lines = reader.readlines()
            tables_contents = dict()
            n = len("TABLE:  ")
            contex = ''
            table_key = None
            for line in lines:
                if line.startswith("TABLE:"):
                    if table_key and contex:
                        tables_contents[table_key] = contex
                    contex = ''
                    table_key = line[n+1:-2]
                else:
                    contex += line
        self.tables_contents = tables_contents
        return tables_contents

    def write(self, filename):
        if self.tables_contents is None:
            self.get_tables_contents()
        with open(filename, 'w') as writer:
            for table_key, content in self.tables_contents.items():
                writer.write(f'TABLE:  "{table_key}"\n')
                writer.write(content)
            writer.write("\nEND TABLE DATA")
        return None


if __name__ == "__main__":

    safe = SafeReader(Path('F:\\alaki\\test_export16.f2k'))
    print(safe)
