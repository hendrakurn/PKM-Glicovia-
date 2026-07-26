export type ISODateString = string;

export type UserProfile = {
  id: string;
  email: string;
  full_name: string | null;
  role: "subject" | "admin" | string;
  is_active: boolean;
  last_login_at: ISODateString | null;
  created_at: ISODateString;
  updated_at: ISODateString;
};

export type SubjectRecord = {
  id: string;
  user_id: string;
  subject_code: string;
  display_name: string | null;
  age: number | null;
  sex: string | null;
  notes: string | null;
  created_at: ISODateString;
  updated_at: ISODateString;
};

export type AuthProfile = {
  user: UserProfile;
  subject: SubjectRecord;
};

export type AuthResponse = AuthProfile & {
  accessToken: string;
  tokenType: "Bearer";
};

export type DeviceStatus = "unpaired" | "paired" | "offline" | "online" | "inactive";

export type DeviceRecord = {
  id: string;
  device_code: string;
  name: string | null;
  mqtt_topic: string;
  status: DeviceStatus;
  firmware_version: string | null;
  last_seen_at: ISODateString | null;
  created_at: ISODateString;
  updated_at: ISODateString;
};

export type ActiveAssignmentRecord = {
  id: string;
  subject_id: string;
  assigned_at: ISODateString;
  subject_code: string | null;
  subject_name: string | null;
};

export type DeviceWithAssignment = DeviceRecord & {
  active_assignment: ActiveAssignmentRecord | null;
};

export type CreateDeviceInput = {
  deviceCode: string;
  name?: string | null;
  mqttTopic: string;
  status?: DeviceStatus;
  firmwareVersion?: string | null;
  lastSeenAt?: string | null;
};

export type UpdateDeviceInput = Partial<CreateDeviceInput>;

export type PairingTokenRecord = {
  id: string;
  device_id: string;
  token: string;
  qr_payload: string;
  status: "pending" | "used" | "expired" | "revoked" | string;
  expires_at: ISODateString;
  used_at: ISODateString | null;
  revoked_at: ISODateString | null;
  created_at: ISODateString;
};

export type DeviceAssignmentRecord = {
  id: string;
  device_id: string;
  subject_id: string;
  pairing_token_id: string | null;
  status: "active" | "ended" | string;
  assigned_at: ISODateString;
  unassigned_at: ISODateString | null;
  created_at: ISODateString;
};

export type SubjectDeviceRow = {
  device_assignment_id: string;
  device_id: string;
  device_code: string;
  device_name: string | null;
  mqtt_topic: string;
  device_status: DeviceStatus | string;
  subject_id: string;
  subject_code: string;
  subject_name: string | null;
  assigned_at: ISODateString;
  unassigned_at: ISODateString | null;
};

export type SensorReadingRow = {
  id: string;
  device_id: string;
  subject_id: string | null;
  device_assignment_id: string | null;
  recorded_at: ISODateString;
  received_at: ISODateString;
  ph: string | number | null;
  fructosamine: string | number | null;
  salivary_glucose: string | number | null;
  raw_payload: unknown;
  quality_flag: "valid" | "suspect" | "incomplete" | string;
  created_at: ISODateString;
};

export type ReadingTrendRow = {
  bucket_start: ISODateString;
  reading_count: string;
  ph_avg: string | null;
  fructosamine_avg: string | null;
  salivary_glucose_avg: string | null;
};

export type PredictionTrendRow = {
  bucket_start: ISODateString;
  prediction_count: string;
  glucose_estimate_avg: string | null;
  glucose_estimate_min: string | null;
  glucose_estimate_max: string | null;
};

export type ModelVersionRow = {
  id: string;
  model_name: string;
  version: string;
  status: "training" | "deployed" | "archived" | string;
  artifact_url: string | null;
  trained_at: ISODateString | null;
  deployed_at: ISODateString | null;
  notes: string | null;
  created_at: ISODateString;
};

export type PredictionResultRow = {
  id: string;
  sensor_reading_id: string;
  model_version_id: string;
  glucose_estimate: string | number | null;
  clinical_category: string | null;
  confidence_score: string | number | null;
  inference_status: string;
  predicted_at: ISODateString | null;
  created_at: ISODateString;
  sensor_recorded_at?: ISODateString;
  model_name?: string;
  model_version?: string;
};

export type HealthResponse = {
  status: "ok" | string;
  timestamp: ISODateString;
};

export type ApiEnvelope<T> = {
  data: T;
};
