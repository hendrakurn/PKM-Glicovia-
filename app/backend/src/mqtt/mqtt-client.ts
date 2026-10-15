import mqtt, { type MqttClient, type IClientOptions } from 'mqtt';
import { env } from '../config/env';
import { logger } from '../config/logger';
import { handleMqttMessage } from './mqtt-handler';

let client: MqttClient | null = null;

function buildSubscribeTopic(): string {
  const prefix = env.MQTT_TOPIC_PREFIX.trim();
  return prefix ? `${prefix}/devices/+/readings` : 'devices/+/readings';
}

function buildOptions(): IClientOptions {
  return {
    clientId: env.MQTT_CLIENT_ID,
    username: env.MQTT_USERNAME,
    password: env.MQTT_PASSWORD ? Buffer.from(env.MQTT_PASSWORD) : undefined,
    reconnectPeriod: 5_000,
    clean: true
  };
}

export async function startMqttClient(): Promise<MqttClient | null> {
  if (!env.MQTT_URL) {
    logger.info('MQTT is disabled because MQTT_URL is not configured');
    return null;
  }

  if (client) {
    return client;
  }

  client = mqtt.connect(env.MQTT_URL, buildOptions());

  client.on('connect', () => {
    const subscription = buildSubscribeTopic();
    client?.subscribe(subscription, (error) => {
      if (error) {
        logger.error('Failed to subscribe to MQTT topic', error);
        return;
      }
      logger.info('MQTT subscribed', { subscription });
    });
  });

  client.on('message', (topic, payload) => {
    void handleMqttMessage(topic, payload).catch((error) => {
      logger.error('Failed to handle MQTT message', error);
    });
  });

  client.on('error', (error) => {
    logger.error('MQTT client error', error);
  });

  client.on('close', () => {
    logger.warn('MQTT connection closed');
  });

  return client;
}

export async function stopMqttClient(): Promise<void> {
  if (!client) return;

  const current = client;
  client = null;

  await new Promise<void>((resolve) => {
    current.end(false, {}, () => resolve());
  });
}

export function publishMqttMessage(topic: string, payload: string): Promise<boolean> {
  return new Promise((resolve) => {
    if (!client || !client.connected) {
      logger.warn('MQTT client not connected; cannot publish message', { topic });
      return resolve(false);
    }
    client.publish(topic, payload, { qos: 0 }, (error) => {
      if (error) {
        logger.error('Failed to publish MQTT message', { topic, error });
        return resolve(false);
      }
      resolve(true);
    });
  });
}

