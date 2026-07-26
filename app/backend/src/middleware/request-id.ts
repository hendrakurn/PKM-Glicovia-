import { randomUUID } from 'crypto';
import type { NextFunction, Response } from 'express';
import type { RequestWithRequestId } from '../types/request';

export function requestIdMiddleware(req: RequestWithRequestId, _res: Response, next: NextFunction): void {
  req.requestId = randomUUID();
  next();
}
