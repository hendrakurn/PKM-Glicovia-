import { badRequest } from '../../lib/http-error';
import type { CreateDeviceInput, DeviceStatus, UpdateDeviceInput } from './device.types';

const deviceStatuses: DeviceStatus[] = ['unpaired', 'paired', 'offline', 'online', 'inactive'];

function isObject(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null && !Array.isArray(value);
}

function readOptionalString(value: unknown, field: string): string | null | undefined {
  if (value === undefined) return undefined;
  if (value === null) return null;
  if (typeof value !== 'string') {
    throw badRequest(`${field} must be a string or null`);
  }
  const trimmed = value.trim();
  return trimmed.length > 0 ? trimmed : null;
}

function readRequiredString(value: unknown, field: string): string {
  if (typeof value !== 'string') {
    throw badRequest(`${field} is required and must be a string`);
  }
  const trimmed = value.trim();
  if (!trimmed) {
    throw badRequest(`${field} cannot be empty`);
  }
  return trimmed;
}

function readOptionalDeviceStatus(value: unknown): DeviceStatus | undefined {
  if (value === undefined) return undefined;
  if (typeof value !== 'string' || !deviceStatuses.includes(value as DeviceStatus)) {
    throw badRequest(`status must be one of: ${deviceStatuses.join(', ')}`);
  }
  return value as DeviceStatus;
}

function readOptionalIsoDate(value: unknown, field: string): string | null | undefined {
  if (value === undefined) return undefined;
  if (value === null) return null;
  if (typeof value !== 'string') {
    throw badRequest(`${field} must be an ISO date string or null`);
  }
  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) {
    throw badRequest(`${field} must be a valid ISO date string`);
  }
  return parsed.toISOString();
}

export function parseCreateDeviceInput(body: unknown): CreateDeviceInput {
  if (!isObject(body)) {
    throw badRequest('Request body must be an object');
  }

  return {
    deviceCode: readRequiredString(body.deviceCode, 'deviceCode'),
    name: readOptionalString(body.name, 'name'),
    mqttTopic: readRequiredString(body.mqttTopic, 'mqttTopic'),
    status: readOptionalDeviceStatus(body.status),
    firmwareVersion: readOptionalString(body.firmwareVersion, 'firmwareVersion'),
    lastSeenAt: readOptionalIsoDate(body.lastSeenAt, 'lastSeenAt')
  };
}

export function parseUpdateDeviceInput(body: unknown): UpdateDeviceInput {
  if (!isObject(body)) {
    throw badRequest('Request body must be an object');
  }

  const input: UpdateDeviceInput = {};

  if ('deviceCode' in body) input.deviceCode = readOptionalString(body.deviceCode, 'deviceCode') ?? undefined;
  if ('name' in body) input.name = readOptionalString(body.name, 'name');
  if ('mqttTopic' in body) input.mqttTopic = readRequiredString(body.mqttTopic, 'mqttTopic');
  if ('status' in body) input.status = readOptionalDeviceStatus(body.status);
  if ('firmwareVersion' in body) input.firmwareVersion = readOptionalString(body.firmwareVersion, 'firmwareVersion');
  if ('lastSeenAt' in body) input.lastSeenAt = readOptionalIsoDate(body.lastSeenAt, 'lastSeenAt');

  if (
    input.deviceCode === undefined &&
    input.name === undefined &&
    input.mqttTopic === undefined &&
    input.status === undefined &&
    input.firmwareVersion === undefined &&
    input.lastSeenAt === undefined
  ) {
    throw badRequest('At least one device field is required');
  }

  return input;
}
