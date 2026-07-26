BEGIN;

CREATE TYPE user_role AS ENUM ('subject', 'admin');
CREATE TYPE device_status AS ENUM ('unpaired', 'paired', 'offline', 'online', 'inactive');
CREATE TYPE assignment_status AS ENUM ('active', 'ended');
CREATE TYPE pairing_status AS ENUM ('pending', 'used', 'expired', 'revoked');
CREATE TYPE quality_flag AS ENUM ('valid', 'suspect', 'incomplete');
CREATE TYPE inference_status AS ENUM ('pending', 'success', 'failed');
CREATE TYPE model_status AS ENUM ('training', 'deployed', 'archived');

CREATE TABLE users (
  id uuid PRIMARY KEY,
  email varchar NOT NULL,
  password_hash varchar NOT NULL,
  full_name varchar,
  role user_role NOT NULL DEFAULT 'subject',
  is_active boolean NOT NULL DEFAULT true,
  last_login_at timestamptz,
  created_at timestamptz NOT NULL,
  updated_at timestamptz NOT NULL,
  CONSTRAINT users_email_key UNIQUE (email)
);

CREATE TABLE subjects (
  id uuid PRIMARY KEY,
  user_id uuid NOT NULL,
  subject_code varchar NOT NULL,
  display_name varchar,
  age int,
  sex varchar,
  notes text,
  created_at timestamptz NOT NULL,
  updated_at timestamptz NOT NULL,
  CONSTRAINT subjects_user_id_key UNIQUE (user_id),
  CONSTRAINT subjects_subject_code_key UNIQUE (subject_code),
  CONSTRAINT subjects_user_id_fkey
    FOREIGN KEY (user_id) REFERENCES users (id)
    ON UPDATE CASCADE
    ON DELETE RESTRICT
);

CREATE TABLE devices (
  id uuid PRIMARY KEY,
  device_code varchar NOT NULL,
  name varchar,
  mqtt_topic varchar NOT NULL,
  status device_status NOT NULL DEFAULT 'unpaired',
  firmware_version varchar,
  last_seen_at timestamptz,
  created_at timestamptz NOT NULL,
  updated_at timestamptz NOT NULL,
  CONSTRAINT devices_device_code_key UNIQUE (device_code),
  CONSTRAINT devices_mqtt_topic_key UNIQUE (mqtt_topic)
);

CREATE TABLE pairing_tokens (
  id uuid PRIMARY KEY,
  device_id uuid NOT NULL,
  token varchar NOT NULL,
  qr_payload text NOT NULL,
  status pairing_status NOT NULL DEFAULT 'pending',
  expires_at timestamptz NOT NULL,
  used_at timestamptz,
  revoked_at timestamptz,
  created_at timestamptz NOT NULL,
  CONSTRAINT pairing_tokens_token_key UNIQUE (token),
  CONSTRAINT pairing_tokens_device_id_fkey
    FOREIGN KEY (device_id) REFERENCES devices (id)
    ON UPDATE CASCADE
    ON DELETE RESTRICT
);

CREATE TABLE device_assignments (
  id uuid PRIMARY KEY,
  device_id uuid NOT NULL,
  subject_id uuid NOT NULL,
  pairing_token_id uuid,
  status assignment_status NOT NULL DEFAULT 'active',
  assigned_at timestamptz NOT NULL,
  unassigned_at timestamptz,
  created_at timestamptz NOT NULL,
  CONSTRAINT device_assignments_device_id_fkey
    FOREIGN KEY (device_id) REFERENCES devices (id)
    ON UPDATE CASCADE
    ON DELETE RESTRICT,
  CONSTRAINT device_assignments_subject_id_fkey
    FOREIGN KEY (subject_id) REFERENCES subjects (id)
    ON UPDATE CASCADE
    ON DELETE RESTRICT,
  CONSTRAINT device_assignments_pairing_token_id_fkey
    FOREIGN KEY (pairing_token_id) REFERENCES pairing_tokens (id)
    ON UPDATE CASCADE
    ON DELETE SET NULL
);

