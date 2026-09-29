-- AI visibility dashboard — reference schema (PostgreSQL)
--
-- Generalised from a running implementation. Table names are unprefixed here;
-- prefix them in your own build (mine uses a short app prefix on every table).
--
-- Design notes live in README.md. The short version:
--   * store answers, never only scores
--   * one snapshot per run; ranges pool snapshots, rows are never mutated
--   * grading output in JSONB; promote to a column only to filter/index
--   * claims get a stable fingerprint so the same error joins across days

-- ---------------------------------------------------------------- snapshots
-- One pull+grade run. `progress` is a free-form JSONB the worker updates as it
-- goes, so a long run is observable from the UI while it's still running.
CREATE TABLE IF NOT EXISTS snapshots (
  id           SERIAL PRIMARY KEY,
  started_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
  finished_at  TIMESTAMPTZ,
  status       TEXT NOT NULL DEFAULT 'running',   -- running | ok | error
  progress     JSONB NOT NULL DEFAULT '{}'::jsonb,
  error        TEXT
);

-- ------------------------------------------------------------------ answers
-- The core table: one AI answer to one prompt on one surface in one run.
CREATE TABLE IF NOT EXISTS answers (
  id                 BIGSERIAL PRIMARY KEY,
  snapshot_id        INT NOT NULL REFERENCES snapshots(id) ON DELETE CASCADE,

  question           TEXT NOT NULL,     -- the prompt, verbatim
  model              TEXT NOT NULL,     -- the AI surface (chatgpt, gemini, ...)
  tag_id             TEXT,              -- prompt tag from the source
  rq                 TEXT,              -- derived from tag: research question
  subgroup           TEXT,              -- derived from tag: sub-niche

  response           TEXT,              -- full answer text
  response_md        TEXT,              -- answer text WITH inline citation links
  sitelinks          JSONB NOT NULL DEFAULT '[]'::jsonb,  -- [{url, title}]
  answer_updated_at  TEXT,              -- source's own "answer as of" stamp
  search_volume      INT,               -- demand for this prompt

  -- sha1(question|model|response). Unchanged answer => reuse its grading.
  answer_hash        TEXT,

  eval               JSONB,             -- grading output (see below)
  facts              JSONB,             -- per-answer fact-check output (optional)

  -- Promoted from eval because question 4 filters on them constantly.
  tool_recommended   BOOLEAN,
  tool_names         JSONB,
  tool_eval_version  SMALLINT           -- which definition graded this row
);
CREATE INDEX IF NOT EXISTS answers_snap     ON answers(snapshot_id);
CREATE INDEX IF NOT EXISTS answers_rq       ON answers(rq);
CREATE INDEX IF NOT EXISTS answers_model    ON answers(model);
CREATE INDEX IF NOT EXISTS answers_hash     ON answers(answer_hash);

-- eval JSONB shape:
-- {
--   "mentioned": bool,
--   "position": int | null,        -- 1-based among brands, by first appearance
--   "total_brands": int,
--   "brands": [str],               -- in order of first appearance
--   "sentiment": "positive"|"neutral"|"mixed"|"negative"|null,
--   "verdict_winner": str | null,  -- null when the answer names no winner
--   "negative_themes": [str],
--   "negative_quotes": [str],      -- verbatim, substring-verified
--   "tool_recommended": bool,
--   "tool_names": [str]
-- }

-- ------------------------------------------------------------------- extras
-- Expensive or irreproducible computed blobs, one per (snapshot, kind).
--   kind='board'         -> the fully computed board (makes trends cheap)
--   kind='crawl_health'  -> operational pull; its trailing window cannot be
--   kind='freshness'        reconstructed after the fact, so it MUST be stored
CREATE TABLE IF NOT EXISTS extras (
  snapshot_id  INT NOT NULL REFERENCES snapshots(id) ON DELETE CASCADE,
  kind         TEXT NOT NULL,
  data         JSONB NOT NULL,
  PRIMARY KEY (snapshot_id, kind)
);

