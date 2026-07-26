import { pool } from '../../db/pool';

export interface SubjectDeviceRow {
  device_assignment_id: string;
  device_id: string;
  device_code: string;
  device_name: string | null;
  mqtt_topic: string;
  device_status: string;
  subject_id: string;
  subject_code: string;
  subject_name: string | null;
  assigned_at: string;
  unassigned_at: string | null;
}

export interface SensorReadingRow {
  id: string;
  device_id: string;
  subject_id: string | null;
  device_assignment_id: string | null;
  recorded_at: string;
  received_at: string;
  ph: string | number | null;
  fructosamine: string | number | null;
  salivary_glucose: string | number | null;
  raw_payload: unknown;
  quality_flag: string;
  created_at: string;
}

export interface SensorReadingInsert {
  id: string;
  deviceId: string;
  subjectId: string | null;
  deviceAssignmentId: string | null;
  recordedAt: string;
  receivedAt: string;
  ph: number | null;
  fructosamine: number | null;
  salivaryGlucose: number | null;
  rawPayload: unknown;
  qualityFlag: 'valid' | 'suspect' | 'incomplete';
}

export interface DeviceResolutionRow {
  id: string;
  device_code: string;
  mqtt_topic: string;
  name: string | null;
  status: string;
}

export interface ActiveAssignmentRow {
  id: string;
  device_id: string;
  subject_id: string;
}

export async function getSubjectByUserId(userId: string): Promise<{ id: string; user_id: string; subject_code: string; display_name: string | null } | null> {
  const result = await pool.query(
    `SELECT id, user_id, subject_code, display_name
     FROM subjects
     WHERE user_id = $1
     LIMIT 1`,
    [userId]
  );

  return result.rows[0] ?? null;
}

export async function listSubjectDevices(subjectId: string): Promise<SubjectDeviceRow[]> {
  const result = await pool.query(
    `SELECT
        da.id AS device_assignment_id,
        d.id AS device_id,
        d.device_code,
        d.name AS device_name,
        d.mqtt_topic,
        d.status AS device_status,
        s.id AS subject_id,
        s.subject_code,
        s.display_name AS subject_name,
        da.assigned_at,
        da.unassigned_at
     FROM device_assignments da
     JOIN devices d ON d.id = da.device_id
     JOIN subjects s ON s.id = da.subject_id
     WHERE da.subject_id = $1
       AND da.status = 'active'
     ORDER BY da.assigned_at DESC`,
    [subjectId]
  );

  return result.rows;
}

export async function listSubjectReadings(subjectId: string, options: { deviceId?: string; from?: string; to?: string; limit: number; offset: number }): Promise<SensorReadingRow[]> {
  const params: unknown[] = [subjectId];
  const where: string[] = ['sr.subject_id = $1'];

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

  params.push(options.limit, options.offset);

  const result = await pool.query(
    `SELECT
        sr.id,
        sr.device_id,
        sr.subject_id,
        sr.device_assignment_id,
        sr.recorded_at,
        sr.received_at,
        sr.ph,
        sr.fructosamine,
        sr.salivary_glucose,
        sr.raw_payload,
        sr.quality_flag,
        sr.created_at
     FROM sensor_readings sr
     WHERE ${where.join(' AND ')}
     ORDER BY sr.recorded_at DESC, sr.created_at DESC
     LIMIT $${params.length - 1}
     OFFSET $${params.length}`,
    params
  );

  return result.rows;
}

export async function listSubjectReadingTrends(subjectId: string, options: { deviceId?: string; from?: string; to?: string; bucket: 'hour' | 'day'; limit: number }): Promise<Array<{ bucket_start: string; reading_count: string; ph_avg: string | null; fructosamine_avg: string | null; salivary_glucose_avg: string | null }>> {
  const params: unknown[] = [subjectId];
  const where: string[] = ['subject_id = $1'];

  if (options.deviceId) {
    params.push(options.deviceId);
    where.push(`device_id = $${params.length}`);
  }

  if (options.from) {
    params.push(options.from);
    where.push(`recorded_at >= $${params.length}`);
  }

  if (options.to) {
    params.push(options.to);
    where.push(`recorded_at <= $${params.length}`);
  }

  params.push(options.limit);

  const bucketExpression = options.bucket === 'day'
    ? `date_trunc('day', recorded_at)`
    : `date_trunc('hour', recorded_at)`;

  const result = await pool.query(
    `SELECT
        ${bucketExpression} AS bucket_start,
        COUNT(*)::text AS reading_count,
        AVG(ph)::text AS ph_avg,
        AVG(fructosamine)::text AS fructosamine_avg,
        AVG(salivary_glucose)::text AS salivary_glucose_avg
     FROM sensor_readings
     WHERE ${where.join(' AND ')}
     GROUP BY 1
     ORDER BY 1 DESC
     LIMIT $${params.length}`,
    params
  );

  return result.rows;
}

