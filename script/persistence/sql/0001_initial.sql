-- TASK-DB-001: initial schema (6 tables: schema_migrations + 5 domain tables).
-- Spec: docs/db/00-database-overview.md, 90-schema-migrations-table.md, 01-05 *-table.md

CREATE TABLE IF NOT EXISTS schema_migrations (
    migration_id TEXT PRIMARY KEY,
    checksum TEXT NOT NULL,
    applied_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_schema_migrations_applied_at ON schema_migrations (applied_at);

CREATE TABLE IF NOT EXISTS projects (
    project_id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    domain TEXT NOT NULL,
    planning_stage TEXT NOT NULL DEFAULT 'registered'
        CHECK (planning_stage IN ('registered', 'curriculum_draft', 'review_pending', 'approved')),
    content_revision INTEGER NOT NULL DEFAULT 1,
    plan_file_path TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    archived_at TEXT
);
CREATE INDEX IF NOT EXISTS idx_projects_archived_at ON projects (archived_at);

CREATE TABLE IF NOT EXISTS sources (
    source_id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL REFERENCES projects (project_id),
    media_type TEXT NOT NULL CHECK (media_type IN ('text', 'pdf', 'image')),
    status TEXT NOT NULL DEFAULT 'registered'
        CHECK (status IN ('registered', 'processing', 'ready', 'review_required', 'failed')),
    original_file_path TEXT NOT NULL,
    content_hash TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_sources_project_id ON sources (project_id);

CREATE TABLE IF NOT EXISTS build_requests (
    build_request_id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL REFERENCES projects (project_id),
    output_formats_json TEXT NOT NULL,
    voice_profile_id TEXT,
    status TEXT NOT NULL DEFAULT 'draft'
        CHECK (status IN ('draft', 'queued', 'running', 'completed', 'failed', 'cancel_requested', 'cancelled')),
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    CHECK (
        json_valid(output_formats_json)
        AND (instr(output_formats_json, 'mp3') = 0 OR voice_profile_id IS NOT NULL)
    )
);
CREATE INDEX IF NOT EXISTS idx_build_requests_project_id ON build_requests (project_id);
CREATE INDEX IF NOT EXISTS idx_build_requests_status ON build_requests (status);

CREATE TABLE IF NOT EXISTS jobs (
    job_id TEXT PRIMARY KEY,
    build_request_id TEXT NOT NULL REFERENCES build_requests (build_request_id),
    job_type TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'queued'
        CHECK (status IN ('queued', 'running', 'succeeded', 'failed', 'cancel_requested', 'cancelled')),
    parent_job_id TEXT REFERENCES jobs (job_id),
    progress_current INTEGER,
    progress_total INTEGER,
    last_message TEXT,
    started_at TEXT,
    finished_at TEXT
);
CREATE INDEX IF NOT EXISTS idx_jobs_build_request_id ON jobs (build_request_id);
CREATE INDEX IF NOT EXISTS idx_jobs_status ON jobs (status);

CREATE TABLE IF NOT EXISTS artifacts (
    artifact_id TEXT PRIMARY KEY,
    job_id TEXT NOT NULL REFERENCES jobs (job_id),
    project_id TEXT NOT NULL REFERENCES projects (project_id),
    artifact_type TEXT NOT NULL CHECK (artifact_type IN ('mp3_chapter', 'text_verified_script')),
    file_path TEXT NOT NULL,
    version_number INTEGER NOT NULL DEFAULT 1 CHECK (version_number >= 1),
    content_hash TEXT NOT NULL,
    created_at TEXT NOT NULL,
    UNIQUE (project_id, artifact_type, version_number)
);
CREATE INDEX IF NOT EXISTS idx_artifacts_project_id ON artifacts (project_id);
CREATE INDEX IF NOT EXISTS idx_artifacts_artifact_type ON artifacts (artifact_type);
