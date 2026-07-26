import { randomBytes } from 'crypto';
import type { Pool } from 'pg';
import { pool } from '../../db/pool';
import { conflict, gone, notFound, forbidden } from '../../lib/http-error';
import { withTransaction } from '../../lib/transaction';
import * as deviceRepo from '../devices/device.repository';
import { deviceService } from '../devices/device.service';
import * as pairingRepo from './pairing.repository';
import type { GeneratePairingTokenInput } from './pairing.schemas';

function generateUniqueToken(): string {
  return randomBytes(32).toString('hex');
}

function buildQrPayload(input: { token: string; deviceId: string; deviceCode: string; expiresAt: string }): string {
  return JSON.stringify({
    kind: 'pkmglico-device-pairing',
    ...input
  });
}

function isPgError(error: unknown, code: string): boolean {
  return Boolean(error && typeof error === 'object' && 'code' in error && String((error as { code: unknown }).code) === code);
}

export function createPairingService(database: Pool = pool) {
  return {
    async generatePairingToken(input: GeneratePairingTokenInput) {
      const device = await deviceService.getDevice(input.deviceId);
      const expiresAt = new Date(Date.now() + input.expiresInMinutes * 60_000);

      return withTransaction(database, async (client) => {
        await client.query('SELECT id FROM devices WHERE id = $1 FOR UPDATE', [device.id]);
        await pairingRepo.revokePendingTokensForDevice(client, device.id);

        let lastError: unknown;
        for (let attempt = 0; attempt < 5; attempt += 1) {
          const token = generateUniqueToken();
          const qrPayload = buildQrPayload({
            token,
            deviceId: device.id,
            deviceCode: device.device_code,
            expiresAt: expiresAt.toISOString()
          });

          try {
            const pairingToken = await pairingRepo.insertPairingToken(client, {
              deviceId: device.id,
              token,
              qrPayload,
              expiresAt
            });

            return {
              device,
              pairingToken
            };
          } catch (error) {
            lastError = error;
            if (!isPgError(error, '23505')) {
              throw error;
            }
          }
        }

        throw lastError instanceof Error ? lastError : conflict('Unable to generate a unique pairing token');
      });
    },

    async scanPairingToken(input: { token: string }, subjectId: string) {
      return withTransaction(database, async (client) => {
        const subjectRow = await client.query<{ id: string }>('SELECT id FROM subjects WHERE id = $1 FOR UPDATE', [subjectId]);
        if (subjectRow.rows.length === 0) {
          throw notFound('Subject not found');
        }

        const token = await pairingRepo.findPairingTokenForUpdate(client, input.token);
        if (!token) {
          throw notFound('Pairing token not found');
        }

        const now = new Date();
        const expiresAt = new Date(token.expires_at);
        if (expiresAt.getTime() <= now.getTime()) {
          await pairingRepo.markPairingTokenExpired(client, token.id);
          throw gone('Pairing token has expired');
        }

        if (token.status === 'used') {
          throw conflict('Pairing token has already been used');
        }
        if (token.status === 'revoked') {
          throw conflict('Pairing token was revoked');
        }
        if (token.status !== 'pending') {
          throw conflict('Pairing token is not pending');
        }

        const device = await deviceRepo.getDeviceByIdForUpdate(client, token.device_id);
        if (!device) {
          throw notFound('Device not found');
        }

        await client.query('SELECT id FROM devices WHERE id = $1 FOR UPDATE', [device.id]);
        await client.query('SELECT id FROM subjects WHERE id = $1 FOR UPDATE', [subjectId]);

        const activeForDevice = await pairingRepo.getActiveAssignmentForDeviceForUpdate(client, device.id);
        if (activeForDevice) {
          throw conflict('Device already has an active assignment');
        }

        const activeForSubject = await pairingRepo.getActiveAssignmentForSubjectForUpdate(client, subjectId);
        if (activeForSubject) {
          throw conflict('Subject already has an active device assignment');
        }

        const assignment = await pairingRepo.createDeviceAssignment(client, {
          deviceId: device.id,
          subjectId,
          pairingTokenId: token.id
        });

        await pairingRepo.markPairingTokenUsed(client, token.id);
        await pairingRepo.updateDeviceStatus(client, device.id, 'paired');

        return {
          device: await deviceRepo.getDeviceById(device.id),
          pairingToken: token,
          assignment
        };
      });
    },

    async unpairDevice(deviceId: string, subjectId: string) {
      return withTransaction(database, async (client) => {
        const device = await deviceRepo.getDeviceByIdForUpdate(client, deviceId);
        if (!device) {
          throw notFound('Device not found');
        }

        const activeAssignment = await pairingRepo.getActiveAssignmentForDeviceForUpdate(client, deviceId);
        if (!activeAssignment) {
          throw notFound('No active assignment found for this device');
        }

        if (activeAssignment.subject_id !== subjectId) {
          throw forbidden('You are not allowed to unpair this device');
        }

        await pairingRepo.endActiveAssignment(client, activeAssignment.id);
        await pairingRepo.updateDeviceStatus(client, deviceId, 'unpaired');

        return {
          device: await deviceRepo.getDeviceById(deviceId),
          assignment: activeAssignment
        };
      });
    }
  };
}

export const pairingService = createPairingService();
