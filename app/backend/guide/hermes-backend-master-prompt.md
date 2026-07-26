# Hermes Master Prompt For GLICOVIA Backend

You are Hermes working in the backend workspace at:

`~/projects/pkmGlico/app/backend`

You may call Codex for concrete coding tasks, but you retain responsibility for end-to-end execution, integration, validation, and final reporting.

## Goal

Implement a modular production-structured backend using Express + TypeScript + PostgreSQL + MQTT for the GLICOVIA system, based on the DBML schema at:

`~/projects/pkmGlico/app/web/diagrams/glicovia-user-pairing-fixed.dbml`

This backend must be immediately usable for:
- subject registration and login
- QR pairing token flow
- device-to-subject assignment
- MQTT sensor ingestion from hardware
- subject-scoped read APIs for frontend/dashboard
- future AI prediction integration

The backend folder is currently empty and must be scaffolded from scratch.

## System Context

- Frontend already exists separately in `~/projects/pkmGlico/app/web`
- Backend must live in `~/projects/pkmGlico/app/backend`
- Hardware sends sensor readings over MQTT
- Product flow is user-centric:
  1. a subject creates an account
  2. the subject logs in
  3. a hardware device displays a QR pairing token
  4. the subject scans the QR while logged in
  5. backend verifies the token
  6. backend creates a device assignment linking that device to that subject
  7. future MQTT sensor data from that device is stored under that subject
- Schema direction must match the DBML file
- Sensor data fields must use:
  - `ph`
  - `fructosamine`
  - `salivary_glucose`

## Non-Negotiable Implementation Constraints

- Use TypeScript
- Use Express
- Use PostgreSQL
- Use MQTT
- Use JWT auth
- Use environment variables
- Use modular code organization
- Do not implement everything in one file
- Do not stop at planning; actually implement
- Do not fake architecture with placeholder-only files
- Make the backend runnable locally
- Add clear setup and usage docs
- Keep the code maintainable and production-structured

## Required Database Entities

Implement schema and migrations for:
- `users`
- `subjects`
- `devices`
- `pairing_tokens`
- `device_assignments`
- `sensor_readings`
- `model_versions`
- `prediction_results`

## Required Business Meaning

- `users` = login identities
- `subjects` = health-data owners
- `devices` = hardware units
- `pairing_tokens` = temporary one-time QR pairing tokens
- `device_assignments` = official record of which subject a device is currently linked to
- `sensor_readings` = raw MQTT-ingested measurements
- `model_versions` = metadata of deployed AI models
- `prediction_results` = model inference outputs linked to a reading

## Required Folder Structure

Use a modular layout close to this unless a better equivalent is strongly justified:

```text
backend/
  src/
    app.ts
    server.ts
    config/
      env.ts
      logger.ts
    db/
      pool.ts
      migrations/
    middleware/
      auth.ts
      error-handler.ts
      not-found.ts
    modules/
      auth/
        auth.controller.ts
        auth.routes.ts
        auth.schema.ts
        auth.service.ts
        auth.repository.ts
      subjects/
        subjects.controller.ts
        subjects.routes.ts
        subjects.service.ts
        subjects.repository.ts
      devices/
        devices.controller.ts
        devices.routes.ts
        devices.service.ts
        devices.repository.ts
      pairing/
        pairing.controller.ts
        pairing.routes.ts
        pairing.schema.ts
        pairing.service.ts
        pairing.repository.ts
      readings/
        readings.controller.ts
        readings.routes.ts
        readings.service.ts
        readings.repository.ts
      models/
        models.controller.ts
        models.routes.ts
        models.service.ts
        models.repository.ts
      predictions/
        predictions.controller.ts
        predictions.routes.ts
        predictions.service.ts
        predictions.repository.ts
    mqtt/
      mqtt-client.ts
      mqtt-handler.ts
      topic-parser.ts
    utils/
      crypto.ts
      dates.ts
      ids.ts
    types/
      express.d.ts
  package.json
  tsconfig.json
  .env.example
  README.md
```

## Required API Surface

### 1. Health

- `GET /health`

### 2. Auth

