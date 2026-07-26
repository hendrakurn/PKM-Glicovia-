import type { NextFunction, Request, Response } from 'express';
import { runInferenceForSensorReadingId } from './inference.service';

export async function triggerReadingInferenceController(req: Request, res: Response, next: NextFunction): Promise<void> {
  try {
    const rawSensorReadingId = req.params.sensorReadingId;
    const sensorReadingId = Array.isArray(rawSensorReadingId) ? rawSensorReadingId[0] : rawSensorReadingId;
    if (!sensorReadingId) {
      res.status(400).json({ message: 'sensorReadingId is required' });
      return;
    }

    const result = await runInferenceForSensorReadingId(sensorReadingId);
    res.status(201).json({ data: result });
  } catch (error) {
    next(error);
  }
}
