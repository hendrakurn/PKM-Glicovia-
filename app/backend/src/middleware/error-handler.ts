import type { NextFunction, Request, Response } from 'express';
import { ZodError } from 'zod';
import { logger } from '../config/logger';

function getStatusCode(err: unknown): number {
  if (typeof err === 'object' && err !== null && 'statusCode' in err) {
    const value = (err as { statusCode?: unknown }).statusCode;
    if (typeof value === 'number' && Number.isFinite(value)) {
      return value;
    }
  }

  return 500;
}

function getMessage(err: unknown): string {
  if (err instanceof ZodError) {
    return 'Validation error';
  }

  if (err instanceof Error && err.message) {
    return err.message;
  }

  return 'Internal server error';
}

export function errorHandler(err: unknown, _req: Request, res: Response, _next: NextFunction): void {
  logger.error('Unhandled error', err);

  if (res.headersSent) {
    return;
  }

  if (err instanceof ZodError) {
    res.status(400).json({
      message: 'Validation error',
      errors: err.issues
    });
    return;
  }

  const statusCode = getStatusCode(err);
  const message = getMessage(err);

  res.status(statusCode).json({
    message
  });
}
