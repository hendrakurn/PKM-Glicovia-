import { Router } from 'express';
import { authMiddleware } from '../../middleware/auth';
import {
  createDeviceController,
  deleteDeviceController,
  getDeviceController,
  listDevicesController,
  updateDeviceController
} from './device.controller';

export const deviceRouter = Router();

deviceRouter.use(authMiddleware);
deviceRouter.get('/', listDevicesController);
deviceRouter.post('/', createDeviceController);
deviceRouter.get('/:deviceId', getDeviceController);
deviceRouter.patch('/:deviceId', updateDeviceController);
deviceRouter.delete('/:deviceId', deleteDeviceController);
