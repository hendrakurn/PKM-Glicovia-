import { pool } from '../../db/pool';

export interface PredictionResultRow {
  id: string;
  sensor_reading_id: string;
  model_version_id: string;
  glucose_estimate: string | number | null;
  clinical_category: string | null;
  confidence_score: string | number | null;
  inference_status: string;
  predicted_at: string | null;
  created_at: string;
  sensor_recorded_at?: string;
  model_name?: string;
  model_version?: string;
}

export interface PredictionTrendRow {
  bucket_start: string;
  prediction_count: string;
  glucose_estimate_avg: string | null;
  glucose_estimate_min: string | null;
  glucose_estimate_max: string | null;
}

export async function listPredictions(options: { limit: number; offset: number; sensorReadingId?: string; modelVersionId?: string }): Promise<PredictionResultRow[]> {
  const params: unknown[] = [];
  const where: string[] = [];

  if (options.sensorReadingId) {
    params.push(options.sensorReadingId);
    where.push(`pr.sensor_reading_id = $${params.length}`);
  }

  if (options.modelVersionId) {
    params.push(options.modelVersionId);
    where.push(`pr.model_version_id = $${params.length}`);
  }

  params.push(options.limit, options.offset);

  const result = await pool.query(
    `SELECT
        pr.id,
        pr.sensor_reading_id,
        pr.model_version_id,
        pr.glucose_estimate,
        pr.clinical_category,
        pr.confidence_score,
        pr.inference_status,
        pr.predicted_at,
        pr.created_at,
        sr.recorded_at AS sensor_recorded_at,
        mv.model_name,
        mv.version AS model_version
     FROM prediction_results pr
     JOIN sensor_readings sr ON sr.id = pr.sensor_reading_id
     JOIN model_versions mv ON mv.id = pr.model_version_id
     ${where.length ? `WHERE ${where.join(' AND ')}` : ''}
     ORDER BY COALESCE(pr.predicted_at, pr.created_at) DESC, pr.created_at DESC
     LIMIT $${params.length - 1}
     OFFSET $${params.length}`,
    params
  );

  return result.rows;
}

export async function listSubjectPredictions(options: {
  subjectId: string;
  limit: number;
  offset: number;
  deviceId?: string;
  sensorReadingId?: string;
  modelVersionId?: string;
}): Promise<PredictionResultRow[]> {
  const params: unknown[] = [options.subjectId];
  const where: string[] = ['sr.subject_id = $1'];

  if (options.deviceId) {
    params.push(options.deviceId);
    where.push(`sr.device_id = $${params.length}`);
  }

  if (options.sensorReadingId) {
    params.push(options.sensorReadingId);
    where.push(`pr.sensor_reading_id = $${params.length}`);
  }

  if (options.modelVersionId) {
    params.push(options.modelVersionId);
    where.push(`pr.model_version_id = $${params.length}`);
  }

  params.push(options.limit, options.offset);

  const result = await pool.query(
    `SELECT
        pr.id,
        pr.sensor_reading_id,
        pr.model_version_id,
        pr.glucose_estimate,
        pr.clinical_category,
        pr.confidence_score,
        pr.inference_status,
        pr.predicted_at,
        pr.created_at,
        sr.recorded_at AS sensor_recorded_at,
        mv.model_name,
        mv.version AS model_version
     FROM prediction_results pr
     JOIN sensor_readings sr ON sr.id = pr.sensor_reading_id
     JOIN model_versions mv ON mv.id = pr.model_version_id
     WHERE ${where.join(' AND ')}
     ORDER BY COALESCE(pr.predicted_at, pr.created_at) DESC, pr.created_at DESC
     LIMIT $${params.length - 1}
     OFFSET $${params.length}`,
    params
  );

  return result.rows;
}

export async function getLatestPrediction(): Promise<PredictionResultRow | null> {
  const rows = await listPredictions({ limit: 1, offset: 0 });
  return rows[0] ?? null;
}

export async function getLatestSubjectPrediction(subjectId: string, deviceId?: string): Promise<PredictionResultRow | null> {
  const rows = await listSubjectPredictions({
    subjectId,
    deviceId,
    limit: 1,
    offset: 0
  });
  return rows[0] ?? null;
}

