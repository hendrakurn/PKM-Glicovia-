import * as dotenv from 'dotenv';

dotenv.config();

function readString(name: string, fallback?: string): string {
  const value = process.env[name] ?? fallback;
  if (!value) {
    throw new Error(`Missing required environment variable: ${name}`);
  }
  return value;
}

function readOptionalString(name: string, fallback?: string): string | undefined {
  const value = process.env[name] ?? fallback;
  return value === '' ? undefined : value;
}

function readNumber(name: string, fallback?: number): number {
  const raw = process.env[name];
  if (raw === undefined || raw === '') {
    if (fallback !== undefined) return fallback;
    throw new Error(`Missing required environment variable: ${name}`);
  }

  const value = Number(raw);
  if (!Number.isFinite(value)) {
    throw new Error(`Environment variable ${name} must be a valid number`);
  }

  return value;
}

export const env = {
  NODE_ENV: readString('NODE_ENV', 'development'),
  PORT: readNumber('PORT', 3000),
  HOST: readString('HOST', '0.0.0.0'),
  DATABASE_URL: readString('DATABASE_URL', 'postgresql://postgres:***@localhost:5432/pkmglico'),
  JWT_SECRET: readString('JWT_SECRET', 'pkmglico-dev-jwt-secret'),
  JWT_EXPIRES_IN: readString('JWT_EXPIRES_IN', '7d'),
  LOG_LEVEL: readString('LOG_LEVEL', 'info'),
  MQTT_URL: readOptionalString('MQTT_URL'),
  MQTT_CLIENT_ID: readOptionalString('MQTT_CLIENT_ID') ?? `pkmglico-backend-${Math.random().toString(36).slice(2, 10)}`,
  MQTT_USERNAME: readOptionalString('MQTT_USERNAME'),
  MQTT_PASSWORD: readOptionalString('MQTT_PASSWORD'),
  MQTT_TOPIC_PREFIX: readString('MQTT_TOPIC_PREFIX', 'glicovia'),
  ML_SERVICE_URL: readString('ML_SERVICE_URL', 'http://localhost:8001'),
  ML_SERVICE_TIMEOUT_MS: readNumber('ML_SERVICE_TIMEOUT_MS', 5000)
} as const;
