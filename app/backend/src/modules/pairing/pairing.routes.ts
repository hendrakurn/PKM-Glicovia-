import { Router } from 'express';
import { authMiddleware, requireSubjectMiddleware } from '../../middleware/auth';
import {
  generatePairingTokenController,
  scanPairingTokenController,
  unpairDeviceController
} from './pairing.controller';

export const pairingRouter = Router();

pairingRouter.use(authMiddleware);
pairingRouter.post('/tokens', generatePairingTokenController);
pairingRouter.post('/scan', requireSubjectMiddleware, scanPairingTokenController);
pairingRouter.post('/unpair', requireSubjectMiddleware, unpairDeviceController);
