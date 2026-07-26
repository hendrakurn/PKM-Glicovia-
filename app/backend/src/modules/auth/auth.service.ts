import * as bcrypt from 'bcryptjs';
import * as jwt from 'jsonwebtoken';
import { env } from '../../config/env';
import { pool } from '../../db/pool';
import { createId } from '../../utils/ids';
import {
  createSubject,
  createUser,
  findAuthProfileByUserId,
  findSubjectByUserId,
  findUserByEmail,
  sanitizeUser,
  updateLastLoginAt,
  type AuthProfile,
  type SubjectRecord,
  type UserProfile
} from './auth.repository';
import type { LoginInput, RegisterInput } from './auth.schema';

export type AuthTokens = {
  accessToken: string;
  tokenType: 'Bearer';
};

export type AuthResponse = AuthProfile & AuthTokens;

export class AppError extends Error {
  statusCode: number;

  constructor(statusCode: number, message: string) {
    super(message);
    this.name = 'AppError';
    this.statusCode = statusCode;
  }
}

function makeSubjectCode(userId: string): string {
  return `SUB-${userId.replace(/-/g, '').toUpperCase()}`;
}

function signToken(payload: { userId: string; email: string; role: string }): string {
  return jwt.sign(payload, env.JWT_SECRET, {
    expiresIn: env.JWT_EXPIRES_IN
  } as jwt.SignOptions);
}

function toAuthResponse(user: UserProfile, subject: SubjectRecord): AuthProfile {
  return { user, subject };
}

export async function register(input: RegisterInput): Promise<AuthResponse> {
  const existingUser = await findUserByEmail(input.email);
  if (existingUser) {
    throw new AppError(409, 'Email already registered');
  }

  const client = await pool.connect();
  const now = new Date();

  try {
    await client.query('BEGIN');

    const userId = createId();
    const subjectId = createId();
    const user = await createUser(
      {
        id: userId,
        email: input.email,
        passwordHash: await bcrypt.hash(input.password, 12),
        fullName: input.fullName ?? null,
        role: 'subject',
        isActive: true,
        createdAt: now,
        updatedAt: now
      },
      client
    );

    const subject = await createSubject(
      {
        id: subjectId,
        userId: user.id,
        subjectCode: makeSubjectCode(user.id),
        displayName: input.fullName ?? input.email,
        age: null,
        sex: null,
        notes: null,
        createdAt: now,
        updatedAt: now
      },
      client
    );

    await client.query('COMMIT');

    return {
      ...toAuthResponse(sanitizeUser(user), subject),
      accessToken: signToken({ userId: user.id, email: user.email, role: user.role }),
      tokenType: 'Bearer'
    };
  } catch (error) {
    await client.query('ROLLBACK');

    if (typeof error === 'object' && error !== null && 'code' in error && (error as { code?: string }).code === '23505') {
      throw new AppError(409, 'Email already registered');
    }

    throw error;
  } finally {
    client.release();
  }
}

export async function login(input: LoginInput): Promise<AuthResponse> {
  const user = await findUserByEmail(input.email);
  if (!user || !user.is_active) {
    throw new AppError(401, 'Invalid email or password');
  }

  const isPasswordValid = await bcrypt.compare(input.password, user.password_hash);
  if (!isPasswordValid) {
    throw new AppError(401, 'Invalid email or password');
  }

  const now = new Date();
  const updatedUser = await updateLastLoginAt(user.id, now);
  const subject = await findSubjectByUserId(user.id);

  if (!updatedUser || !subject) {
    throw new AppError(404, 'User profile not found');
  }

  return {
    user: sanitizeUser(updatedUser),
    subject,
    accessToken: signToken({ userId: updatedUser.id, email: updatedUser.email, role: updatedUser.role }),
    tokenType: 'Bearer'
  };
}

export async function me(userId: string): Promise<AuthProfile> {
  const profile = await findAuthProfileByUserId(userId);
  if (!profile) {
    throw new AppError(404, 'User profile not found');
  }

  return profile;
}
