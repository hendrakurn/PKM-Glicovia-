import type { NextFunction, Request, Response } from 'express';
import { badRequest } from '../../lib/http-error';
import { parseCreateDeviceInput, parseUpdateDeviceInput } from './device.schemas';
import { deviceService } from './device.service';

export async function listDevicesController(_req: Request, res: Response, next: NextFunction): Promise<void> {
  try {
    const devices = await deviceService.listDevices();
    res.status(200).json({ data: devices });
  } catch (error) {
    next(error);
  }
}

function getParamId(value: string | string[] | undefined): string | undefined {
  return typeof value === 'string' ? value : undefined;
}

export async function getDeviceController(req: Request, res: Response, next: NextFunction): Promise<void> {
  try {
    const id = getParamId(req.params.deviceId);
    if (!id) {
      throw badRequest('deviceId is required');
    }
    const device = await deviceService.getDevice(id);
    res.status(200).json({ data: device });
  } catch (error) {
    next(error);
  }
}

export async function createDeviceController(req: Request, res: Response, next: NextFunction): Promise<void> {
  try {
    const input = parseCreateDeviceInput(req.body);
    const device = await deviceService.createDevice(input);
    res.status(201).json({ data: device });
  } catch (error) {
    next(error);
  }
}

export async function updateDeviceController(req: Request, res: Response, next: NextFunction): Promise<void> {
  try {
    const id = getParamId(req.params.deviceId);
    if (!id) {
      throw badRequest('deviceId is required');
    }
    const input = parseUpdateDeviceInput(req.body);
    const device = await deviceService.updateDevice(id, input);
    res.status(200).json({ data: device });
  } catch (error) {
    next(error);
  }
}

export async function deleteDeviceController(req: Request, res: Response, next: NextFunction): Promise<void> {
  try {
    const id = getParamId(req.params.deviceId);
    if (!id) {
      throw badRequest('deviceId is required');
    }
    await deviceService.deleteDevice(id);
    res.status(204).send();
  } catch (error) {
    next(error);
  }
}
