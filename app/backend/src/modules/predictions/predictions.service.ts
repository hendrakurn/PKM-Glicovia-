import { randomUUID } from 'crypto';
import { getSubjectContext } from '../readings/readings.service';
import {
  createPredictionResultIfAbsent,
  getLatestPrediction,
  getLatestSubjectPrediction,
  listPredictions,
  listSubjectPredictions,
  listSubjectPredictionTrends
} from './predictions.repository';

export async function getPredictions(query: { limit?: number; offset?: number; sensorReadingId?: string; modelVersionId?: string }) {
  const predictions = await listPredictions({
    limit: query.limit ?? 100,
    offset: query.offset ?? 0,
    sensorReadingId: query.sensorReadingId,
    modelVersionId: query.modelVersionId
  });

  return { predictions };
}

export async function getMyPredictions(userId: string, query: {
  limit?: number;
  offset?: number;
  deviceId?: string;
  sensorReadingId?: string;
  modelVersionId?: string;
}) {
  const subject = await getSubjectContext(userId);
  const predictions = await listSubjectPredictions({
    subjectId: subject.id,
    limit: query.limit ?? 100,
    offset: query.offset ?? 0,
    deviceId: query.deviceId,
    sensorReadingId: query.sensorReadingId,
    modelVersionId: query.modelVersionId
  });

  return { subject, predictions };
}

export async function getMyLatestPrediction(userId: string, deviceId?: string) {
  const subject = await getSubjectContext(userId);
  const prediction = await getLatestSubjectPrediction(subject.id, deviceId);
  return { subject, prediction };
}

export async function getMyPredictionTrends(userId: string, query: {
  deviceId?: string;
  from?: string;
  to?: string;
  bucket?: 'day' | 'week';
  limit?: number;
}) {
  const subject = await getSubjectContext(userId);
  const trends = await listSubjectPredictionTrends({
    subjectId: subject.id,
    deviceId: query.deviceId,
    from: query.from,
    to: query.to,
    bucket: query.bucket ?? 'day',
    limit: query.limit ?? 12
  });

  return { subject, trends };
}

export async function upsertPredictionMetadata(input: {
  sensorReadingId: string;
  modelVersionId: string;
  glucoseEstimate?: number | null;
  clinicalCategory?: string | null;
  confidenceScore?: number | null;
  inferenceStatus?: 'pending' | 'success' | 'failed';
  predictedAt?: string | null;
}) {
  const row = await createPredictionResultIfAbsent({
    id: randomUUID(),
    ...input
  });

  return { prediction: row };
}

export async function getLatestPredictionResult() {
  const prediction = await getLatestPrediction();
  return { prediction };
}
