import DatabaseHelpers
class DatabaseHandler:
    def __init__(self, databasePath):
        self.engine = DatabaseHelpers.createSQLiteEngine(databasePath)
