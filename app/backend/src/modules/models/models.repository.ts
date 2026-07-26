import { pool } from '../../db/pool';

export interface ModelVersionRow {
  id: string;
  model_name: string;
  version: string;
  status: string;
  artifact_url: string | null;
  trained_at: string | null;
  deployed_at: string | null;
  notes: string | null;
  created_at: string;
}

export async function listModelVersions(): Promise<ModelVersionRow[]> {
  const result = await pool.query(
    `SELECT
        id,
        model_name,
        version,
        status,
        artifact_url,
        trained_at,
        deployed_at,
        notes,
        created_at
     FROM model_versions
     ORDER BY created_at DESC, model_name ASC, version DESC`
  );

  return result.rows;
}

export async function getLatestDeployedModelVersion(): Promise<ModelVersionRow | null> {
  const result = await pool.query(
    `SELECT
        id,
        model_name,
        version,
        status,
        artifact_url,
        trained_at,
        deployed_at,
        notes,
        created_at
     FROM model_versions
     WHERE status = 'deployed'
     ORDER BY deployed_at DESC NULLS LAST, created_at DESC
     LIMIT 1`
  );

  return result.rows[0] ?? null;
}

export async function upsertDeployedModelVersion(input: {
  id: string;
  modelName: string;
  version: string;
  artifactUrl?: string | null;
  notes?: string | null;
}): Promise<ModelVersionRow> {
  const result = await pool.query(
    `INSERT INTO model_versions (
        id,
        model_name,
        version,
        status,
        artifact_url,
        trained_at,
        deployed_at,
        notes,
        created_at
     ) VALUES ($1, $2, $3, 'deployed', $4, NULL, NOW(), $5, NOW())
     ON CONFLICT (model_name, version)
     DO UPDATE SET
        status = 'deployed',
        deployed_at = COALESCE(model_versions.deployed_at, EXCLUDED.deployed_at),
        artifact_url = COALESCE(model_versions.artifact_url, EXCLUDED.artifact_url),
        notes = COALESCE(model_versions.notes, EXCLUDED.notes)
     RETURNING
        id,
        model_name,
        version,
        status,
        artifact_url,
        trained_at,
        deployed_at,
        notes,
        created_at`,
    [
      input.id,
      input.modelName,
      input.version,
      input.artifactUrl ?? null,
      input.notes ?? 'Auto-registered from ML inference service.'
    ]
  );

  return result.rows[0];
}

export async function createModelVersion(input: {
  id: string;
  modelName: string;
  version: string;
  status: 'training' | 'deployed' | 'archived';
  artifactUrl?: string | null;
  trainedAt?: string | null;
  deployedAt?: string | null;
  notes?: string | null;
}): Promise<ModelVersionRow> {
  const result = await pool.query(
    `INSERT INTO model_versions (
        id,
        model_name,
        version,
        status,
        artifact_url,
        trained_at,
        deployed_at,
        notes,
        created_at
     ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, NOW())
     RETURNING
        id,
        model_name,
        version,
        status,
        artifact_url,
        trained_at,
        deployed_at,
        notes,
        created_at`,
    [
      input.id,
      input.modelName,
      input.version,
      input.status,
      input.artifactUrl ?? null,
      input.trainedAt ?? null,
      input.deployedAt ?? null,
      input.notes ?? null
    ]
  );

  return result.rows[0];
}
