import type { NextFunction, Request, Response } from 'express';
import { addModelVersion, getModels } from './models.service';

export async function listModelsController(_req: Request, res: Response, next: NextFunction): Promise<void> {
  try {
    const result = await getModels();
    res.json({ data: result });
  } catch (error) {
    next(error);
  }
}

export async function createModelController(req: Request, res: Response, next: NextFunction): Promise<void> {
  try {
    const body = req.body ?? {};
    if (typeof body.model_name !== 'string' || typeof body.version !== 'string') {
      res.status(400).json({ message: 'model_name and version are required' });
      return;
    }

    const result = await addModelVersion({
      modelName: body.model_name,
      version: body.version,
      status: body.status === 'deployed' || body.status === 'archived' ? body.status : 'training',
      artifactUrl: typeof body.artifact_url === 'string' ? body.artifact_url : null,
      trainedAt: typeof body.trained_at === 'string' ? body.trained_at : null,
      deployedAt: typeof body.deployed_at === 'string' ? body.deployed_at : null,
      notes: typeof body.notes === 'string' ? body.notes : null
    });

    res.status(201).json({ data: result });
  } catch (error) {
    next(error);
  }
}
