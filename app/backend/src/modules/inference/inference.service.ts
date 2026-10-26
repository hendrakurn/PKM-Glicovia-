import { randomUUID } from 'crypto';
import { env } from '../../config/env';
import { logger } from '../../config/logger';
import { getSensorReadingById, type SensorReadingRow } from '../readings/readings.repository';
import { upsertDeployedModelVersion, type ModelVersionRow } from '../models/models.repository';
import { savePredictionResult, type PredictionResultRow } from '../predictions/predictions.repository';
import { getDeviceById } from '../devices/device.repository';
import { publishMqttMessage } from '../../mqtt/mqtt-client';

export interface MlPredictionPayload {
  id: string;
  glucose_saliva: number;
  ph_value: number;
  fructosamine_umol_l: number;
}

interface MlModelInfoResponse {
  model_name?: unknown;
  version?: unknown;
}

interface MlPredictionResponse {
  prediction?: unknown;
  category?: unknown;
  confidence?: unknown;
  timestamp?: unknown;
}

export interface InferenceResult {
  reading: SensorReadingRow;
  modelVersion: ModelVersionRow;
  prediction: PredictionResultRow;
  mlPayload: MlPredictionPayload;
  mlResponse: MlPredictionResponse;
}

const FALLBACK_MODEL_INFO = {
  modelName: 'GlicoSaliva SVR',
  version: '2.0.0'
};

function httpError(message: string, statusCode: number): Error & { statusCode: number } {
  return Object.assign(new Error(message), { statusCode });
}

function asFiniteNumber(value: string | number | null, fieldName: string): number {
  if (value === null || value === '') {
    throw httpError(`Sensor reading is missing ${fieldName}`, 422);
  }

  const parsed = Number(value);
  if (!Number.isFinite(parsed)) {
    throw httpError(`Sensor reading has invalid ${fieldName}`, 422);
  }

  return parsed;
}

function isValidIsoTimestamp(value: unknown): value is string {
  return typeof value === 'string' && !Number.isNaN(Date.parse(value));
}

function getCategoryName(category: unknown): string | null {
  if (typeof category === 'string' && category.trim()) return category;
  if (category && typeof category === 'object' && 'name' in category) {
    const name = (category as { name?: unknown }).name;
    if (typeof name === 'string' && name.trim()) return name;
  }
  return null;
}

function normalizeMlPrediction(response: MlPredictionResponse): {
  glucoseEstimate: number;
  clinicalCategory: string | null;
  confidenceScore: number | null;
  predictedAt: string;
} {
  const glucoseEstimate = Number(response.prediction);
  if (!Number.isFinite(glucoseEstimate)) {
    throw httpError('ML service returned an invalid prediction value', 502);
  }

  const confidence = response.confidence === undefined || response.confidence === null ? null : Number(response.confidence);
  if (confidence !== null && !Number.isFinite(confidence)) {
    throw httpError('ML service returned an invalid confidence value', 502);
  }

  return {
    glucoseEstimate,
    clinicalCategory: getCategoryName(response.category),
    confidenceScore: confidence,
    predictedAt: isValidIsoTimestamp(response.timestamp) ? new Date(response.timestamp).toISOString() : new Date().toISOString()
  };
}

async function fetchMlJson<T>(path: string, init?: RequestInit): Promise<T> {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), env.ML_SERVICE_TIMEOUT_MS);
  const url = new URL(path, env.ML_SERVICE_URL).toString();

  try {
    const response = await fetch(url, {
      ...init,
      signal: controller.signal,
      headers: {
        Accept: 'application/json',
        ...(init?.body ? { 'Content-Type': 'application/json' } : {}),
        ...init?.headers
      }
    });
    const text = await response.text();
    const payload = text ? JSON.parse(text) as unknown : undefined;

    if (!response.ok) {
      const detail = payload && typeof payload === 'object' && 'detail' in payload ? String((payload as { detail?: unknown }).detail) : response.statusText;
      throw httpError(`ML service ${path} failed: ${detail}`, 502);
    }

    return payload as T;
  } catch (error) {
    if (error instanceof Error && error.name === 'AbortError') {
      throw httpError(`ML service ${path} timed out after ${env.ML_SERVICE_TIMEOUT_MS}ms`, 504);
    }
    if (error instanceof SyntaxError) {
      throw httpError(`ML service ${path} returned invalid JSON`, 502);
    }
    throw error;
  } finally {
    clearTimeout(timeout);
  }
}