CREATE TABLE sensor_readings (
  id uuid PRIMARY KEY,
  device_id uuid NOT NULL,
  subject_id uuid,
  device_assignment_id uuid,
  recorded_at timestamptz NOT NULL,
  received_at timestamptz NOT NULL,
  ph decimal(6,3),
  fructosamine decimal(10,3),
  salivary_glucose decimal(10,3),
  raw_payload jsonb NOT NULL,
  quality_flag quality_flag NOT NULL DEFAULT 'valid',
  created_at timestamptz NOT NULL,
  CONSTRAINT sensor_readings_device_id_fkey
    FOREIGN KEY (device_id) REFERENCES devices (id)
    ON UPDATE CASCADE
    ON DELETE RESTRICT,
  CONSTRAINT sensor_readings_subject_id_fkey
    FOREIGN KEY (subject_id) REFERENCES subjects (id)
    ON UPDATE CASCADE
    ON DELETE SET NULL,
  CONSTRAINT sensor_readings_device_assignment_id_fkey
    FOREIGN KEY (device_assignment_id) REFERENCES device_assignments (id)
    ON UPDATE CASCADE
    ON DELETE SET NULL
);

CREATE TABLE model_versions (
  id uuid PRIMARY KEY,
  model_name varchar NOT NULL,
  version varchar NOT NULL,
  status model_status NOT NULL DEFAULT 'training',
  artifact_url text,
  trained_at timestamptz,
  deployed_at timestamptz,
  notes text,
  created_at timestamptz NOT NULL,
  CONSTRAINT model_versions_model_name_version_key UNIQUE (model_name, version)
);

CREATE TABLE prediction_results (
  id uuid PRIMARY KEY,
  sensor_reading_id uuid NOT NULL,
  model_version_id uuid NOT NULL,
  glucose_estimate decimal(10,3),
  clinical_category varchar,
  confidence_score decimal(5,4),
  inference_status inference_status NOT NULL DEFAULT 'pending',
  predicted_at timestamptz,
  created_at timestamptz NOT NULL,
  CONSTRAINT prediction_results_sensor_reading_id_fkey
    FOREIGN KEY (sensor_reading_id) REFERENCES sensor_readings (id)
    ON UPDATE CASCADE
    ON DELETE CASCADE,
  CONSTRAINT prediction_results_model_version_id_fkey
    FOREIGN KEY (model_version_id) REFERENCES model_versions (id)
    ON UPDATE CASCADE
    ON DELETE RESTRICT
);

COMMENT ON TABLE users IS 'Akun login untuk web. Pada flow baru, subject login lewat tabel ini.';
COMMENT ON TABLE subjects IS 'Profil health/data owner. Dipisahkan dari users agar nanti tetap fleksibel.';
COMMENT ON TABLE devices IS 'Satu baris = satu hardware GLICOVIA.';
COMMENT ON TABLE pairing_tokens IS 'Token sementara yang ditampilkan sebagai QR di layar hardware.';
COMMENT ON TABLE device_assignments IS 'Catatan resmi bahwa device sedang terhubung ke subject tertentu.';
COMMENT ON TABLE sensor_readings IS 'Data mentah dari MQTT. Tetap disimpan meski model AI belum tersedia.';
COMMENT ON TABLE model_versions IS 'Metadata versi model AI/SVM yang dipakai saat inferensi.';
COMMENT ON TABLE prediction_results IS 'Hasil prediksi AI dari satu sensor reading.';

CREATE INDEX idx_device_assignments_active_device_id
  ON device_assignments (device_id)
  WHERE status = 'active';

CREATE INDEX idx_device_assignments_active_subject_id
  ON device_assignments (subject_id)
  WHERE status = 'active';

CREATE INDEX idx_sensor_readings_subject_id_recorded_at
  ON sensor_readings (subject_id, recorded_at DESC);

CREATE INDEX idx_sensor_readings_device_id_recorded_at
  ON sensor_readings (device_id, recorded_at DESC);

COMMIT;
