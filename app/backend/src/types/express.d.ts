declare global {
  namespace Express {
    interface User {
      id: string;
      email?: string;
      roles?: string[];
    }

    interface Subject {
      id: string;
      userId: string;
      subjectCode: string;
      displayName?: string | null;
      age?: number | null;
      sex?: string | null;
      notes?: string | null;
    }
  }
}

declare module 'express-serve-static-core' {
  interface Request {
    requestId?: string;
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
  }
}

export {};
