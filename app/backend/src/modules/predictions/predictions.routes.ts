import { Router } from 'express';
import { authMiddleware } from '../../middleware/auth';
import {
  latestPredictionController,
  listPredictionsController,
  meLatestPredictionController,
  mePredictionTrendsController,
  mePredictionsController
} from './predictions.controller';

export const predictionsRouter = Router();

predictionsRouter.use('/me', authMiddleware);
predictionsRouter.get('/me', mePredictionsController);
predictionsRouter.get('/me/latest', meLatestPredictionController);
predictionsRouter.get('/me/trends', mePredictionTrendsController);
predictionsRouter.get('/latest', latestPredictionController);
predictionsRouter.get('/', listPredictionsController);
