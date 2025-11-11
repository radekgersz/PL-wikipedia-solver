from DatabaseHelpers import createSQLiteEngine
from sqlalchemy import text
class DatabaseHandler:
    def __init__(self, databasePath):
        self.engine = createSQLiteEngine(databasePath)

    def getIDFromName(self, name):
        query = text("SELECT id FROM pages WHERE title = :title LIMIT 1;")
        with self.engine.connect() as conn:
            result = conn.execute(query, {"title": name}).fetchone()
            if result:
                return result[0]
            else:
                return None


    def getNameFromID(self, id):
        query = text("SELECT title FROM pages WHERE id = :id LIMIT 1;")
        with self.engine.connect() as conn:
            result = conn.execute(query, {"id": id}).fetchone()
            if result:
                return result[0]
            else:
                return None


    def findShortestPath(self, startName, endName):
        pass

