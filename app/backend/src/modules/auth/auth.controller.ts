import type { NextFunction, Request, Response } from 'express';
import { AppError, login, me, register } from './auth.service';
import { loginSchema, registerSchema } from './auth.schema';

export async function registerController(req: Request, res: Response, next: NextFunction): Promise<void> {
  try {
    const payload = registerSchema.parse(req.body);
    const result = await register(payload);
    res.status(201).json(result);
  } catch (error) {
    next(error);
  }
}

export async function loginController(req: Request, res: Response, next: NextFunction): Promise<void> {
  try {
    const payload = loginSchema.parse(req.body);
    const result = await login(payload);
    res.status(200).json(result);
  } catch (error) {
    next(error);
  }
}

export async function meController(req: Request, res: Response, next: NextFunction): Promise<void> {
  try {
    const userId = req.user?.id;
    if (!userId) {
      throw new AppError(401, 'Unauthorized');
    }

    const result = await me(userId);
    res.status(200).json(result);
  } catch (error) {
    next(error);
  }
}
