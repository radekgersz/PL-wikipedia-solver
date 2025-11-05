import sqlite3
from collections import deque

SEP = "|"  # your DB uses pipe-separated lists

# ---------- DB helpers ----------

def _split_ids(s):
    if not s:
        return []
    return [int(x) for x in s.split(SEP) if x and x.isdigit()]

def get_outgoing(conn, page_id):
    cur = conn.cursor()
    cur.execute("SELECT outgoing_links FROM links WHERE id = ?", (page_id,))
    row = cur.fetchone()
    return _split_ids(row[0]) if row else []

def get_incoming(conn, page_id):
    cur = conn.cursor()
    cur.execute("SELECT incoming_links FROM links WHERE id = ?", (page_id,))
    row = cur.fetchone()
    return _split_ids(row[0]) if row else []

# (optional) resolve redirects for start/target if you want:
def resolve_redirect(conn, page_id):
    cur = conn.cursor()
    cur.execute("SELECT is_redirect FROM pages WHERE id = ?", (page_id,))
    row = cur.fetchone()
    if not row:
        return page_id
    if row[0] == 0:  # not a redirect
        return page_id
    cur.execute("SELECT target_id FROM redirects WHERE source_id = ?", (page_id,))
    r = cur.fetchone()
    return r[0] if r else page_id

# ---------- BiBFS ----------

def bidirectional_bfs(conn, start_id, target_id, resolve_redirs=True):
    if resolve_redirs:
        start_id = resolve_redirect(conn, start_id)
        target_id = resolve_redirect(conn, target_id)

    if start_id == target_id:
        return [start_id]

    # parents maps: node -> predecessor in its search tree
    parents_fwd = {start_id: None}
    parents_bwd = {target_id: None}

    q_fwd = deque([start_id])  # expands via OUTGOING
    q_bwd = deque([target_id]) # expands via INCOMING (reverse graph)

    while q_fwd and q_bwd:
        meet = _expand_frontier(conn, q_fwd, parents_fwd, parents_bwd, get_outgoing)
        if meet is not None:
            return _reconstruct(meet, parents_fwd, parents_bwd)

        meet = _expand_frontier(conn, q_bwd, parents_bwd, parents_fwd, get_incoming)
        if meet is not None:
            return _reconstruct(meet, parents_fwd, parents_bwd)

    return None

def _expand_frontier(conn, queue, this_parents, other_parents, neighbor_fn):
    if not queue:
        return None
    current = queue.popleft()
    for nb in neighbor_fn(conn, current):
        if nb not in this_parents:
            this_parents[nb] = current
            queue.append(nb)
            if nb in other_parents:
                return nb  # meeting node
    return None

def _reconstruct(meet, parents_fwd, parents_bwd):
    # start -> meet
    path = []
    n = meet
    while n is not None:
        path.append(n)
        n = parents_fwd[n]
    path.reverse()
    # meet -> target (follow backward parents)
    n = parents_bwd[meet]
    tail = []
    while n is not None:
        tail.append(n)
        n = parents_bwd[n]
    return path + tail

# ---------- Example run ----------

if __name__ == "__main__":
    db_path = "../finalDB.sqlite"  # <- set this
    start_page_id = 2964518            # <- set this
    target_page_id = 999              # <- set this

    conn = sqlite3.connect(db_path)
    path = bidirectional_bfs(conn, start_page_id, target_page_id, resolve_redirs=True)
    conn.close()

    if path:
        print("Shortest path (page IDs):")
        print(" -> ".join(map(str, path)))
    else:
        print("No path found.")