export async function listSubjectPredictionTrends(options: {
  subjectId: string;
  deviceId?: string;
  from?: string;
  to?: string;
  bucket: 'day' | 'week';
  limit: number;
}): Promise<PredictionTrendRow[]> {
  const params: unknown[] = [options.subjectId];
  const where: string[] = [
    'sr.subject_id = $1',
    `pr.inference_status = 'success'`,
    'pr.glucose_estimate IS NOT NULL'
  ];

  if (options.deviceId) {
    params.push(options.deviceId);
    where.push(`sr.device_id = $${params.length}`);
  }

  if (options.from) {
    params.push(options.from);
    where.push(`sr.recorded_at >= $${params.length}`);
  }

  if (options.to) {
    params.push(options.to);
    where.push(`sr.recorded_at <= $${params.length}`);
  }

  params.push(options.limit);

  const bucketExpression = options.bucket === 'week'
    ? `date_trunc('week', sr.recorded_at)`
    : `date_trunc('day', sr.recorded_at)`;

  const result = await pool.query(
    `SELECT
        ${bucketExpression} AS bucket_start,
        COUNT(*)::text AS prediction_count,
        AVG(pr.glucose_estimate)::text AS glucose_estimate_avg,
        MIN(pr.glucose_estimate)::text AS glucose_estimate_min,
        MAX(pr.glucose_estimate)::text AS glucose_estimate_max
     FROM prediction_results pr
     JOIN sensor_readings sr ON sr.id = pr.sensor_reading_id
     WHERE ${where.join(' AND ')}
     GROUP BY 1
     ORDER BY 1 DESC
     LIMIT $${params.length}`,
    params
  );

  return result.rows;
}

export async function createPredictionResultIfAbsent(input: {
  id: string;
  sensorReadingId: string;
  modelVersionId: string;
  glucoseEstimate?: number | null;
  clinicalCategory?: string | null;
  confidenceScore?: number | null;
  inferenceStatus?: 'pending' | 'success' | 'failed';
  predictedAt?: string | null;
}) {
  const result = await pool.query(
    `INSERT INTO prediction_results (
        id,
        sensor_reading_id,
        model_version_id,
        glucose_estimate,
        clinical_category,
        confidence_score,
        inference_status,
        predicted_at,
        created_at
     ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, NOW())
     ON CONFLICT DO NOTHING
     RETURNING
        id,
        sensor_reading_id,
        model_version_id,
        glucose_estimate,
        clinical_category,
        confidence_score,
        inference_status,
        predicted_at,
        created_at`,
    [
      input.id,
      input.sensorReadingId,
      input.modelVersionId,
      input.glucoseEstimate ?? null,
      input.clinicalCategory ?? null,
      input.confidenceScore ?? null,
      input.inferenceStatus ?? 'pending',
      input.predictedAt ?? null
    ]
  );

  return result.rows[0] ?? null;
}

export async function getPredictionForReadingAndModel(sensorReadingId: string, modelVersionId: string): Promise<PredictionResultRow | null> {
  const result = await pool.query(
    `SELECT
        id,
        sensor_reading_id,
        model_version_id,
        glucose_estimate,
        clinical_category,
        confidence_score,
        inference_status,
        predicted_at,
        created_at
     FROM prediction_results
     WHERE sensor_reading_id = $1
       AND model_version_id = $2
     ORDER BY created_at DESC
     LIMIT 1`,
    [sensorReadingId, modelVersionId]
  );

  return result.rows[0] ?? null;
}

export async function savePredictionResult(input: {
  id: string;
  sensorReadingId: string;
  modelVersionId: string;
  glucoseEstimate?: number | null;
  clinicalCategory?: string | null;
  confidenceScore?: number | null;
  inferenceStatus: 'pending' | 'success' | 'failed';
  predictedAt?: string | null;
}): Promise<PredictionResultRow> {
  const existing = await getPredictionForReadingAndModel(input.sensorReadingId, input.modelVersionId);
  if (existing) {
    const result = await pool.query(
      `UPDATE prediction_results
       SET glucose_estimate = $1,
           clinical_category = $2,
           confidence_score = $3,
           inference_status = $4,
           predicted_at = $5
       WHERE id = $6
       RETURNING
          id,
          sensor_reading_id,
          model_version_id,
          glucose_estimate,
          clinical_category,
          confidence_score,
          inference_status,
          predicted_at,
          created_at`,
      [
        input.glucoseEstimate ?? null,
        input.clinicalCategory ?? null,
        input.confidenceScore ?? null,
        input.inferenceStatus,
        input.predictedAt ?? null,
        existing.id
      ]
    );
    return result.rows[0];
  }

  const result = await pool.query(
    `INSERT INTO prediction_results (
        id,
        sensor_reading_id,
        model_version_id,
        glucose_estimate,
        clinical_category,
        confidence_score,
        inference_status,
        predicted_at,
        created_at
     ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, NOW())
     RETURNING
        id,
        sensor_reading_id,
        model_version_id,
        glucose_estimate,
        clinical_category,
        confidence_score,
        inference_status,
        predicted_at,
        created_at`,
    [
      input.id,
      input.sensorReadingId,
      input.modelVersionId,
      input.glucoseEstimate ?? null,
      input.clinicalCategory ?? null,
      input.confidenceScore ?? null,
      input.inferenceStatus,
      input.predictedAt ?? null
    ]
  );

  return result.rows[0];
}