async function resolveModelVersion(): Promise<ModelVersionRow> {
  let modelName = FALLBACK_MODEL_INFO.modelName;
  let version = FALLBACK_MODEL_INFO.version;

  try {
    const modelInfo = await fetchMlJson<MlModelInfoResponse>('/model-info');
    if (typeof modelInfo.model_name === 'string' && modelInfo.model_name.trim()) {
      modelName = modelInfo.model_name.trim();
    }
    if (typeof modelInfo.version === 'string' && modelInfo.version.trim()) {
      version = modelInfo.version.trim();
    }
  } catch (error) {
    logger.warn('ML model-info unavailable; using fallback model metadata', {
      error: error instanceof Error ? error.message : String(error),
      modelName,
      version
    });
  }

  return upsertDeployedModelVersion({
    id: randomUUID(),
    modelName,
    version
  });
}

// Koefisien kalibrasi SEMENTARA (bukan hasil fit buffer/larutan standar). Harus sama dengan CAL di
// ml_pipeline/src/convert_data_log.py, karena model dilatih dari fitur yang dikonversi dengan nilai ini.
const PROVISIONAL_CAL = {
  rfOhm: 100e3,
  ph: { m: -0.05916, c: 0.3226 },   // V = m*pH + c
  glu: { a: 1000, b: 0 },           // I_nA = a*C + b
  fru: { a: 35, b: -4000 }          // I_nA = a*C + b
};
const ML_BOUNDS = { glucose: [0.1, 10], ph: [4, 9], fructosamine: [150, 500] } as const;
// Satuan yang dikirim firmware bila nilainya sudah terkalibrasi.
const REAL_UNITS = { ph: ['pH'], salivary_glucose: ['mg/dL'], fructosamine: ['umol/L', 'µmol/L'] } as const;

type Param = keyof typeof REAL_UNITS;

function rawValue(reading: SensorReadingRow, key: string): number | null {
  const raw = (reading.raw_payload as { raw?: Record<string, unknown> } | null)?.raw;
  const value = raw?.[key];
  return typeof value === 'number' && Number.isFinite(value) ? value : null;
}

function clamp(value: number, [lo, hi]: readonly [number, number]): number {
  return Math.min(Math.max(value, lo), hi);
}

// Volt mentah -> satuan riil dengan kalibrasi sementara. null bila volt yang dibutuhkan tidak ada.
function provisionalValue(reading: SensorReadingRow, param: Param): number | null {
  if (param === 'ph') {
    const v = rawValue(reading, 'v_ph');
    return v === null ? null : clamp((v - PROVISIONAL_CAL.ph.c) / PROVISIONAL_CAL.ph.m, ML_BOUNDS.ph);
  }
  if (param === 'salivary_glucose') {
    const i = rawValue(reading, 'i_glu_nA');
    return i === null ? null : clamp((i - PROVISIONAL_CAL.glu.b) / PROVISIONAL_CAL.glu.a, ML_BOUNDS.glucose);
  }
  const vMid = rawValue(reading, 'v_mid');
  const vFru = rawValue(reading, 'v_fru');
  if (vMid === null || vFru === null) return null;
  const iNA = ((vMid - vFru) / PROVISIONAL_CAL.rfOhm) * 1e9;
  return clamp((iNA - PROVISIONAL_CAL.fru.b) / PROVISIONAL_CAL.fru.a, ML_BOUNDS.fructosamine);
}

// Firmware mengisi kolom ph/fructosamine/salivary_glucose dengan volt (atau null) sebelum kalibrasi,
// dan menandainya lewat raw_payload.units.<param> ("V"/"none"). Karena itu keputusan lewat `units`,
// bukan lewat null. Tanpa `units` (firmware lama) nilai kolom dipakai apa adanya bila ada.
function resolveParam(reading: SensorReadingRow, param: Param, column: string | number | null): number | null {
  const units = (reading.raw_payload as { units?: Record<string, unknown> } | null)?.units;
  const unit = units?.[param];
  const isReal = typeof unit === 'string' ? (REAL_UNITS[param] as readonly string[]).includes(unit) : column !== null;
  if (isReal && column !== null && column !== '') return Number(column);
  logger.warn('Using provisional calibration (raw volts) for inference', { readingId: reading.id, param });
  return provisionalValue(reading, param);
}

