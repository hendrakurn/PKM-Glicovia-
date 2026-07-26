import express = require('express');
import cors = require('cors');
import { errorHandler } from './middleware/error-handler';
import { notFoundHandler } from './middleware/not-found';
import { requestIdMiddleware } from './middleware/request-id';
import { authRoutes } from './modules/auth/auth.routes';
import { deviceRouter } from './modules/devices/device.routes';
import { pairingRouter } from './modules/pairing/pairing.routes';
import { readingsRouter } from './modules/readings/readings.routes';
import { modelsRouter } from './modules/models/models.routes';
import { predictionsRouter } from './modules/predictions/predictions.routes';
import { inferenceRouter } from './modules/inference/inference.routes';

export const app = express();

app.disable('x-powered-by');
app.use(cors({
  origin: ['http://localhost:3000', 'http://localhost:3001', 'http://127.0.0.1:3000', 'http://127.0.0.1:3001'],
  credentials: true,
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'PATCH'],
  allowedHeaders: ['Content-Type', 'Authorization']
}));
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(requestIdMiddleware);

app.get('/health', (_req, res) => {
  res.status(200).json({
    status: 'ok',
    timestamp: new Date().toISOString()
  });
});

app.use('/api/auth', authRoutes);
app.use('/api/devices', deviceRouter);
app.use('/api/pairing', pairingRouter);
app.use('/api/readings', readingsRouter);
app.use('/api/models', modelsRouter);
app.use('/api/predictions', predictionsRouter);
app.use('/api/inference', inferenceRouter);

app.use(notFoundHandler);
app.use(errorHandler);
