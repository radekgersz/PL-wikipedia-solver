import sqlite3

class DatabaseConnector:
    def __init__(self, databaseName):
        self.connection = sqlite3.connect(databaseName)
        self.cursor = self.connection.cursor()

    def close(self):
        self.connection.close()

    def getPageID(self, pageName):
        QUERY = f"SELECT * FROM pages WHERE pageName = '{pageName}'"
        self.cursor.execute(QUERY)