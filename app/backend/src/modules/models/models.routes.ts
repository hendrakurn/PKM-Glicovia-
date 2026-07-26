import { Router } from 'express';
import { createModelController, listModelsController } from './models.controller';

export const modelsRouter = Router();

modelsRouter.get('/', listModelsController);
modelsRouter.post('/', createModelController);