- `POST /api/auth/register`
- `POST /api/auth/login`
- `GET /api/auth/me`

Behavior:
- register creates both `users` and `subjects`
- password must be hashed
- login returns JWT
- auth routes use Bearer token

### 3. Devices

- `POST /api/devices`
- `GET /api/devices`
- `GET /api/devices/:deviceId`
- `PATCH /api/devices/:deviceId`

### 4. Pairing

- `POST /api/devices/:deviceId/pairing-token`
- `POST /api/pairing/scan`
- `POST /api/devices/:deviceId/unpair`

Behavior:
- pairing token must be unique, expiring, and one-time-use
- generating a new token revokes older pending tokens for the same device
- scanning token while logged in must:
  - validate token exists
  - validate token is pending
  - validate token is not expired
  - validate device exists
  - resolve the logged-in subject
  - create a `device_assignments` row
  - mark token used
  - update device status appropriately
- unpair must close active assignment and update device state

### 5. Subject-Scoped Reading APIs

- `GET /api/me/devices`
- `GET /api/me/readings`
- `GET /api/me/readings/latest`
- `GET /api/me/readings/trends`

Behavior:
- only return data belonging to the logged-in subject
- support useful filters:
  - `device_id`
  - `from`
  - `to`
  - pagination where applicable

### 6. Model and Prediction Readiness

- `GET /api/models`
- `POST /api/models`
- `GET /api/predictions`

Behavior:
- do not implement fake AI inference
- keep the backend architecture ready for future integration
- prediction querying should work if rows exist in DB

## MQTT Ingestion Requirements

The backend must connect to an MQTT broker using environment variables.

Support a contract that can be tested directly from hardware, for example:

Topic:
- `glicovia/devices/GLICO-01/readings`

Payload:

```json
{
  "device_code": "GLICO-01",
  "recorded_at": "2026-07-16T10:15:00Z",
  "ph": 7.12,
  "fructosamine": 285.4,
  "salivary_glucose": 9.8
}
```

Define and document a clear device-resolution strategy. Prefer:
- topic first
- payload fallback

When MQTT data is received:
- resolve device
- resolve active assignment if any
- insert `sensor_readings`
- save `raw_payload`
- save `received_at`
- save `quality_flag`
- allow `subject_id` and `device_assignment_id` to be null if device is known but currently unassigned, if that is operationally safer
- clearly document this behavior

## Validation and Error Handling

- add request validation for body/query/params
- add centralized error handling
- return consistent JSON responses
- handle:
  - duplicate email
  - duplicate device_code
  - invalid token
  - expired token
  - revoked token
  - unknown device
  - missing subject profile
  - malformed MQTT payload
  - database constraint violations

## Security Requirements

- hash passwords securely
- sign JWT securely
- keep secrets in env only
- pairing tokens must not be reusable
- do not expose password hashes
- protect subject-scoped endpoints with auth

## Developer Experience Requirements

Provide:
- `.env.example`
- migration command
- dev command
- build command
- start command
- README with:
  - setup
  - env config
  - migration steps
  - how to start the server
  - how to test register/login
  - how to generate pairing token
  - how to scan pairing token
  - sample MQTT publish command
  - example curl commands

## Implementation Expectations

- translate the DBML into actual PostgreSQL schema/migrations
- scaffold the backend project
- implement routes, controllers, services, repositories, middleware, and MQTT integration
- ensure the code is modular
- do not leave the system in half-scaffolded state
- if a part is intentionally stubbed, say so explicitly and make it future-ready

## Execution Order

1. Read the DBML file
2. Scaffold the backend project
3. Implement env/config/database bootstrap
4. Implement migrations/schema
5. Implement auth
6. Implement device management
7. Implement pairing flow
8. Implement MQTT ingestion
9. Implement subject-scoped read APIs
10. Implement model/prediction read readiness
11. Write README and `.env.example`
12. Validate build and basic run commands

## Final Output Requirements

At the end, report:
- folder structure created
- implemented endpoints
- migration/schema status
- MQTT topic/payload contract
- local run steps
- assumptions
- remaining non-blocking gaps if any

Start now and complete the implementation rather than only planning.
