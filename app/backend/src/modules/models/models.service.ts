import { randomUUID } from 'crypto';
import { createModelVersion, listModelVersions } from './models.repository';

export async function getModels() {
  const models = await listModelVersions();
  return { models };
}

export async function addModelVersion(input: {
  modelName: string;
  version: string;
  status?: 'training' | 'deployed' | 'archived';
  artifactUrl?: string | null;
  trainedAt?: string | null;
  deployedAt?: string | null;
  notes?: string | null;
}) {
  const row = await createModelVersion({
    id: randomUUID(),
    modelName: input.modelName,
    version: input.version,
    status: input.status ?? 'training',
    artifactUrl: input.artifactUrl,
    trainedAt: input.trainedAt,
    deployedAt: input.deployedAt,
    notes: input.notes
  });

  return { model: row };
}
