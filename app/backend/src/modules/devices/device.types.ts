export type DeviceStatus = 'unpaired' | 'paired' | 'offline' | 'online' | 'inactive';

export interface DeviceRecord {
  id: string;
  device_code: string;
  name: string | null;
  mqtt_topic: string;
  status: DeviceStatus;
  firmware_version: string | null;
  last_seen_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface ActiveAssignmentRecord {
  id: string;
  subject_id: string;
  assigned_at: string;
  subject_code: string | null;
  subject_name: string | null;
}

export interface DeviceWithAssignment extends DeviceRecord {
  active_assignment: ActiveAssignmentRecord | null;
}

export interface CreateDeviceInput {
  deviceCode: string;
  name?: string | null;
  mqttTopic: string;
  status?: DeviceStatus;
  firmwareVersion?: string | null;
  lastSeenAt?: string | null;
}

export interface UpdateDeviceInput {
  deviceCode?: string;
  name?: string | null;
  mqttTopic?: string;
  status?: DeviceStatus;
  firmwareVersion?: string | null;
  lastSeenAt?: string | null;
}
