# Graph Report - backend  (2026-09-07)

## Corpus Check
- 66 files · ~19,091 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 495 nodes · 923 edges · 18 communities (15 shown, 1 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 33 edges (avg confidence: 0.85)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `55011bf4`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- readings.service.ts
- package.json
- auth.ts
- device.repository.ts
- auth.service.ts
- API Detail
- mqtt-handler.ts
- app.ts
- Panduan Testing MQTT Hardware GLICOVIA
- inference.service.ts
- Checklist Selesai
- pairing.service.ts
- Hermes Master Prompt For GLICOVIA Backend
- compilerOptions
- express.d.ts
- apply_migrations.sh

## God Nodes (most connected - your core abstractions)
1. `badRequest()` - 22 edges
2. `express` - 21 edges
3. `API Detail` - 20 edges
4. `Hermes Master Prompt For GLICOVIA Backend` - 15 edges
5. `compilerOptions` - 14 edges
6. `PKMGlico Backend` - 13 edges
7. `register()` - 12 edges
8. `handleMqttMessage()` - 12 edges
9. `Strategi Eksekusi Yang Disarankan` - 11 edges
10. `Checklist Selesai` - 11 edges

## Surprising Connections (you probably didn't know these)
- `translateDbError()` --calls--> `conflict()`  [EXTRACTED]
  src/modules/devices/device.service.ts → src/lib/http-error.ts
- `register()` --calls--> `createId()`  [EXTRACTED]
  src/modules/auth/auth.service.ts → src/utils/ids.ts
- `DeviceJoinedRow` --references--> `DeviceStatus`  [EXTRACTED]
  src/modules/devices/device.repository.ts → src/modules/devices/device.types.ts
- `saveSensorReading()` --calls--> `insertSensorReading()`  [EXTRACTED]
  src/modules/readings/readings.service.ts → src/modules/readings/readings.repository.ts
- `handleMqttMessage()` --calls--> `resolveDeviceByTopicFirst()`  [EXTRACTED]
  src/mqtt/mqtt-handler.ts → src/modules/readings/readings.repository.ts

## Import Cycles
- None detected.

## Communities (18 total, 1 thin omitted)

### Community 0 - "readings.service.ts"
Cohesion: 0.09
Nodes (43): latestPredictionController(), listPredictionsController(), meLatestPredictionController(), mePredictionsController(), mePredictionTrendsController(), toNumber(), createPredictionResultIfAbsent(), getLatestPrediction() (+35 more)

### Community 1 - "package.json"
Cohesion: 0.04
Nodes (47): dependencies, bcryptjs, cors, dotenv, express, jsonwebtoken, mqtt, pg (+39 more)

### Community 2 - "auth.ts"
Cohesion: 0.10
Nodes (41): badRequest(), unauthorized(), base64UrlDecode(), base64UrlEncode(), JwtPayload, signHs256Jwt(), verifyHs256Jwt(), AuthenticatedRequest (+33 more)

### Community 3 - "device.repository.ts"
Cohesion: 0.08
Nodes (28): buildDeviceQuery(), createDevice(), DeviceJoinedRow, getActiveAssignmentForDeviceForUpdate(), getDeviceById(), getDeviceByIdForUpdate(), listDevices(), mapActiveAssignment() (+20 more)

### Community 4 - "auth.service.ts"
Cohesion: 0.13
Nodes (32): zod, loginController(), meController(), registerController(), AuthProfile, createSubject(), createUser(), findAuthProfileByUserId() (+24 more)

### Community 5 - "API Detail"
Cohesion: 0.06
Nodes (32): API Detail, Catatan implementasi, Database schema, DELETE /api/devices/:deviceId, Environment, Fitur yang sudah dibuat, GET /api/auth/me, GET /api/devices (+24 more)

### Community 6 - "mqtt-handler.ts"
Cohesion: 0.11
Nodes (21): dotenv, mqtt, app, env, logger, LogLevel, triggerInferenceForSensorReading(), resolveActiveAssignment() (+13 more)

### Community 7 - "app.ts"
Cohesion: 0.11
Nodes (21): express, errorHandler(), getMessage(), getStatusCode(), notFoundHandler(), requestIdMiddleware(), authRoutes, createModelController() (+13 more)

### Community 8 - "Panduan Testing MQTT Hardware GLICOVIA"
Cohesion: 0.07
Nodes (29): 1. Pakai Konfigurasi MQTT yang Sama, 1. Siapkan MQTT Broker, 2. Connect ke MQTT Broker, 2. Set Environment Backend, 3. Jalankan Database dan Migration, 3. Publish ke Topic yang Disepakati, 4. Jalankan Backend, 4. Kirim Payload JSON (+21 more)

### Community 9 - "inference.service.ts"
Cohesion: 0.13
Nodes (26): triggerReadingInferenceController(), inferenceRouter, asFiniteNumber(), callMlPrediction(), FALLBACK_MODEL_INFO, fetchMlJson(), getCategoryName(), httpError() (+18 more)

### Community 10 - "Checklist Selesai"
Cohesion: 0.07
Nodes (28): Arsitektur Yang Harus Dijaga, Aturan Delegasi Ke Codex, Auth, Checklist Selesai, Database, Devices, Docs, Fase 10. Dokumentasi dan verifikasi (+20 more)

### Community 11 - "pairing.service.ts"
Cohesion: 0.16
Nodes (12): pg, pool, AppError, conflict(), forbidden(), gone(), notFound(), withTransaction() (+4 more)

### Community 12 - "Hermes Master Prompt For GLICOVIA Backend"
Cohesion: 0.09
Nodes (21): 1. Health, 2. Auth, 3. Devices, 4. Pairing, 5. Subject-Scoped Reading APIs, 6. Model and Prediction Readiness, Developer Experience Requirements, Execution Order (+13 more)

### Community 13 - "compilerOptions"
Cohesion: 0.12
Nodes (16): compilerOptions, declaration, esModuleInterop, forceConsistentCasingInFileNames, module, moduleResolution, outDir, resolveJsonModule (+8 more)

### Community 14 - "express.d.ts"
Cohesion: 0.33
Nodes (5): Express, express-serve-static-core, Request, Subject, User

## Knowledge Gaps
- **194 isolated node(s):** `name`, `version`, `private`, `description`, `main` (+189 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 230 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **1 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `express` connect `app.ts` to `readings.service.ts`, `package.json`, `auth.ts`, `auth.service.ts`, `inference.service.ts`?**
  _High betweenness centrality (0.126) - this node is a cross-community bridge._
- **Why does `pg` connect `pairing.service.ts` to `package.json`, `device.repository.ts`, `auth.service.ts`?**
  _High betweenness centrality (0.049) - this node is a cross-community bridge._
- **Why does `pool` connect `pairing.service.ts` to `readings.service.ts`, `auth.ts`, `device.repository.ts`, `auth.service.ts`, `app.ts`?**
  _High betweenness centrality (0.042) - this node is a cross-community bridge._
- **What connects `name`, `version`, `private` to the rest of the system?**
  _194 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `readings.service.ts` be split into smaller, more focused modules?**
  _Cohesion score 0.09361393323657474 - nodes in this community are weakly interconnected._
- **Should `package.json` be split into smaller, more focused modules?**
  _Cohesion score 0.04081632653061224 - nodes in this community are weakly interconnected._
- **Should `auth.ts` be split into smaller, more focused modules?**
  _Cohesion score 0.10119047619047619 - nodes in this community are weakly interconnected._