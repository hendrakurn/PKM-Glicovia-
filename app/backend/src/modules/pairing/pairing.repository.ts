import type { PoolClient } from 'pg';
import { createId } from '../../utils/ids';
import type { DeviceStatus } from '../devices/device.types';

export type PairingStatus = 'pending' | 'used' | 'expired' | 'revoked';
export type AssignmentStatus = 'active' | 'ended';

export interface PairingTokenRecord {
  id: string;
  device_id: string;
  token: string;
  qr_payload: string;
  status: PairingStatus;
  expires_at: string;
  used_at: string | null;
  revoked_at: string | null;
  created_at: string;
}

export interface DeviceAssignmentRecord {
  id: string;
  device_id: string;
  subject_id: string;
  pairing_token_id: string | null;
  status: AssignmentStatus;
  assigned_at: string;
  unassigned_at: string | null;
  created_at: string;
}

export interface ActiveAssignmentLookup {
  id: string;
  device_id: string;
  subject_id: string;
  pairing_token_id: string | null;
  status: AssignmentStatus;
  assigned_at: Date | string;
  unassigned_at: Date | string | null;
  created_at: Date | string;
  subject_code: string | null;
  subject_display_name: string | null;
}

export interface TokenWithDevice {
  id: string;
  device_id: string;
  device_code: string;
  token: string;
  qr_payload: string;
  status: PairingStatus;
  expires_at: Date | string;
  used_at: Date | string | null;
  revoked_at: Date | string | null;
  created_at: Date | string;
}

function toIso(value: Date | string | null): string | null {
  return value === null ? null : new Date(value).toISOString();
}

export async function revokePendingTokensForDevice(client: PoolClient, deviceId: string): Promise<number> {
  const result = await client.query(
    `UPDATE pairing_tokens
     SET status = 'revoked', revoked_at = NOW()
     WHERE device_id = $1 AND status = 'pending'`,
    [deviceId]
  );
  return result.rowCount ?? 0;
}

export async function insertPairingToken(
  client: PoolClient,
  input: {
    deviceId: string;
    token: string;
    qrPayload: string;
    expiresAt: Date;
  }
): Promise<PairingTokenRecord> {
  const id = createId();
  const result = await client.query<PairingTokenRecord>(
    `INSERT INTO pairing_tokens (
      id,
      device_id,
      token,
      qr_payload,
      status,
      expires_at,
      created_at
    )
    VALUES ($1, $2, $3, $4, 'pending', $5, NOW())
    RETURNING
      id,
      device_id,
      token,
      qr_payload,
      status,
      expires_at,
      used_at,
      revoked_at,
      created_at`,
    [id, input.deviceId, input.token, input.qrPayload, input.expiresAt.toISOString()]
  );

  const row = result.rows[0];
  return {
    ...row,
    expires_at: toIso(row.expires_at) ?? input.expiresAt.toISOString(),
    used_at: toIso(row.used_at),
    revoked_at: toIso(row.revoked_at),
    created_at: toIso(row.created_at) ?? new Date().toISOString()
  };
}

export async function findPairingTokenForUpdate(client: PoolClient, token: string): Promise<TokenWithDevice | null> {
  const result = await client.query<TokenWithDevice>(
    `SELECT
       pt.id,
       pt.device_id,
       d.device_code,
       pt.token,
       pt.qr_payload,
       pt.status,
       pt.expires_at,
       pt.used_at,
       pt.revoked_at,
       pt.created_at
     FROM pairing_tokens pt
     INNER JOIN devices d ON d.id = pt.device_id
     WHERE pt.token = $1
     FOR UPDATE OF pt, d`,
    [token]
  );

  if (result.rows.length === 0) return null;
  const row = result.rows[0];
  return {
    ...row,
    expires_at: toIso(row.expires_at) ?? new Date().toISOString(),
    used_at: toIso(row.used_at),
    revoked_at: toIso(row.revoked_at),
    created_at: toIso(row.created_at) ?? new Date().toISOString()
  };
}

export async function getActiveAssignmentForDeviceForUpdate(client: PoolClient, deviceId: string): Promise<ActiveAssignmentLookup | null> {
  const result = await client.query<ActiveAssignmentLookup>(
    `SELECT
       da.id,
       da.device_id,
       da.subject_id,
       da.pairing_token_id,
       da.status,
       da.assigned_at,
       da.unassigned_at,
       da.created_at,
       s.subject_code,
       s.display_name AS subject_display_name
     FROM device_assignments da
     INNER JOIN subjects s ON s.id = da.subject_id
     WHERE da.device_id = $1 AND da.status = 'active'
     ORDER BY da.assigned_at DESC
     LIMIT 1`,
    [deviceId]
  );

  return result.rows[0] ?? null;
}

export async function getActiveAssignmentForSubjectForUpdate(client: PoolClient, subjectId: string): Promise<ActiveAssignmentLookup | null> {
  const result = await client.query<ActiveAssignmentLookup>(
    `SELECT
       da.id,
       da.device_id,
       da.subject_id,
       da.pairing_token_id,
       da.status,
       da.assigned_at,
       da.unassigned_at,
       da.created_at,
       s.subject_code,
       s.display_name AS subject_display_name
     FROM device_assignments da
     INNER JOIN subjects s ON s.id = da.subject_id
     WHERE da.subject_id = $1 AND da.status = 'active'
     ORDER BY da.assigned_at DESC
     LIMIT 1`,
    [subjectId]
  );

  return result.rows[0] ?? null;
}

export async function createDeviceAssignment(
  client: PoolClient,
  input: {
    deviceId: string;
    subjectId: string;
    pairingTokenId: string;
  }
): Promise<DeviceAssignmentRecord> {
  const id = createId();
  const result = await client.query<DeviceAssignmentRecord>(
    `INSERT INTO device_assignments (
      id,
      device_id,
      subject_id,
      pairing_token_id,
      status,
      assigned_at,
      created_at
    )
    VALUES ($1, $2, $3, $4, 'active', NOW(), NOW())
    RETURNING
      id,
      device_id,
      subject_id,
      pairing_token_id,
      status,
      assigned_at,
      unassigned_at,
      created_at`,
    [id, input.deviceId, input.subjectId, input.pairingTokenId]
  );

  const row = result.rows[0];
  return {
    ...row,
    assigned_at: toIso(row.assigned_at) ?? new Date().toISOString(),
    unassigned_at: toIso(row.unassigned_at),
    created_at: toIso(row.created_at) ?? new Date().toISOString()
  };
}

export async function endActiveAssignment(client: PoolClient, assignmentId: string): Promise<void> {
  await client.query(
    `UPDATE device_assignments
     SET status = 'ended', unassigned_at = NOW()
     WHERE id = $1 AND status = 'active'`,
    [assignmentId]
  );
}

export async function markPairingTokenUsed(client: PoolClient, tokenId: string): Promise<void> {
  await client.query(
    `UPDATE pairing_tokens
     SET status = 'used', used_at = NOW()
     WHERE id = $1`,
    [tokenId]
  );
}

export async function markPairingTokenExpired(client: PoolClient, tokenId: string): Promise<void> {
  await client.query(
    `UPDATE pairing_tokens
     SET status = 'expired'
     WHERE id = $1 AND status = 'pending'`,
    [tokenId]
  );
}

export async function updateDeviceStatus(client: PoolClient, deviceId: string, status: DeviceStatus): Promise<void> {
  await client.query('UPDATE devices SET status = $2, updated_at = NOW() WHERE id = $1', [deviceId, status]);
}
