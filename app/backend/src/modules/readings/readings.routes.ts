import { Router } from 'express';
import { authMiddleware } from '../../middleware/auth';
import { meDevicesController, meLatestReadingController, meReadingTrendsController, meReadingsController } from './readings.controller';

export const readingsRouter = Router();

readingsRouter.use('/me', authMiddleware);
readingsRouter.get('/me/devices', meDevicesController);
readingsRouter.get('/me/readings', meReadingsController);
readingsRouter.get('/me/readings/latest', meLatestReadingController);
readingsRouter.get('/me/readings/trends', meReadingTrendsController);