-- --------------------------------------------------------------- page_dates
-- Per-URL facts accumulated over time: dates (question 10), citation counts,
-- brand data (question 5/11), bot data (question 9). Keyed by URL, not by
-- snapshot: these are properties of the page, refreshed with a checked_at.
CREATE TABLE IF NOT EXISTS page_dates (
  url                 TEXT PRIMARY KEY,

  -- dates, in the priority order described in 01-questions/10-*.md
  visible_updated     DATE,          -- 1st choice: reader-visible "Updated:"
  jsonld_modified     DATE,          -- 2nd: machine-set, any touch
  jsonld_published    DATE,
  provider_publish_ts BIGINT,        -- 3rd: the data source's own timestamp
  page_fetched_at     TIMESTAMPTZ,

  -- page metrics
  dr                  REAL,
  page_traffic        REAL,

  -- citation counts from the provider's index, with the date they apply to.
  -- Separate columns because "citations across all surfaces" and "citations
  -- shown in the UI for one date" are different numbers and get compared.
  index_citations     INT,
  ui_citations        INT,
  ui_citations_date   DATE,
  ui_checked_at       TIMESTAMPTZ,

  -- Brands the provider says this page mentions. THREE-STATE, and the
  -- distinction is load-bearing:
  --   ['a','b']  -> brands found
  --   []         -> looked, found none
  --   NULL       -> NO DATA (never read this as "no mention")
  mentioned_brands    JSONB,
  brands_checked_at   TIMESTAMPTZ,

  -- AI bot activity on this URL
  bot_requests        INT,
  bot_top_name        TEXT,
  bot_window_end      DATE,
  bot_checked_at      TIMESTAMPTZ,

  found               BOOLEAN NOT NULL DEFAULT true,
  checked_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- -------------------------------------------------------------- page_content
-- Fetched page text, so a claim can be verified against what a page actually
-- says ("is this page the SOURCE of the error, or does it refute it?").
CREATE TABLE IF NOT EXISTS page_content (
  url         TEXT PRIMARY KEY,
  status      TEXT,
  http_code   INT,
  title       TEXT,
  body_text   TEXT,
  chars       INT,
  crawled_at  TIMESTAMPTZ,
  first_seen  TIMESTAMPTZ NOT NULL DEFAULT now(),
  fetched_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ------------------------------------------------------------------- claims
-- One checkable claim extracted from one answer, verdicted against the fact
-- sheet. `fingerprint` is what makes the same error joinable across days.
CREATE TABLE IF NOT EXISTS claims (
  id                 BIGSERIAL PRIMARY KEY,
  snapshot_id        INT NOT NULL REFERENCES snapshots(id) ON DELETE CASCADE,
  answer_id          BIGINT REFERENCES answers(id) ON DELETE CASCADE,

  fingerprint        TEXT NOT NULL,   -- normalise(claim) + sorted(fact_ids)
  claim              TEXT NOT NULL,
  verdict            TEXT,            -- consistent | contradicted | unverifiable
  severity           TEXT,            -- hard | soft
  fact_ids           JSONB NOT NULL DEFAULT '[]'::jsonb,
  note               TEXT,

  -- denormalised for query convenience
  question           TEXT,
  model              TEXT,
  rq                 TEXT,
  provoked           BOOLEAN,         -- asked about pricing vs volunteered

  factsheet_version  TEXT NOT NULL,   -- which sheet version judged this
  created_at         TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS claims_snap    ON claims(snapshot_id);
CREATE INDEX IF NOT EXISTS claims_fp      ON claims(fingerprint);
CREATE INDEX IF NOT EXISTS claims_verdict ON claims(verdict);

-- -------------------------------------------------------------- claim_cache
-- A claim already judged against this sheet version is never re-billed.
-- This is most of the LLM cost control on the fact-fidelity card.
CREATE TABLE IF NOT EXISTS claim_cache (
  fingerprint        TEXT NOT NULL,
  factsheet_version  TEXT NOT NULL,
  claim              TEXT NOT NULL,
  verdict            TEXT,
  severity           TEXT,
  fact_ids           JSONB NOT NULL DEFAULT '[]'::jsonb,
  note               TEXT,
  created_at         TIMESTAMPTZ NOT NULL DEFAULT now(),
  PRIMARY KEY (fingerprint, factsheet_version)
);

-- ------------------------------------------------------------ error_history
-- Lifecycle of a distinct error. Turns "today's errors" into "this error is
-- three weeks old and appearing on more surfaces".
CREATE TABLE IF NOT EXISTS error_history (
  fingerprint     TEXT PRIMARY KEY,
  claim           TEXT NOT NULL,
  severity        TEXT,
  first_seen      TIMESTAMPTZ NOT NULL,
  last_seen       TIMESTAMPTZ NOT NULL,
  first_snapshot  INT,
  last_snapshot   INT,
  occurrences     INT NOT NULL DEFAULT 1,
  surfaces        JSONB NOT NULL DEFAULT '[]'::jsonb,
  status          TEXT                      -- new | persisting | spreading | resolved
);

-- -------------------------------------------------------------------- facts
-- The fact sheet, under human review. The grader only ever sees status='approved'.
CREATE TABLE IF NOT EXISTS facts (
  id             BIGSERIAL PRIMARY KEY,
  fact_key       TEXT NOT NULL,
  fact           TEXT NOT NULL,
  aspect         TEXT,                       -- pricing | limits | features | ...
  source_quote   TEXT,                       -- substring-verified against source
  source_url     TEXT,
  authoritative  BOOLEAN NOT NULL DEFAULT false,  -- parsed table > prose
  conflict_note  TEXT,                       -- when two sources disagree
  status         TEXT NOT NULL DEFAULT 'pending',  -- pending | approved | rejected
  change_kind    TEXT,                       -- new | changed | unchanged
  prev_fact      TEXT,
  decided_by     TEXT,
  decided_at     TIMESTAMPTZ,
  created_at     TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE UNIQUE INDEX IF NOT EXISTS facts_key    ON facts(fact_key);
CREATE INDEX        IF NOT EXISTS facts_status ON facts(status);

-- ------------------------------------------------------------ verifications
-- "Does this cited page actually state the wrong thing?" — turns a SUSPECT
-- (page cited in an answer containing an error) into a CAUSE.
CREATE TABLE IF NOT EXISTS verifications (
  id           BIGSERIAL PRIMARY KEY,
  fingerprint  TEXT NOT NULL,
  url          TEXT NOT NULL,
  claim        TEXT,
  verdict      TEXT,        -- states | contradicts | silent | unclear
  evidence     TEXT,        -- verbatim quote from the page
  note         TEXT,
  snapshot_id  INT,
  crawled_at   TIMESTAMPTZ,
  created_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE UNIQUE INDEX IF NOT EXISTS verif_pair    ON verifications(fingerprint, url);
CREATE INDEX        IF NOT EXISTS verif_verdict ON verifications(verdict);

-- --------------------------------------------------------------------- meta
-- Small key/value state: cached tracked-page lists, ingest cursors, the
-- current fact sheet version, etc.
CREATE TABLE IF NOT EXISTS meta (
  key         TEXT PRIMARY KEY,
  value       TEXT,
  updated_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ------------------------------------------------------------------ queries
-- Two patterns worth copying.
--
-- 1. A date range is a LIST of snapshots, pooled — never a BETWEEN on one
--    table. Pick one snapshot per day (the last successful one):
--
--   SELECT DISTINCT ON (date_trunc('day', finished_at))
--          id, finished_at
--     FROM snapshots
--    WHERE status = 'ok' AND finished_at::date BETWEEN $1 AND $2
--    ORDER BY date_trunc('day', finished_at), finished_at DESC;
--
-- 2. Every answer-derived metric takes (snapshot_ids, surface) and computes
--    over the pool. Same code path for one day and for thirty:
--
--   SELECT * FROM answers
--    WHERE snapshot_id = ANY($1)
--      AND ($2 IS NULL OR model = $2);
