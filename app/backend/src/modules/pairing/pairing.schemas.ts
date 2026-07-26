import { badRequest } from '../../lib/http-error';

function isObject(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null && !Array.isArray(value);
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

function readOptionalPositiveInteger(value: unknown, field: string, fallback: number): number {
  if (value === undefined) return fallback;
  if (typeof value !== 'number' || !Number.isInteger(value) || value <= 0) {
    throw badRequest(`${field} must be a positive integer`);
  }
  return value;
}

export interface GeneratePairingTokenInput {
  deviceId: string;
  expiresInMinutes: number;
}

export interface ScanPairingTokenInput {
  token: string;
}

export interface UnpairDeviceInput {
  deviceId: string;
}

export function parseGeneratePairingTokenInput(body: unknown): GeneratePairingTokenInput {
  if (!isObject(body)) {
    throw badRequest('Request body must be an object');
  }

  return {
    deviceId: readRequiredString(body.deviceId, 'deviceId'),
    expiresInMinutes: readOptionalPositiveInteger(body.expiresInMinutes, 'expiresInMinutes', 15)
  };
}

export function parseScanPairingTokenInput(body: unknown): ScanPairingTokenInput {
  if (!isObject(body)) {
    throw badRequest('Request body must be an object');
  }

  return {
    token: readRequiredString(body.token, 'token')
  };
}

export function parseUnpairDeviceInput(body: unknown): UnpairDeviceInput {
  if (!isObject(body)) {
    throw badRequest('Request body must be an object');
  }

  return {
    deviceId: readRequiredString(body.deviceId, 'deviceId')
  };
}
