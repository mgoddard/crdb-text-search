-- DDL for the two tables
DROP TABLE IF EXISTS docs;
CREATE TABLE docs
(
  idx_name TEXT
  , uri TEXT
  , content TEXT[]
  , n_words INT
  , PRIMARY KEY (idx_name, uri)
);

DROP TABLE IF EXISTS words;
CREATE TABLE words
(
  idx_name TEXT
  , uri TEXT
  , word TEXT
  , cnt INT
);

-- Secondary indexes
CREATE INDEX ON docs USING GIN(content);
CREATE INDEX ON words (idx_name, word) STORING (cnt);

-- Search: "follower reads"
WITH d AS (
  SELECT idx_name, uri, n_words
  FROM docs
  WHERE content @> '{crdb_docs, follow, read}'
), w AS (
  SELECT idx_name, uri, SUM(cnt) n
  FROM words
  WHERE idx_name = 'crdb_docs' AND word IN ('follow', 'read')
  GROUP BY (idx_name, uri)
)
SELECT w.uri, (100.0 * n/n_words)::NUMERIC(9, 3) score FROM w
JOIN d ON d.idx_name = w.idx_name AND d.uri = w.uri
ORDER BY score DESC
LIMIT 12;

-- Search: "cluster settings"
WITH d AS (
  SELECT idx_name, uri, n_words
  FROM docs
  WHERE content @> '{crdb_docs, cluster, set}'
), w AS (
  SELECT idx_name, uri, SUM(cnt) n
  FROM words
  WHERE idx_name = 'crdb_docs' AND word IN ('cluster', 'set')
  GROUP BY (idx_name, uri)
)
SELECT w.uri, (100.0 * n/n_words)::NUMERIC(9, 3) score FROM w
JOIN d ON d.idx_name = w.idx_name AND d.uri = w.uri
-- AS OF SYSTEM TIME experimental_follower_read_timestamp()
ORDER BY score DESC
LIMIT 12;

