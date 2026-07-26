import { env } from './config/env';
import { logger } from './config/logger';
import { app } from './app';
import { startMqttClient } from './mqtt';

async function bootstrap(): Promise<void> {
  await startMqttClient();

  app.listen(env.PORT, env.HOST, () => {
    logger.info(`Server listening on http://${env.HOST}:${env.PORT}`);
  });
}

void bootstrap().catch((error) => {
  logger.error('Failed to bootstrap server', error);
  process.exit(1);
});
