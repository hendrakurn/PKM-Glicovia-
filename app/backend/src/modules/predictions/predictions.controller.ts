import type { NextFunction, Request, Response } from 'express';
import { assertUserId } from '../readings/readings.service';
import { getLatestPredictionResult, getMyLatestPrediction, getMyPredictionTrends, getMyPredictions, getPredictions } from './predictions.service';

function toNumber(value: unknown): number | undefined {
  if (value === undefined || value === null || value === '') return undefined;
  const n = Number(value);
  return Number.isFinite(n) ? n : undefined;
}

export async function listPredictionsController(req: Request, res: Response, next: NextFunction): Promise<void> {
  try {
    const result = await getPredictions({
      limit: toNumber(req.query.limit),
      offset: toNumber(req.query.offset),
      sensorReadingId: typeof req.query.sensor_reading_id === 'string' ? req.query.sensor_reading_id : undefined,
      modelVersionId: typeof req.query.model_version_id === 'string' ? req.query.model_version_id : undefined
    });

    res.json({ data: result });
  } catch (error) {
    next(error);
  }
}

export async function mePredictionsController(req: Request, res: Response, next: NextFunction): Promise<void> {
  try {
    const userId = assertUserId(req.user);
    const result = await getMyPredictions(userId, {
      limit: toNumber(req.query.limit),
      offset: toNumber(req.query.offset),
      deviceId: typeof req.query.device_id === 'string' ? req.query.device_id : undefined,
      sensorReadingId: typeof req.query.sensor_reading_id === 'string' ? req.query.sensor_reading_id : undefined,
      modelVersionId: typeof req.query.model_version_id === 'string' ? req.query.model_version_id : undefined
    });

    res.json({ data: result });
  } catch (error) {
    next(error);
  }
}

export async function latestPredictionController(_req: Request, res: Response, next: NextFunction): Promise<void> {
  try {
    const result = await getLatestPredictionResult();
    if (!result.prediction) {
      res.status(404).json({ message: 'No predictions found' });
      return;
    }

    res.json({ data: result });
  } catch (error) {
    next(error);
  }
}

export async function meLatestPredictionController(req: Request, res: Response, next: NextFunction): Promise<void> {
  try {
    const userId = assertUserId(req.user);
    const result = await getMyLatestPrediction(userId, typeof req.query.device_id === 'string' ? req.query.device_id : undefined);
    if (!result.prediction) {
      res.status(404).json({ message: 'No predictions found' });
      return;
    }

    res.json({ data: result });
  } catch (error) {
    next(error);
  }
}

export async function mePredictionTrendsController(req: Request, res: Response, next: NextFunction): Promise<void> {
  try {
    const userId = assertUserId(req.user);
    const bucket = req.query.bucket === 'week' ? 'week' : 'day';
    const result = await getMyPredictionTrends(userId, {
      deviceId: typeof req.query.device_id === 'string' ? req.query.device_id : undefined,
      from: typeof req.query.from === 'string' ? req.query.from : undefined,
      to: typeof req.query.to === 'string' ? req.query.to : undefined,
      bucket,
      limit: toNumber(req.query.limit)
    });

    res.json({ data: result });
  } catch (error) {
    next(error);
  }
}
