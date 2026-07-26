import { pool } from '../../db/pool';
import { createId } from '../../utils/ids';
import type { PoolClient } from 'pg';
import type {
  ActiveAssignmentRecord,
  CreateDeviceInput,
  DeviceRecord,
  DeviceStatus,
  DeviceWithAssignment,
  UpdateDeviceInput
} from './device.types';

interface DeviceJoinedRow {
  id: string;
  device_code: string;
  name: string | null;
  mqtt_topic: string;
  status: DeviceStatus;
  firmware_version: string | null;
  last_seen_at: Date | string | null;
  created_at: Date | string;
  updated_at: Date | string;
  active_assignment_id: string | null;
  active_assignment_subject_id: string | null;
  active_assignment_assigned_at: Date | string | null;
  active_assignment_subject_code: string | null;
  active_assignment_subject_name: string | null;
}

function toIso(value: Date | string | null): string | null {
  return value === null ? null : new Date(value).toISOString();
}

function mapRow(row: DeviceJoinedRow): DeviceWithAssignment {
  const device: DeviceRecord = {
    id: row.id,
    device_code: row.device_code,
    name: row.name,
    mqtt_topic: row.mqtt_topic,
    status: row.status,
    firmware_version: row.firmware_version,
    last_seen_at: toIso(row.last_seen_at),
    created_at: toIso(row.created_at) ?? new Date().toISOString(),
    updated_at: toIso(row.updated_at) ?? new Date().toISOString()
  };

  const activeAssignment: ActiveAssignmentRecord | null = row.active_assignment_id
    ? {
        id: row.active_assignment_id,
        subject_id: row.active_assignment_subject_id ?? '',
        assigned_at: toIso(row.active_assignment_assigned_at) ?? new Date().toISOString(),
        subject_code: row.active_assignment_subject_code,
        subject_name: row.active_assignment_subject_name
      }
    : null;

  return {
    ...device,
    active_assignment: activeAssignment
  };
}

function mapActiveAssignment(row: { id: string; subject_id: string; assigned_at: Date | string; subject_code: string | null; subject_display_name: string | null } | null): ActiveAssignmentRecord | null {
  if (!row) {
    return null;
  }

  return {
    id: row.id,
    subject_id: row.subject_id,
    assigned_at: toIso(row.assigned_at) ?? new Date().toISOString(),
    subject_code: row.subject_code,
    subject_name: row.subject_display_name
  };
}

function buildDeviceQuery(): string {
  return `SELECT
    d.id,
    d.device_code,
    d.name,
    d.mqtt_topic,
    d.status,
    d.firmware_version,
    d.last_seen_at,
    d.created_at,
    d.updated_at,
    a.id AS active_assignment_id,
    a.subject_id AS active_assignment_subject_id,
    a.assigned_at AS active_assignment_assigned_at,
    s.subject_code AS active_assignment_subject_code,
    s.display_name AS active_assignment_subject_name
  FROM devices d
  LEFT JOIN LATERAL (
    SELECT da.id, da.subject_id, da.assigned_at
    FROM device_assignments da
    WHERE da.device_id = d.id AND da.status = 'active'
    ORDER BY da.assigned_at DESC
    LIMIT 1
  ) a ON TRUE
  LEFT JOIN subjects s ON s.id = a.subject_id`;
}

export async function listDevices(): Promise<DeviceWithAssignment[]> {
  const result = await pool.query<DeviceJoinedRow>(`${buildDeviceQuery()} ORDER BY d.created_at DESC`);
  return result.rows.map(mapRow);
}

export async function getDeviceById(id: string): Promise<DeviceWithAssignment | null> {
  const result = await pool.query<DeviceJoinedRow>(`${buildDeviceQuery()} WHERE d.id = $1`, [id]);
  return result.rows[0] ? mapRow(result.rows[0]) : null;
}

