-- Schema permissions.
GRANT USAGE ON SCHEMA errata TO esdoc_errata_db_user;

-- Table permissions.
GRANT INSERT, UPDATE, DELETE, SELECT ON ALL TABLES IN SCHEMA errata TO esdoc_errata_db_user;

-- Sequence permissions.
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA errata TO esdoc_errata_db_user;
