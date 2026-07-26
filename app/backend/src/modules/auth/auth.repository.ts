import type { PoolClient } from 'pg';
import { pool } from '../../db/pool';

export type UserRecord = {
  id: string;
  email: string;
  password_hash: string;
  full_name: string | null;
  role: 'subject' | 'admin';
  is_active: boolean;
  last_login_at: Date | null;
  created_at: Date;
  updated_at: Date;
};

export type SubjectRecord = {
  id: string;
  user_id: string;
  subject_code: string;
  display_name: string | null;
  age: number | null;
  sex: string | null;
  notes: string | null;
  created_at: Date;
  updated_at: Date;
};

export type UserProfile = Omit<UserRecord, 'password_hash'>;
export type AuthProfile = {
  user: UserProfile;
  subject: SubjectRecord;
};

type Queryable = Pick<PoolClient, 'query'>;

const USER_COLUMNS = 'id, email, password_hash, full_name, role, is_active, last_login_at, created_at, updated_at';
const SUBJECT_COLUMNS = 'id, user_id, subject_code, display_name, age, sex, notes, created_at, updated_at';

function mapUser(row: Record<string, unknown>): UserRecord {
  return {
    id: String(row.id),
    email: String(row.email),
    password_hash: String(row.password_hash),
    full_name: row.full_name === null ? null : String(row.full_name),
    role: row.role as UserRecord['role'],
    is_active: Boolean(row.is_active),
    last_login_at: row.last_login_at === null ? null : new Date(String(row.last_login_at)),
    created_at: new Date(String(row.created_at)),
    updated_at: new Date(String(row.updated_at))
  };
}

function mapSubject(row: Record<string, unknown>): SubjectRecord {
  return {
    id: String(row.id),
    user_id: String(row.user_id),
    subject_code: String(row.subject_code),
    display_name: row.display_name === null ? null : String(row.display_name),
    age: row.age === null ? null : Number(row.age),
    sex: row.sex === null ? null : String(row.sex),
    notes: row.notes === null ? null : String(row.notes),
    created_at: new Date(String(row.created_at)),
    updated_at: new Date(String(row.updated_at))
  };
}

export function sanitizeUser(user: UserRecord): UserProfile {
  const { password_hash: _passwordHash, ...profile } = user;
  return profile;
}

export async function findUserByEmail(email: string, client: Queryable = pool): Promise<UserRecord | null> {
  const result = await client.query(`SELECT ${USER_COLUMNS} FROM users WHERE email = $1 LIMIT 1`, [email]);
  const row = result.rows[0] as Record<string, unknown> | undefined;
  return row ? mapUser(row) : null;
}

export async function findUserById(id: string, client: Queryable = pool): Promise<UserRecord | null> {
  const result = await client.query(`SELECT ${USER_COLUMNS} FROM users WHERE id = $1 LIMIT 1`, [id]);
  const row = result.rows[0] as Record<string, unknown> | undefined;
  return row ? mapUser(row) : null;
}

export async function findSubjectByUserId(userId: string, client: Queryable = pool): Promise<SubjectRecord | null> {
  const result = await client.query(`SELECT ${SUBJECT_COLUMNS} FROM subjects WHERE user_id = $1 LIMIT 1`, [userId]);
  const row = result.rows[0] as Record<string, unknown> | undefined;
  return row ? mapSubject(row) : null;
}

export async function createUser(
  input: {
    id: string;
    email: string;
    passwordHash: string;
    fullName: string | null;
    role: UserRecord['role'];
    isActive: boolean;
    createdAt: Date;
    updatedAt: Date;
  },
  client: Queryable
): Promise<UserRecord> {
  const result = await client.query(
    `
      INSERT INTO users (
        id,
        email,
        password_hash,
        full_name,
        role,
        is_active,
        created_at,
        updated_at
      )
      VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
      RETURNING ${USER_COLUMNS}
    `,
    [
      input.id,
      input.email,
      input.passwordHash,
      input.fullName,
      input.role,
      input.isActive,
      input.createdAt,
      input.updatedAt
    ]
  );

  return mapUser(result.rows[0] as Record<string, unknown>);
}

export async function createSubject(
  input: {
    id: string;
    userId: string;
    subjectCode: string;
    displayName: string | null;
    age: number | null;
    sex: string | null;
    notes: string | null;
    createdAt: Date;
    updatedAt: Date;
  },
  client: Queryable
): Promise<SubjectRecord> {
  const result = await client.query(
    `
      INSERT INTO subjects (
        id,
        user_id,
        subject_code,
        display_name,
        age,
        sex,
        notes,
        created_at,
        updated_at
      )
      VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
      RETURNING ${SUBJECT_COLUMNS}
    `,
    [
      input.id,
      input.userId,
      input.subjectCode,
      input.displayName,
      input.age,
      input.sex,
      input.notes,
      input.createdAt,
      input.updatedAt
    ]
  );

  return mapSubject(result.rows[0] as Record<string, unknown>);
}

export async function updateLastLoginAt(userId: string, lastLoginAt: Date, client: Queryable = pool): Promise<UserRecord | null> {
  const result = await client.query(
    `
      UPDATE users
      SET last_login_at = $2,
          updated_at = $2
      WHERE id = $1
      RETURNING ${USER_COLUMNS}
    `,
    [userId, lastLoginAt]
  );

  const row = result.rows[0] as Record<string, unknown> | undefined;
  return row ? mapUser(row) : null;
}

export async function findAuthProfileByUserId(userId: string, client: Queryable = pool): Promise<AuthProfile | null> {
  const user = await findUserById(userId, client);
  if (!user) {
    return null;
  }

  const subject = await findSubjectByUserId(userId, client);
  if (!subject) {
    return null;
  }

  return {
    user: sanitizeUser(user),
    subject
  };
}
