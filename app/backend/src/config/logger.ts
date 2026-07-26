type LogLevel = 'debug' | 'info' | 'warn' | 'error';

function write(level: LogLevel, message: string, meta?: unknown): void {
  const payload = meta === undefined ? '' : ` ${JSON.stringify(meta)}`;
  // eslint-disable-next-line no-console
  console.log(`[${level.toUpperCase()}] ${message}${payload}`);
}

export const logger = {
  debug: (message: string, meta?: unknown) => write('debug', message, meta),
  info: (message: string, meta?: unknown) => write('info', message, meta),
  warn: (message: string, meta?: unknown) => write('warn', message, meta),
  error: (message: string, meta?: unknown) => write('error', message, meta)
};
