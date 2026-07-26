import type { NextFunction, Request, Response } from 'express';
import { badRequest, unauthorized } from '../../lib/http-error';
import { parseGeneratePairingTokenInput, parseScanPairingTokenInput, parseUnpairDeviceInput } from './pairing.schemas';
import { pairingService } from './pairing.service';

export async function generatePairingTokenController(req: Request, res: Response, next: NextFunction): Promise<void> {
  try {
    const input = parseGeneratePairingTokenInput(req.body);
    const result = await pairingService.generatePairingToken(input);
    res.status(201).json({ data: result });
  } catch (error) {
    next(error);
  }
}

export async function scanPairingTokenController(req: Request, res: Response, next: NextFunction): Promise<void> {
  try {
    const subjectId = req.subject?.id;
    if (!subjectId) {
      throw unauthorized('Subject identity is required');
    }
    const input = parseScanPairingTokenInput(req.body);
    const result = await pairingService.scanPairingToken(input, subjectId);
    res.status(201).json({ data: result });
  } catch (error) {
    next(error);
  }
}

export async function unpairDeviceController(req: Request, res: Response, next: NextFunction): Promise<void> {
  try {
    const subjectId = req.subject?.id;
    if (!subjectId) {
      throw unauthorized('Subject identity is required');
    }
    const input = parseUnpairDeviceInput(req.body);
    const result = await pairingService.unpairDevice(input.deviceId, subjectId);
    res.status(200).json({ data: result });
  } catch (error) {
    next(error);
  }
}
