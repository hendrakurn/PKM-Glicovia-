import { Pool } from 'pg';
import { pool } from '../../db/pool';
import { conflict, notFound } from '../../lib/http-error';
import { withTransaction } from '../../lib/transaction';
import * as deviceRepo from './device.repository';
import type { CreateDeviceInput, UpdateDeviceInput } from './device.types';

function translateDbError(error: unknown): never {
  if (error && typeof error === 'object' && 'code' in error) {
    const code = String((error as { code: unknown }).code);
    if (code === '23505') {
      throw conflict('A device with the same unique field already exists');
    }
    if (code === '23503') {
      throw conflict('Device has dependent records and cannot be removed');
    }
  }

  throw error as never;
}

export function createDeviceService(database: Pool = pool) {
  return {
    async listDevices() {
      return deviceRepo.listDevices();
    },

    async getDevice(id: string) {
      const device = await deviceRepo.getDeviceById(id);
      if (!device) {
        throw notFound('Device not found');
      }
      return device;
    },

    async createDevice(input: CreateDeviceInput) {
      try {
        return await deviceRepo.createDevice(input);
      } catch (error) {
        translateDbError(error);
      }
    },

    async updateDevice(id: string, input: UpdateDeviceInput) {
      try {
        const device = await deviceRepo.updateDevice(id, input);
        if (!device) {
          throw notFound('Device not found');
        }
        return device;
      } catch (error) {
        translateDbError(error);
      }
    },

    async deleteDevice(id: string) {
      try {
        const deleted = await deviceRepo.deleteDevice(id);
        if (!deleted) {
          throw notFound('Device not found');
        }
      } catch (error) {
        translateDbError(error);
      }
    },

    async updateDeviceStatus(id: string, status: CreateDeviceInput['status'] | NonNullable<UpdateDeviceInput['status']>) {
      return withTransaction(database, async (client) => {
        const device = await deviceRepo.getDeviceByIdForUpdate(client, id);
        if (!device) {
          throw notFound('Device not found');
        }

        await deviceRepo.updateDeviceStatus(client, id, status ?? 'unpaired');
        return deviceRepo.getDeviceById(id);
      });
    }
  };
}

export const deviceService = createDeviceService();
