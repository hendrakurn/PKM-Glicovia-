import type { Request } from 'express';

export type RequestWithRequestId = Request & {
  requestId?: string;
};

export type AuthenticatedUser = {
  id: string;
  email?: string;
  roles?: string[];
};

export type AuthenticatedSubject = {
  id: string;
  userId: string;
  subjectCode: string;
  displayName?: string | null;
  age?: number | null;
  sex?: string | null;
  notes?: string | null;
};

export type AuthenticatedRequest = Request & {
  requestId?: string;
  user?: AuthenticatedUser;
  subject?: AuthenticatedSubject;
};
