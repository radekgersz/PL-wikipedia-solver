"""
Replaces page IDs in the links file with their corresponding redirected IDs,
eliminates links containing non-existing pages, and replaces redirects with the
pages to which they redirect.

Output is written to stdout.
"""

import sys
import gzip

# Validate inputs
if len(sys.argv) < 5:
    print('[ERROR] Not enough arguments provided!')
    print('[INFO] Usage: {0} <pages_file> <redirects_file> <links_file>'.format(sys.argv[0]))
    sys.exit()

PAGES_FILE = sys.argv[1]
REDIRECTS_FILE = sys.argv[2]
LINKS_FILE = sys.argv[3]
LINKTARGET_FILE = sys.argv[4]

for f in [PAGES_FILE, REDIRECTS_FILE, LINKS_FILE]:
    if not f.endswith('.gz'):
        print(f'[ERROR] File {f} must be gzipped.')
        sys.exit()

# --- Load all valid pages ---
ALL_PAGE_IDS = set()
pageNameToID = {}
with gzip.open(PAGES_FILE, 'rt', encoding='utf-8') as f:
    for line in f:
        parts = line.rstrip('\n').split('\t')
        page_id,page_title = parts[0],parts[1]
        ALL_PAGE_IDS.add(page_id)
        pageNameToID[page_title] = ID

# --- Load redirects ---
REDIRECTS = {}
with gzip.open(REDIRECTS_FILE, 'rt', encoding='utf-8') as f:
    for line in f:
        parts = line.rstrip('\n').split('\t')
        src, tgt = parts[0], parts[1]
        REDIRECTS[src] = tgt

relationalIDToTitle ={}
with gzip.open(LINKTARGET_FILE, 'rt', encoding='utf-8') as f:
    for line in f:
        parts = line.rstrip('\n').split('\t')
        relational_ID, title = parts[0], parts[1]
        relationalIDToTitle[relational_ID] = title


# --- Process links file (source_id → target_id) ---
with gzip.open(LINKS_FILE, 'rt', encoding='utf-8') as f:
    for line in f:
        parts = line.rstrip('\n').split('\t')
        source_page_id, relational_page_id = parts[0], parts[1]
        page_title = relationalIDToTitle[relational_ID]
        if page_title is None:
            continue

        target_page_id = pageNameToID[page_title]
        if target_page_id is None:
            continue

        if source_page_id not in ALL_PAGE_IDS or target_page_id not in ALL_PAGE_IDS:
            continue

        # Apply redirects
        source_page_id = REDIRECTS.get(source_page_id, source_page_id)
        target_page_id = REDIRECTS.get(target_page_id, target_page_id)

        # Avoid self-links
        if source_page_id != target_page_id:
            print('\t'.join([source_page_id, target_page_id]))

