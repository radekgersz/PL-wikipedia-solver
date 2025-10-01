-- Drop old intermediate tables
DROP TABLE IF EXISTS redirect_map;
DROP TABLE IF EXISTS pl_resolved_src;
DROP TABLE IF EXISTS pl_resolved;
DROP TABLE IF EXISTS edges;
DROP TABLE IF EXISTS articles;

-- Step 1: build redirect map (redirect_id -> target_id)
CREATE TABLE redirect_map AS
SELECT r.rd_from AS redirect_id,
       p.page_id AS target_id
FROM redirect r
JOIN page p
  ON r.rd_namespace = p.page_namespace
 AND r.rd_title = p.page_title;

-- Step 2: resolve redirect sources
CREATE TABLE pl_resolved_src AS
SELECT COALESCE(rm.target_id, pl.pl_from) AS src_id,
       pl.pl_target_id AS dst_id
FROM pagelinks pl
LEFT JOIN redirect_map rm
  ON pl.pl_from = rm.redirect_id;

-- Step 3: resolve redirect targets
CREATE TABLE pl_resolved AS
SELECT src_id,
       COALESCE(rm.target_id, pl.dst_id) AS dst_id
FROM pl_resolved_src pl
LEFT JOIN redirect_map rm
  ON pl.dst_id = rm.redirect_id;

-- Step 4: keep only namespace=0 (articles)
CREATE TABLE edges AS
SELECT DISTINCT src_id, dst_id
FROM pl_resolved
JOIN page src ON src.page_id = pl_resolved.src_id
JOIN page dst ON dst.page_id = pl_resolved.dst_id
WHERE src.page_namespace = 0
  AND dst.page_namespace = 0;

-- Step 5: keep article lookup
CREATE TABLE articles AS
SELECT page_id, page_title
FROM page
WHERE page_namespace = 0;
