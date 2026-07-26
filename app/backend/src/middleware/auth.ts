import type { NextFunction, Request, Response } from 'express';
import { pool } from '../db/pool';
import { env } from '../config/env';
import { badRequest, unauthorized } from '../lib/http-error';
import { verifyHs256Jwt } from '../lib/jwt';

type AuthenticatedRequest = Request & {
  user?: {
    id: string;
    email?: string;
    roles?: string[];
  };
  subject?: {
    id: string;
    userId: string;
    subjectCode: string;
    displayName?: string | null;
    age?: number | null;
    sex?: string | null;
    notes?: string | null;
  };
};

interface AuthenticatedUser {
  id: string;
  email?: string;
  roles?: string[];
}

interface AuthenticatedSubject {
  id: string;
  userId: string;
  subjectCode: string;
  displayName?: string | null;
  age?: number | null;
  sex?: string | null;
  notes?: string | null;
}

interface SubjectLookupRow {
  subject_id: string;
  subject_user_id: string;
  subject_code: string;
  subject_display_name: string | null;
  subject_age: number | null;
  subject_sex: string | null;
  subject_notes: string | null;
  user_id: string;
  user_email: string;
  user_role: string;
  user_is_active: boolean;
}

interface UserLookupRow {
  user_id: string;
  user_email: string;
  user_role: string;
  user_is_active: boolean;
  subject_id: string | null;
  subject_user_id: string | null;
  subject_code: string | null;
  subject_display_name: string | null;
  subject_age: number | null;
  subject_sex: string | null;
  subject_notes: string | null;
}

async function resolveIdentityFromClaims(token: string): Promise<{ user: AuthenticatedUser; subject?: AuthenticatedSubject }> {
  const payload = verifyHs256Jwt(token, env.JWT_SECRET);
  const candidates = [payload.subjectId, payload.userId, payload.sub].filter((value): value is string => typeof value === 'string' && value.length > 0);

  if (candidates.length === 0) {
    throw unauthorized('JWT subject is missing');
  }

  for (const candidate of candidates) {
    const subjectResult = await pool.query<SubjectLookupRow>(
      `SELECT
         s.id AS subject_id,
         s.user_id AS subject_user_id,
         s.subject_code,
         s.display_name AS subject_display_name,
         s.age AS subject_age,
         s.sex AS subject_sex,
         s.notes AS subject_notes,
         u.id AS user_id,
         u.email AS user_email,
         u.role AS user_role,
         u.is_active AS user_is_active
       FROM subjects s
       INNER JOIN users u ON u.id = s.user_id
       WHERE s.id = $1`,
      [candidate]
    );

    if (subjectResult.rows.length > 0) {
      const row = subjectResult.rows[0];
      if (!row.user_is_active) {
        throw unauthorized('User account is inactive');
      }

      return {
        user: {
          id: row.user_id,
          email: row.user_email,
          roles: [row.user_role]
        },
        subject: {
          id: row.subject_id,
          userId: row.subject_user_id,
          subjectCode: row.subject_code,
          displayName: row.subject_display_name,
          age: row.subject_age,
          sex: row.subject_sex,
          notes: row.subject_notes
        }
      };
    }

    const userResult = await pool.query<UserLookupRow>(
      `SELECT
         u.id AS user_id,
         u.email AS user_email,
         u.role AS user_role,
         u.is_active AS user_is_active,
         s.id AS subject_id,
         s.user_id AS subject_user_id,
         s.subject_code,
         s.display_name AS subject_display_name,
         s.age AS subject_age,
         s.sex AS subject_sex,
         s.notes AS subject_notes
       FROM users u
       LEFT JOIN subjects s ON s.user_id = u.id
       WHERE u.id = $1`,
      [candidate]
    );

    if (userResult.rows.length > 0) {
      const row = userResult.rows[0];
      if (!row.user_is_active) {
        throw unauthorized('User account is inactive');
      }

      return {
        user: {
          id: row.user_id,
          email: row.user_email,
          roles: [row.user_role]
        },
        subject: row.subject_id
          ? {
              id: row.subject_id,
              userId: row.subject_user_id ?? row.user_id,
              subjectCode: row.subject_code ?? '',
              displayName: row.subject_display_name,
              age: row.subject_age,
              sex: row.subject_sex,
              notes: row.subject_notes
            }
          : undefined
      };
    }
  }

  throw unauthorized('Invalid authentication subject');
}

export function authMiddleware(req: AuthenticatedRequest, _res: Response, next: NextFunction): void {
  const authorization = req.headers.authorization;
  if (!authorization) {
    next(unauthorized('Missing authorization header'));
    return;
  }

  const [scheme, token] = authorization.split(' ');
  if (scheme !== 'Bearer' || !token) {
    next(badRequest('Authorization header must use Bearer token'));
    return;
  }

  void resolveIdentityFromClaims(token)
    .then(({ user, subject }) => {
      req.user = user;
      if (subject) {
        req.subject = subject;
      }
      next();
    })
    .catch((error: unknown) => {
      if (error instanceof Error && error.name === 'SyntaxError') {
        next(unauthorized('Malformed JWT payload'));
        return;
      }
      next(error);
    });
}

export function requireSubjectMiddleware(req: AuthenticatedRequest, _res: Response, next: NextFunction): void {
  if (!req.subject) {
    next(unauthorized('Subject identity is required for this route'));
    return;
  }

  next();
}