export function mapSensorReadingToMlPayload(reading: SensorReadingRow): MlPredictionPayload {
  if (reading.quality_flag === 'incomplete') {
    throw httpError('Sensor reading is incomplete and cannot be sent to inference', 422);
  }

  return {
    id: reading.id,
    glucose_saliva: asFiniteNumber(resolveParam(reading, 'salivary_glucose', reading.salivary_glucose), 'salivary_glucose'),
    ph_value: asFiniteNumber(resolveParam(reading, 'ph', reading.ph), 'ph'),
    fructosamine_umol_l: asFiniteNumber(resolveParam(reading, 'fructosamine', reading.fructosamine), 'fructosamine')
  };
}

async function persistFailedPrediction(sensorReadingId: string, modelVersionId: string): Promise<PredictionResultRow> {
  return savePredictionResult({
    id: randomUUID(),
    sensorReadingId,
    modelVersionId,
    glucoseEstimate: null,
    clinicalCategory: null,
    confidenceScore: null,
    inferenceStatus: 'failed',
    predictedAt: new Date().toISOString()
  });
}

async function callMlPrediction(payload: MlPredictionPayload): Promise<MlPredictionResponse> {
  return fetchMlJson<MlPredictionResponse>('/predict', {
    method: 'POST',
    body: JSON.stringify(payload)
  });
}

export async function runInferenceForSensorReading(reading: SensorReadingRow): Promise<InferenceResult> {
  const modelVersion = await resolveModelVersion();
  let mlPayload: MlPredictionPayload;

  try {
    mlPayload = mapSensorReadingToMlPayload(reading);
  } catch (error) {
    await persistFailedPrediction(reading.id, modelVersion.id);
    throw error;
  }

  try {
    const mlResponse = await callMlPrediction(mlPayload);
    const normalized = normalizeMlPrediction(mlResponse);
    const prediction = await savePredictionResult({
      id: randomUUID(),
      sensorReadingId: reading.id,
      modelVersionId: modelVersion.id,
      glucoseEstimate: normalized.glucoseEstimate,
      clinicalCategory: normalized.clinicalCategory,
      confidenceScore: normalized.confidenceScore,
      inferenceStatus: 'success',
      predictedAt: normalized.predictedAt
    });

    return {
      reading,
      modelVersion,
      prediction,
      mlPayload,
      mlResponse
    };
  } catch (error) {
    await persistFailedPrediction(reading.id, modelVersion.id);
    throw error;
  }
}

export async function runInferenceForSensorReadingId(sensorReadingId: string): Promise<InferenceResult> {
  const reading = await getSensorReadingById(sensorReadingId);
  if (!reading) {
    throw httpError('Sensor reading not found', 404);
  }

  return runInferenceForSensorReading(reading);
}

export async function triggerInferenceForSensorReading(reading: SensorReadingRow): Promise<void> {
  try {
    const result = await runInferenceForSensorReading(reading);
    logger.info('Inference prediction stored', {
      sensorReadingId: reading.id,
      predictionResultId: result.prediction.id,
      modelVersionId: result.modelVersion.id,
      inferenceStatus: result.prediction.inference_status
    });

    if (result.prediction.inference_status === 'success' && reading.device_id) {
      try {
        const device = await getDeviceById(reading.device_id);
        if (device) {
          const predictionTopic = `${env.MQTT_TOPIC_PREFIX}/devices/${device.device_code}/predictions`;
          const payload = JSON.stringify({
            device_code: device.device_code,
            glucose_estimate: Number(result.prediction.glucose_estimate),
            clinical_category: result.prediction.clinical_category,
            confidence_score: Number(result.prediction.confidence_score),
            timestamp: result.prediction.predicted_at
          });
          await publishMqttMessage(predictionTopic, payload);
          logger.info('Inference prediction published to MQTT for device', {
            topic: predictionTopic,
            deviceCode: device.device_code
          });
        }
      } catch (pubErr) {
        logger.warn('Failed to publish prediction to MQTT', { error: pubErr });
      }
    }
  } catch (error) {
    logger.warn('Inference failed for stored sensor reading', {
      sensorReadingId: reading.id,
      error: error instanceof Error ? error.message : String(error)
    });
  }
}
