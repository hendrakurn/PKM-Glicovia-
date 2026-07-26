-- CreateSchema
CREATE SCHEMA IF NOT EXISTS "public";

-- CreateEnum
CREATE TYPE "user_role" AS ENUM ('subject', 'admin');

-- CreateEnum
CREATE TYPE "device_status" AS ENUM ('unpaired', 'paired', 'offline', 'online', 'inactive');

-- CreateEnum
CREATE TYPE "assignment_status" AS ENUM ('active', 'ended');

-- CreateEnum
CREATE TYPE "pairing_status" AS ENUM ('pending', 'used', 'expired', 'revoked');

-- CreateEnum
CREATE TYPE "quality_flag" AS ENUM ('valid', 'suspect', 'incomplete');

-- CreateEnum
CREATE TYPE "inference_status" AS ENUM ('pending', 'success', 'failed');

-- CreateEnum
CREATE TYPE "model_status" AS ENUM ('training', 'deployed', 'archived');

-- CreateTable
CREATE TABLE "users" (
    "id" UUID NOT NULL,
    "email" VARCHAR NOT NULL,
    "password_hash" VARCHAR NOT NULL,
    "full_name" VARCHAR,
    "role" "user_role" NOT NULL DEFAULT 'subject',
    "is_active" BOOLEAN NOT NULL DEFAULT true,
    "last_login_at" TIMESTAMPTZ(6),
    "created_at" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ(6) NOT NULL,

    CONSTRAINT "users_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "subjects" (
    "id" UUID NOT NULL,
    "user_id" UUID NOT NULL,
    "subject_code" VARCHAR NOT NULL,
    "display_name" VARCHAR,
    "age" INTEGER,
    "sex" VARCHAR,
    "notes" TEXT,
    "created_at" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ(6) NOT NULL,

    CONSTRAINT "subjects_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "devices" (
    "id" UUID NOT NULL,
    "device_code" VARCHAR NOT NULL,
    "name" VARCHAR,
    "mqtt_topic" VARCHAR NOT NULL,
    "status" "device_status" NOT NULL DEFAULT 'unpaired',
    "firmware_version" VARCHAR,
    "last_seen_at" TIMESTAMPTZ(6),
    "created_at" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ(6) NOT NULL,

    CONSTRAINT "devices_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "pairing_tokens" (
    "id" UUID NOT NULL,
    "device_id" UUID NOT NULL,
    "token" VARCHAR NOT NULL,
    "qr_payload" TEXT NOT NULL,
    "status" "pairing_status" NOT NULL DEFAULT 'pending',
    "expires_at" TIMESTAMPTZ(6) NOT NULL,
    "used_at" TIMESTAMPTZ(6),
    "revoked_at" TIMESTAMPTZ(6),
    "created_at" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "pairing_tokens_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "device_assignments" (
    "id" UUID NOT NULL,
    "device_id" UUID NOT NULL,
    "subject_id" UUID NOT NULL,
    "pairing_token_id" UUID,
    "status" "assignment_status" NOT NULL DEFAULT 'active',
    "assigned_at" TIMESTAMPTZ(6) NOT NULL,
    "unassigned_at" TIMESTAMPTZ(6),
    "created_at" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "device_assignments_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "sensor_readings" (
    "id" UUID NOT NULL,
    "device_id" UUID NOT NULL,
    "subject_id" UUID,
    "device_assignment_id" UUID,
    "recorded_at" TIMESTAMPTZ(6) NOT NULL,
    "received_at" TIMESTAMPTZ(6) NOT NULL,
    "ph" DECIMAL(6,3),
    "fructosamine" DECIMAL(10,3),
    "salivary_glucose" DECIMAL(10,3),
    "raw_payload" JSONB NOT NULL,
    "quality_flag" "quality_flag" NOT NULL DEFAULT 'valid',
    "created_at" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "sensor_readings_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "model_versions" (
    "id" UUID NOT NULL,
    "model_name" VARCHAR NOT NULL,
    "version" VARCHAR NOT NULL,
    "status" "model_status" NOT NULL DEFAULT 'training',
    "artifact_url" TEXT,
    "trained_at" TIMESTAMPTZ(6),
    "deployed_at" TIMESTAMPTZ(6),
    "notes" TEXT,
    "created_at" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "model_versions_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "prediction_results" (
    "id" UUID NOT NULL,
    "sensor_reading_id" UUID NOT NULL,
    "model_version_id" UUID NOT NULL,
    "glucose_estimate" DECIMAL(10,3),
    "clinical_category" VARCHAR,
    "confidence_score" DECIMAL(5,4),
    "inference_status" "inference_status" NOT NULL DEFAULT 'pending',
    "predicted_at" TIMESTAMPTZ(6),
    "created_at" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "prediction_results_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE UNIQUE INDEX "users_email_key" ON "users"("email");

-- CreateIndex
CREATE UNIQUE INDEX "subjects_user_id_key" ON "subjects"("user_id");

-- CreateIndex
CREATE UNIQUE INDEX "subjects_subject_code_key" ON "subjects"("subject_code");

-- CreateIndex
CREATE UNIQUE INDEX "devices_device_code_key" ON "devices"("device_code");

-- CreateIndex
CREATE UNIQUE INDEX "devices_mqtt_topic_key" ON "devices"("mqtt_topic");

-- CreateIndex
CREATE UNIQUE INDEX "pairing_tokens_token_key" ON "pairing_tokens"("token");

-- CreateIndex
CREATE INDEX "device_assignments_device_id_idx" ON "device_assignments"("device_id");

-- CreateIndex
CREATE INDEX "device_assignments_subject_id_idx" ON "device_assignments"("subject_id");

-- CreateIndex
CREATE INDEX "sensor_readings_subject_id_recorded_at_idx" ON "sensor_readings"("subject_id", "recorded_at" DESC);

-- CreateIndex
CREATE INDEX "sensor_readings_device_id_recorded_at_idx" ON "sensor_readings"("device_id", "recorded_at" DESC);

-- CreateIndex
CREATE UNIQUE INDEX "model_versions_model_name_version_key" ON "model_versions"("model_name", "version");

-- AddForeignKey
ALTER TABLE "subjects" ADD CONSTRAINT "subjects_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "users"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "pairing_tokens" ADD CONSTRAINT "pairing_tokens_device_id_fkey" FOREIGN KEY ("device_id") REFERENCES "devices"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "device_assignments" ADD CONSTRAINT "device_assignments_device_id_fkey" FOREIGN KEY ("device_id") REFERENCES "devices"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "device_assignments" ADD CONSTRAINT "device_assignments_subject_id_fkey" FOREIGN KEY ("subject_id") REFERENCES "subjects"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "device_assignments" ADD CONSTRAINT "device_assignments_pairing_token_id_fkey" FOREIGN KEY ("pairing_token_id") REFERENCES "pairing_tokens"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "sensor_readings" ADD CONSTRAINT "sensor_readings_device_id_fkey" FOREIGN KEY ("device_id") REFERENCES "devices"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "sensor_readings" ADD CONSTRAINT "sensor_readings_subject_id_fkey" FOREIGN KEY ("subject_id") REFERENCES "subjects"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "sensor_readings" ADD CONSTRAINT "sensor_readings_device_assignment_id_fkey" FOREIGN KEY ("device_assignment_id") REFERENCES "device_assignments"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "prediction_results" ADD CONSTRAINT "prediction_results_sensor_reading_id_fkey" FOREIGN KEY ("sensor_reading_id") REFERENCES "sensor_readings"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "prediction_results" ADD CONSTRAINT "prediction_results_model_version_id_fkey" FOREIGN KEY ("model_version_id") REFERENCES "model_versions"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

