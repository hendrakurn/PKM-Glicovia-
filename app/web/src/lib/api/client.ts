import type {
  ApiEnvelope,
  AuthProfile,
  AuthResponse,
  CreateDeviceInput,
  DeviceAssignmentRecord,
  DeviceRecord,
  DeviceWithAssignment,
  HealthResponse,
  ModelVersionRow,
  PairingTokenRecord,
  PredictionResultRow,
  ReadingTrendRow,
  SensorReadingRow,
  SubjectDeviceRow,
  SubjectRecord,
  UpdateDeviceInput,
} from "./types";

export const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:5000";

type QueryValue = string | number | boolean | null | undefined;
type RequestOptions = {
  method?: "GET" | "POST" | "PATCH" | "DELETE";
  token?: string | null;
  body?: unknown;
  query?: Record<string, QueryValue>;
  signal?: AbortSignal;
};

export class ApiError extends Error {
  status: number;
  payload: unknown;

  constructor(status: number, message: string, payload?: unknown) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.payload = payload;
  }
}

function buildUrl(path: string, query?: Record<string, QueryValue>) {
  const base = API_BASE_URL.endsWith("/") ? API_BASE_URL.slice(0, -1) : API_BASE_URL;
  const url = new URL(`${base}${path}`);
  Object.entries(query ?? {}).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== "") {
      url.searchParams.set(key, String(value));
    }
  });
  return url.toString();
}

async function readPayload(response: Response) {
  const text = await response.text();
  if (!text) return undefined;
  try {
    return JSON.parse(text) as unknown;
  } catch {
    return text;
  }
}

function messageFromPayload(payload: unknown, fallback: string) {
  if (payload && typeof payload === "object" && "message" in payload) {
    const message = (payload as { message?: unknown }).message;
    if (typeof message === "string" && message.trim()) return message;
  }
  return fallback;
}

async function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const headers = new Headers();
  if (options.body !== undefined) headers.set("Content-Type", "application/json");
  if (options.token) headers.set("Authorization", `Bearer ${options.token}`);

  const response = await fetch(buildUrl(path, options.query), {
    method: options.method ?? "GET",
    headers,
    body: options.body === undefined ? undefined : JSON.stringify(options.body),
    cache: "no-store",
    signal: options.signal,
  });

  const payload = await readPayload(response);
  if (!response.ok) {
    if (response.status === 401 && typeof window !== "undefined") {
      window.dispatchEvent(new Event("glicovia:unauthorized"));
    }
    throw new ApiError(response.status, messageFromPayload(payload, `Request failed with status ${response.status}`), payload);
  }

  return payload as T;
}

export const api = {
  health: () => request<HealthResponse>("/health"),
  register: (body: { email: string; password: string; fullName?: string }) =>
    request<AuthResponse>("/api/auth/register", { method: "POST", body }),
  login: (body: { email: string; password: string }) =>
    request<AuthResponse>("/api/auth/login", { method: "POST", body }),
  me: (token: string) => request<AuthProfile>("/api/auth/me", { token }),
  listDevices: (token?: string | null) =>
    request<ApiEnvelope<DeviceWithAssignment[]>>("/api/devices", { token }).then((response) => response.data),
  createDevice: (body: CreateDeviceInput, token?: string | null) =>
    request<ApiEnvelope<DeviceRecord>>("/api/devices", { method: "POST", token, body }).then((response) => response.data),
  getDevice: (deviceId: string, token?: string | null) =>
    request<ApiEnvelope<DeviceWithAssignment>>(`/api/devices/${deviceId}`, { token }).then((response) => response.data),
  updateDevice: (deviceId: string, body: UpdateDeviceInput, token?: string | null) =>
    request<ApiEnvelope<DeviceRecord>>(`/api/devices/${deviceId}`, { method: "PATCH", token, body }).then((response) => response.data),
  deleteDevice: async (deviceId: string, token?: string | null) => {
    await request<void>(`/api/devices/${deviceId}`, { method: "DELETE", token });
  },
  createPairingToken: (body: { deviceId: string; expiresInMinutes?: number }, token?: string | null) =>
    request<ApiEnvelope<{ device: DeviceRecord; pairingToken: PairingTokenRecord }>>("/api/pairing/tokens", {
      method: "POST",
      token,
      body,
    }).then((response) => response.data),
  scanPairingToken: (body: { token: string }, token: string) =>
    request<ApiEnvelope<{ device: DeviceRecord; pairingToken: PairingTokenRecord; assignment: DeviceAssignmentRecord }>>(
      "/api/pairing/scan",
      { method: "POST", token, body }
    ).then((response) => response.data),
  unpairDevice: (body: { deviceId: string }, token: string) =>
    request<ApiEnvelope<{ device: DeviceRecord; assignment: DeviceAssignmentRecord }>>("/api/pairing/unpair", {
      method: "POST",
      token,
      body,
    }).then((response) => response.data),
  myDevices: (token: string) =>
    request<ApiEnvelope<{ subject: Pick<SubjectRecord, "id" | "user_id" | "subject_code" | "display_name">; devices: SubjectDeviceRow[] }>>(
      "/api/readings/me/devices",
      { token }
    ).then((response) => response.data),
  myReadings: (
    query: { device_id?: string; from?: string; to?: string; limit?: number; offset?: number },
    token: string
  ) =>
    request<ApiEnvelope<{ subject: Pick<SubjectRecord, "id" | "user_id" | "subject_code" | "display_name">; readings: SensorReadingRow[] }>>(
      "/api/readings/me/readings",
      { token, query }
    ).then((response) => response.data),
  latestReading: (query: { device_id?: string }, token: string) =>
    request<ApiEnvelope<{ subject: Pick<SubjectRecord, "id" | "user_id" | "subject_code" | "display_name">; reading: SensorReadingRow }>>(
      "/api/readings/me/readings/latest",
      { token, query }
    ).then((response) => response.data),
  readingTrends: (
    query: { device_id?: string; from?: string; to?: string; bucket?: "hour" | "day"; limit?: number },
    token: string
  ) =>
    request<ApiEnvelope<{ subject: Pick<SubjectRecord, "id" | "user_id" | "subject_code" | "display_name">; trends: ReadingTrendRow[] }>>(
      "/api/readings/me/readings/trends",
      { token, query }
    ).then((response) => response.data),
  models: () => request<ApiEnvelope<{ models: ModelVersionRow[] }>>("/api/models").then((response) => response.data.models),
  createModel: (body: {
    model_name: string;
    version: string;
    status?: "training" | "deployed" | "archived";
    artifact_url?: string | null;
    trained_at?: string | null;
    deployed_at?: string | null;
    notes?: string | null;
  }) => request<ApiEnvelope<{ model: ModelVersionRow }>>("/api/models", { method: "POST", body }).then((response) => response.data.model),
  predictions: (query: { limit?: number; offset?: number; sensor_reading_id?: string; model_version_id?: string } = {}) =>
    request<ApiEnvelope<{ predictions: PredictionResultRow[] }>>("/api/predictions", { query }).then((response) => response.data.predictions),
};

export type GlicoviaApi = typeof api;
