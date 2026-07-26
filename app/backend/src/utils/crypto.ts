import { createHash, randomBytes } from 'crypto';

export function hashSha256(value: string): string {
  return createHash('sha256').update(value).digest('hex');
}

export function generateToken(bytes = 32): string {
  return randomBytes(bytes).toString('hex');
}
