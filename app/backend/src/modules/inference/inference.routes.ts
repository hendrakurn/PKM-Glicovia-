import { Router } from 'express';
import { triggerReadingInferenceController } from './inference.controller';

export const inferenceRouter = Router();

inferenceRouter.post('/readings/:sensorReadingId', triggerReadingInferenceController);