export async function createDevice(input: CreateDeviceInput): Promise<DeviceWithAssignment> {
  const id = createId();
  const result = await pool.query<DeviceJoinedRow>(
    `INSERT INTO devices (
      id,
      device_code,
      name,
      mqtt_topic,
      status,
      firmware_version,
      last_seen_at,
      created_at,
      updated_at
    )
    VALUES ($1, $2, $3, $4, $5, $6, $7, NOW(), NOW())
    RETURNING
      id,
      device_code,
      name,
      mqtt_topic,
      status,
      firmware_version,
      last_seen_at,
      created_at,
      updated_at,
      NULL::uuid AS active_assignment_id,
      NULL::uuid AS active_assignment_subject_id,
      NULL::timestamptz AS active_assignment_assigned_at,
      NULL::varchar AS active_assignment_subject_code,
      NULL::varchar AS active_assignment_subject_name`,
    [
      id,
      input.deviceCode,
      input.name ?? null,
      input.mqttTopic,
      input.status ?? 'unpaired',
      input.firmwareVersion ?? null,
      input.lastSeenAt ?? null
    ]
  );

  return mapRow(result.rows[0]);
}

export async function updateDevice(id: string, input: UpdateDeviceInput): Promise<DeviceWithAssignment | null> {
  const result = await pool.query<DeviceJoinedRow>(
    `UPDATE devices
     SET
       device_code = COALESCE($2, device_code),
       name = COALESCE($3, name),
       mqtt_topic = COALESCE($4, mqtt_topic),
       status = COALESCE($5, status),
       firmware_version = COALESCE($6, firmware_version),
       last_seen_at = COALESCE($7, last_seen_at),
       updated_at = NOW()
     WHERE id = $1
     RETURNING
       id,
       device_code,
       name,
       mqtt_topic,
       status,
       firmware_version,
       last_seen_at,
       created_at,
       updated_at,
       NULL::uuid AS active_assignment_id,
       NULL::uuid AS active_assignment_subject_id,
       NULL::timestamptz AS active_assignment_assigned_at,
       NULL::varchar AS active_assignment_subject_code,
       NULL::varchar AS active_assignment_subject_name`,
    [
      id,
      input.deviceCode ?? null,
      input.name ?? null,
      input.mqttTopic ?? null,
      input.status ?? null,
      input.firmwareVersion ?? null,
      input.lastSeenAt ?? null
    ]
  );

  return result.rows[0] ? mapRow(result.rows[0]) : null;
}

export async function deleteDevice(id: string): Promise<boolean> {
  const result = await pool.query('DELETE FROM devices WHERE id = $1', [id]);
  return result.rowCount === 1;
}

export async function updateDeviceStatus(client: PoolClient, id: string, status: DeviceStatus): Promise<void> {
  await client.query('UPDATE devices SET status = $2, updated_at = NOW() WHERE id = $1', [id, status]);
}

export async function updateDeviceLastSeen(client: PoolClient, id: string, lastSeenAt: Date): Promise<void> {
  await client.query('UPDATE devices SET last_seen_at = $2, updated_at = NOW() WHERE id = $1', [id, lastSeenAt.toISOString()]);
}

export async function getDeviceByIdForUpdate(client: PoolClient, id: string): Promise<DeviceWithAssignment | null> {
  const result = await client.query<DeviceJoinedRow>(`${buildDeviceQuery()} WHERE d.id = $1 FOR UPDATE OF d`, [id]);
  return result.rows[0] ? mapRow(result.rows[0]) : null;
}

export async function getActiveAssignmentForDeviceForUpdate(client: PoolClient, deviceId: string): Promise<ActiveAssignmentRecord | null> {
  const result = await client.query<{ id: string; subject_id: string; assigned_at: Date | string; subject_code: string | null; subject_display_name: string | null }>(
    `SELECT
       da.id,
       da.subject_id,
       da.assigned_at,
       s.subject_code,
       s.display_name AS subject_display_name
     FROM device_assignments da
     INNER JOIN subjects s ON s.id = da.subject_id
     WHERE da.device_id = $1 AND da.status = 'active'
     ORDER BY da.assigned_at DESC
     LIMIT 1
     FOR UPDATE OF da`,
    [deviceId]
  );

  return mapActiveAssignment(result.rows[0] ?? null);
}
