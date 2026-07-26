import { randomUUID } from 'crypto';
import {
  getLatestSubjectReading,
  getSubjectByUserId,
  insertSensorReading,
  listSubjectDevices,
  listSubjectReadings,
  listSubjectReadingTrends,
  resolveActiveAssignment,
  resolveDeviceByTopicFirst
} from './readings.repository';

export interface AuthenticatedUser {
  id: string;
}

export { resolveActiveAssignment, resolveDeviceByTopicFirst };

export function assertUserId(user: AuthenticatedUser | undefined): string {
  if (!user?.id) {
    throw Object.assign(new Error('Unauthorized'), { statusCode: 401 });
  }

  return user.id;
}

export async function getSubjectContext(userId: string) {
  const subject = await getSubjectByUserId(userId);
  if (!subject) {
    throw Object.assign(new Error('Subject profile not found'), { statusCode: 404 });
  }
  return subject;
}

export async function getMyDevices(userId: string) {
  const subject = await getSubjectContext(userId);
  const devices = await listSubjectDevices(subject.id);
  return { subject, devices };
}

export async function getMyReadings(userId: string, query: { deviceId?: string; from?: string; to?: string; limit?: number; offset?: number }) {
  const subject = await getSubjectContext(userId);
  const readings = await listSubjectReadings(subject.id, {
    deviceId: query.deviceId,
    from: query.from,
    to: query.to,
    limit: query.limit ?? 100,
    offset: query.offset ?? 0
  });

  return { subject, readings };
}

export async function getMyLatestReading(userId: string, deviceId?: string) {
  const subject = await getSubjectContext(userId);
  const reading = await getLatestSubjectReading(subject.id, deviceId);
  return { subject, reading };
}

export async function getMyReadingTrends(userId: string, query: { deviceId?: string; from?: string; to?: string; bucket?: 'hour' | 'day'; limit?: number }) {
  const subject = await getSubjectContext(userId);
  const trends = await listSubjectReadingTrends(subject.id, {
    deviceId: query.deviceId,
    from: query.from,
    to: query.to,
    bucket: query.bucket ?? 'hour',
    limit: query.limit ?? 48
  });

  return { subject, trends };
}

export async function saveSensorReading(input: {
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
}) {
  const row = await insertSensorReading({
    id: randomUUID(),
    ...input
  });

  return row;
}