export async function getLatestSubjectReading(subjectId: string, deviceId?: string): Promise<SensorReadingRow | null> {
  const params: unknown[] = [subjectId];
  const where: string[] = ['sr.subject_id = $1'];

  if (deviceId) {
    params.push(deviceId);
    where.push(`sr.device_id = $${params.length}`);
  }

  const result = await pool.query(
    `SELECT
        sr.id,
        sr.device_id,
        sr.subject_id,
        sr.device_assignment_id,
        sr.recorded_at,
        sr.received_at,
        sr.ph,
        sr.fructosamine,
        sr.salivary_glucose,
        sr.raw_payload,
        sr.quality_flag,
        sr.created_at
     FROM sensor_readings sr
     WHERE ${where.join(' AND ')}
     ORDER BY sr.recorded_at DESC, sr.created_at DESC
     LIMIT 1`,
    params
  );

  return result.rows[0] ?? null;
}

export async function getSensorReadingById(sensorReadingId: string): Promise<SensorReadingRow | null> {
  const result = await pool.query(
    `SELECT
        sr.id,
        sr.device_id,
        sr.subject_id,
        sr.device_assignment_id,
        sr.recorded_at,
        sr.received_at,
        sr.ph,
        sr.fructosamine,
        sr.salivary_glucose,
        sr.raw_payload,
        sr.quality_flag,
        sr.created_at
     FROM sensor_readings sr
     WHERE sr.id = $1
     LIMIT 1`,
    [sensorReadingId]
  );

  return result.rows[0] ?? null;
}

export async function insertSensorReading(input: SensorReadingInsert): Promise<SensorReadingRow> {
  const result = await pool.query(
    `INSERT INTO sensor_readings (
        id,
        device_id,
        subject_id,
        device_assignment_id,
        recorded_at,
        received_at,
        ph,
        fructosamine,
        salivary_glucose,
        raw_payload,
        quality_flag,
        created_at
     ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, NOW())
     RETURNING
        id,
        device_id,
        subject_id,
        device_assignment_id,
        recorded_at,
        received_at,
        ph,
        fructosamine,
        salivary_glucose,
        raw_payload,
        quality_flag,
        created_at`,
    [
      input.id,
      input.deviceId,
      input.subjectId,
      input.deviceAssignmentId,
      input.recordedAt,
      input.receivedAt,
      input.ph,
      input.fructosamine,
      input.salivaryGlucose,
      input.rawPayload,
      input.qualityFlag
    ]
  );

  return result.rows[0];
}

export async function resolveDeviceByTopicFirst(params: { topic: string; topicPrefix: string; payload: Record<string, unknown> | null }): Promise<DeviceResolutionRow | null> {
  const candidates = buildDeviceCandidates(params.topic, params.topicPrefix, params.payload);

  for (const candidate of candidates) {
    const result = await pool.query(
      `SELECT id, device_code, mqtt_topic, name, status
      FROM devices
      WHERE id::text = $1 OR device_code = $1 OR mqtt_topic = $1
      LIMIT 1`,
      [candidate]
    );
    if (result.rows[0]) return result.rows[0];
  }

  return null;
}

export async function resolveActiveAssignment(deviceId: string): Promise<ActiveAssignmentRow | null> {
  const result = await pool.query(
    `SELECT id, device_id, subject_id
     FROM device_assignments
     WHERE device_id = $1
       AND status = 'active'
     ORDER BY assigned_at DESC
     LIMIT 1`,
    [deviceId]
  );

  return result.rows[0] ?? null;
}

function buildDeviceCandidates(topic: string, topicPrefix: string, payload: Record<string, unknown> | null): string[] {
  const candidates = new Set<string>();
  const normalizedTopic = topic.trim();
  if (normalizedTopic) {
    candidates.add(normalizedTopic);
  }

  const topicTokens = normalizedTopic.split('/').filter(Boolean);
  const prefixTokens = topicPrefix.split('/').filter(Boolean);
  const prefixMatches = prefixTokens.length > 0 && prefixTokens.every((token, index) => topicTokens[index] === token);
  if (prefixMatches) {
    const remainder = topicTokens.slice(prefixTokens.length);
    if (remainder.length > 0) {
      candidates.add(remainder[0]);
      candidates.add(remainder[remainder.length - 1]);
      const readingsIndex = remainder.indexOf('readings');
      if (readingsIndex > 0) {
        candidates.add(remainder[readingsIndex - 1]);
      }
    }
  }

  if (payload) {
    const payloadKeys = ['device_id', 'device_code', 'mqtt_topic', 'deviceId', 'deviceCode'];
    for (const key of payloadKeys) {
      const value = payload[key];
      if (typeof value === 'string' && value.trim()) {
        candidates.add(value.trim());
      }
    }
  }

  return Array.from(candidates);
}
