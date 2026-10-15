import { logger } from '../config/logger';
import { env } from '../config/env';
import { resolveActiveAssignment, resolveDeviceByTopicFirst, saveSensorReading } from '../modules/readings/readings.service';
import { triggerInferenceForSensorReading } from '../modules/inference/inference.service';
import { parseTopicResolution } from './topic-parser';

function asRecord(value: unknown): Record<string, unknown> | null {
  return value !== null && typeof value === 'object' && !Array.isArray(value) ? (value as Record<string, unknown>) : null;
}

function parsePayload(buffer: Buffer): { rawPayload: unknown; payload: Record<string, unknown> | null } {
  const text = buffer.toString('utf8');
  if (!text.trim()) {
    return { rawPayload: { raw: text, parse_error: 'empty_payload' }, payload: null };
  }

  try {
    const parsed = JSON.parse(text);
    const payload = asRecord(parsed);
    return {
      rawPayload: payload ?? { value: parsed },
      payload
    };
  } catch {
    return { rawPayload: { raw: text, parse_error: 'malformed_json' }, payload: null };
  }
}

function parseOptionalNumber(value: unknown): number | null {
  if (value === undefined || value === null || value === '') return null;
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : null;
}

function parseRecordedAt(payload: Record<string, unknown> | null): string {
  const candidateKeys = ['recorded_at', 'recordedAt', 'timestamp', 'time', 'received_at'];
  for (const key of candidateKeys) {
    const value = payload?.[key];
    if (typeof value === 'string' && !Number.isNaN(Date.parse(value))) {
      return new Date(value).toISOString();
    }
  }
  return new Date().toISOString();
}

function determineQualityFlag(payload: Record<string, unknown> | null, rawPayload: unknown): 'valid' | 'suspect' | 'incomplete' {
  if (rawPayload && typeof rawPayload === 'object' && 'parse_error' in rawPayload) {
    return 'incomplete';
  }

  const hasAnyMeasurement = ['ph', 'fructosamine', 'salivary_glucose', 'salivaryGlucose'].some((key) => payload?.[key] !== undefined && payload?.[key] !== null && payload?.[key] !== '');
  if (!hasAnyMeasurement) return 'incomplete';
  return 'valid';
}

export async function handleMqttMessage(topic: string, payloadBuffer: Buffer): Promise<void> {
  if (!topic.endsWith('/readings')) {
    return;
  }
  const { rawPayload, payload } = parsePayload(payloadBuffer);
  const resolution = parseTopicResolution(topic, env.MQTT_TOPIC_PREFIX);

  const device = await resolveDeviceByTopicFirst({ topic, topicPrefix: env.MQTT_TOPIC_PREFIX, payload });
  if (!device) {
    logger.warn('MQTT message ignored because device could not be resolved', {
      topic,
      resolution,
      rawPayload
    });
    return;
  }

  const assignment = await resolveActiveAssignment(device.id);
  const recordedAt = parseRecordedAt(payload);
  const receivedAt = new Date().toISOString();
  const qualityFlag = determineQualityFlag(payload, rawPayload);

  const reading = await saveSensorReading({
    deviceId: device.id,
    subjectId: assignment?.subject_id ?? null,
    deviceAssignmentId: assignment?.id ?? null,
    recordedAt,
    receivedAt,
    ph: parseOptionalNumber(payload?.ph),
    fructosamine: parseOptionalNumber(payload?.fructosamine),
    salivaryGlucose: parseOptionalNumber(payload?.salivary_glucose ?? payload?.salivaryGlucose),
    rawPayload,
    qualityFlag
  });

  void triggerInferenceForSensorReading(reading);

  logger.info('MQTT reading stored', {
    topic,
    deviceId: device.id,
    subjectId: assignment?.subject_id ?? null,
    deviceAssignmentId: assignment?.id ?? null,
    recordedAt,
    qualityFlag
  });
}
