import type { NextFunction, Request, Response } from 'express';
import { assertUserId, getMyDevices, getMyLatestReading, getMyReadingTrends, getMyReadings } from './readings.service';

function toNumber(value: unknown): number | undefined {
  if (value === undefined || value === null || value === '') return undefined;
  const n = Number(value);
  return Number.isFinite(n) ? n : undefined;
}

export async function meDevicesController(req: Request, res: Response, next: NextFunction): Promise<void> {
  try {
    const userId = assertUserId(req.user);
    const result = await getMyDevices(userId);
    res.json({ data: result });
  } catch (error) {
    next(error);
  }
}

export async function meReadingsController(req: Request, res: Response, next: NextFunction): Promise<void> {
  try {
    const userId = assertUserId(req.user);
    const result = await getMyReadings(userId, {
      deviceId: typeof req.query.device_id === 'string' ? req.query.device_id : undefined,
      from: typeof req.query.from === 'string' ? req.query.from : undefined,
      to: typeof req.query.to === 'string' ? req.query.to : undefined,
      limit: toNumber(req.query.limit),
      offset: toNumber(req.query.offset)
    });
    res.json({ data: result });
  } catch (error) {
    next(error);
  }
}

export async function meLatestReadingController(req: Request, res: Response, next: NextFunction): Promise<void> {
  try {
    const userId = assertUserId(req.user);
    const result = await getMyLatestReading(userId, typeof req.query.device_id === 'string' ? req.query.device_id : undefined);
    if (!result.reading) {
      res.status(404).json({ message: 'No readings found' });
      return;
    }
    res.json({ data: result });
  } catch (error) {
    next(error);
  }
}

export async function meReadingTrendsController(req: Request, res: Response, next: NextFunction): Promise<void> {
  try {
    const userId = assertUserId(req.user);
    const bucket = req.query.bucket === 'day' ? 'day' : 'hour';
    const result = await getMyReadingTrends(userId, {
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
