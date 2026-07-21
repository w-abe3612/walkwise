-- TASK-BUILD-EXEC-001: voice_profiles table (DB正本化) + build_requests.voice_profile_id FK
-- + jobs失敗詳細列(error_code/error_stage/error_detail_json)。
-- Spec: docs/db/06-voice-profiles-table.md, 03-build-requests-table.md, 04-jobs-table.md
--
-- 事前条件: 呼び出し側(script/persistence/migrations.py の
-- check_orphaned_build_request_voice_profiles)が、本migration適用前に
-- build_requests.voice_profile_id の参照先不在行がないことを確認済みであること。

CREATE TABLE IF NOT EXISTS voice_profiles (
    voice_profile_id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL REFERENCES projects (project_id),
    name TEXT NOT NULL,
    engine TEXT NOT NULL,
    speaker_id TEXT NOT NULL,
    style_id TEXT,
    speed_scale REAL NOT NULL DEFAULT 1.0,
    pitch_scale REAL NOT NULL DEFAULT 0.0,
    intonation_scale REAL NOT NULL DEFAULT 1.0,
    volume_scale REAL NOT NULL DEFAULT 1.0,
    sentence_pause_ms INTEGER NOT NULL DEFAULT 250,
    paragraph_pause_ms INTEGER NOT NULL DEFAULT 600,
    section_pause_ms INTEGER NOT NULL DEFAULT 1000,
    chapter_pause_ms INTEGER NOT NULL DEFAULT 1500,
    settings_json TEXT NOT NULL DEFAULT '{}',
    status TEXT NOT NULL DEFAULT 'draft' CHECK (status IN ('draft', 'approved', 'archived')),
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    UNIQUE (project_id, name),
    CHECK (json_valid(settings_json)),
    CHECK (speed_scale > 0),
    CHECK (volume_scale > 0),
    CHECK (sentence_pause_ms >= 0 AND paragraph_pause_ms >= 0 AND section_pause_ms >= 0 AND chapter_pause_ms >= 0)
);
CREATE INDEX IF NOT EXISTS idx_voice_profiles_project_id ON voice_profiles (project_id);
CREATE INDEX IF NOT EXISTS idx_voice_profiles_status ON voice_profiles (status);

-- jobs: 安定エラーコード・失敗段階・詳細(秘密値・原稿全文・絶対pathを含まない)を追記可能にする。
ALTER TABLE jobs ADD COLUMN error_code TEXT;
ALTER TABLE jobs ADD COLUMN error_stage TEXT;
ALTER TABLE jobs ADD COLUMN error_detail_json TEXT;

-- build_requests.voice_profile_idへFKを追加する(SQLiteは既存列への制約追加を
-- ALTER TABLEで直接サポートしないため、既存データを保持するtable rebuildを行う)。
CREATE TABLE build_requests_new (
    build_request_id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL REFERENCES projects (project_id),
    output_formats_json TEXT NOT NULL,
    voice_profile_id TEXT REFERENCES voice_profiles (voice_profile_id),
    status TEXT NOT NULL DEFAULT 'draft'
        CHECK (status IN ('draft', 'queued', 'running', 'completed', 'failed', 'cancel_requested', 'cancelled')),
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    CHECK (
        json_valid(output_formats_json)
        AND (instr(output_formats_json, 'mp3') = 0 OR voice_profile_id IS NOT NULL)
    )
);

INSERT INTO build_requests_new (
    build_request_id, project_id, output_formats_json, voice_profile_id, status, created_at, updated_at
)
SELECT build_request_id, project_id, output_formats_json, voice_profile_id, status, created_at, updated_at
FROM build_requests;

DROP TABLE build_requests;
ALTER TABLE build_requests_new RENAME TO build_requests;

CREATE INDEX IF NOT EXISTS idx_build_requests_project_id ON build_requests (project_id);
CREATE INDEX IF NOT EXISTS idx_build_requests_status ON build_requests (status);
