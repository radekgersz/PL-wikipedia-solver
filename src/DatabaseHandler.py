from DatabaseHelpers import createSQLiteEngine
from sqlalchemy import text
from collections import deque

SEP = "|"  # pipe-separated list of IDs in DB

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


# ---------- internal helpers ----------

    def _split_ids(self, s):
        if not s:
            return []
        return [int(x) for x in s.split(SEP) if x and x.isdigit()]

    def _get_outgoing(self, conn, page_id):
        row = conn.execute(
            text("SELECT outgoing_links FROM links WHERE id = :id"),
            {"id": page_id}
        ).fetchone()
        return self._split_ids(row[0]) if row else []

    def _get_incoming(self, conn, page_id):
        row = conn.execute(
            text("SELECT incoming_links FROM links WHERE id = :id"),
            {"id": page_id}
        ).fetchone()
        return self._split_ids(row[0]) if row else []

    # ---------- bidirectional BFS ----------

    def findShortestPath(self, startName, endName):
        start_id = self.getIDFromName(startName)
        end_id = self.getIDFromName(endName)
        if start_id is None or end_id is None:
            return None

        if start_id == end_id:
            return [start_id]

        with self.engine.connect() as conn:
            parents_fwd = {start_id: None}
            parents_bwd = {end_id: None}
            q_fwd = deque([start_id])
            q_bwd = deque([end_id])

            while q_fwd and q_bwd:
                meet = self._expand_frontier(conn, q_fwd, parents_fwd, parents_bwd, self._get_outgoing)
                if meet is not None:
                    return self._reconstruct(meet, parents_fwd, parents_bwd)

                meet = self._expand_frontier(conn, q_bwd, parents_bwd, parents_fwd, self._get_incoming)
                if meet is not None:
                    return self._reconstruct(meet, parents_fwd, parents_bwd)

        return None

    def _expand_frontier(self, conn, queue, this_parents, other_parents, neighbor_fn):
        if not queue:
            return None
        current = queue.popleft()
        for nb in neighbor_fn(conn, current):
            if nb not in this_parents:
                this_parents[nb] = current
                queue.append(nb)
                if nb in other_parents:
                    return nb
        return None

    def _reconstruct(self, meet, parents_fwd, parents_bwd):
        path = []
        n = meet
        while n is not None:
            path.append(n)
            n = parents_fwd[n]
        path.reverse()

        n = parents_bwd[meet]
        tail = []
        while n is not None:
            tail.append(n)
            n = parents_bwd[n]
        return path + tail

    def convertIDsToNames(self, id_list):
        """Convert a list of page IDs into a list of corresponding page titles."""
        if not id_list:
            return []

        query = text(
            f"SELECT id, title FROM pages WHERE id IN ({','.join([':id'+str(i) for i in range(len(id_list))])})"
        )
        params = {f"id{i}": id_ for i, id_ in enumerate(id_list)}

        with self.engine.connect() as conn:
            rows = conn.execute(query, params).fetchall()

        id_to_title = {row[0]: row[1] for row in rows}
        return [id_to_title.get(i, f"[missing:{i}]") for i in id_list]
