"""Read the currently connected workspace; never select or initialize another store."""


class WorkspaceInfoService:
    def __init__(self, reader):
        self.reader = reader

    def read(self):
        return self.reader.read()
