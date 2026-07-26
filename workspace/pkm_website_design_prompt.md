# Rancangan Design & Prompt Hermes

## Project Context
Website ini dibuat untuk PKM-KC: non-invasive blood glucose monitoring via saliva.

Tujuan website:
- menerima data dari hardware prototype atau input manual
- menampilkan prediksi gula darah dari model ML
- menampilkan status device / sensor
- menyimpan riwayat data per subject anonim
- menyajikan analitik untuk tim, dosen pembimbing, dan evaluasi PKM

## Design Direction

Nama gaya:
- Clinical Precision Light

Karakter visual:
- bright, clean, trustworthy
- medical-tech, scientific, data-driven
- rapi dan profesional, bukan generic AI startup
- minim dekorasi, fokus ke informasi
- terasa seperti dashboard monitoring kesehatan modern

Catatan penting:
- tema warna JANGAN gelap
- gunakan light theme sebagai default
- background cerah, surface putih/abu muda
- accent hijau/teal untuk health/status
- warning amber, danger red, info blue
- hindari neon, glassmorphism berlebihan, dan gradient yang ramai

## Visual System

### 1. Color Tokens

Base / Background:
- Background utama: `#F7F9FC`
- Background sekunder: `#EEF3F8`
- Surface card: `#FFFFFF`
- Surface elevated: `#F9FBFD`
- Border subtle: `#DCE5EE`

Text:
- Text primary: `#102033`
- Text secondary: `#4B5C70`
- Text muted: `#748599`
- Text disabled: `#A6B3C2`

Accent utama:
- Emerald: `#10B981`
- Teal: `#14B8A6`
- Blue info: `#3B82F6`

Status colors:
- Normal: `#10B981`
- Warning: `#F59E0B`
- Danger: `#EF4444`
- Offline / muted: `#94A3B8`

Chart colors:
- Primary line: `#14B8A6`
- Secondary line: `#3B82F6`
- Comparison line: `#8B5CF6`
- Gridline: `#E5EDF5`

Rules:
- jangan pakai banyak warna sekaligus
- setiap warna harus punya makna semantik
- hindari warna ungu startup generik sebagai aksen utama
- jangan pakai background gelap

### 2. Typography

Primary font:
- Inter / Geist

Mono font:
- JetBrains Mono

Hierarchy:
- Page title: kuat, jelas, modern
- KPI number: paling dominan
- Section title: medium-bold
- Body text: normal, mudah dibaca
- Table text: compact tapi tetap lega
- Technical values: monospace

Typography behavior:
- heading harus ringkas dan percaya diri
- angka penting dibuat lebih besar daripada label
- gunakan letter spacing normal atau sangat halus
- jangan terlalu banyak style dekoratif

### 3. Layout

Layout utama:
- sidebar kiri untuk navigasi
- header atas untuk search, status device, user/setting
- content area berbasis card
- grid 12 kolom untuk desktop

Spacing:
- gunakan sistem 8px
- cukup whitespace agar terasa bersih
- tetap data-dense, jangan terlalu kosong

Radius:
- card: 14px
- button: 10px
- chip: 9999px
- input: 12px

Shadow:
- soft shadow ringan
- lebih banyak mengandalkan border + surface layering daripada shadow dramatis

### 4. Visual Style Rules

Wajib:
- clean medical dashboard feel
- tabel dan chart menjadi fokus utama
- nomor dan status mudah dibaca dalam 3 detik
- responsif di desktop dan mobile
- ada loading state, empty state, error state

Hindari:
- hero besar yang seperti landing page SaaS biasa
- ilustrasi generik AI
- dekorasi berlebihan
- animasi yang terlalu ramai
- glassmorphism berat
- gradient blur yang tidak perlu
- layout yang terlalu template-like

## Sitemap / Pages

1. Dashboard
- summary cards
- chart utama tren gula darah
- recent readings table
- device status
- alert panel
- quick actions

2. Subjects
- daftar subject anonim
- search dan filter
- jumlah data per subject
- status pengukuran

3. Subject Detail
- profil subject anonim
- riwayat pengukuran
- chart per subject
- metadata sampling
- timeline data

4. Data Ingestion
- form input data dari hardware/manual
- validasi field
- feedback sukses/gagal
- log request terakhir

5. Predictions
- hasil prediksi mg/dL
- category label klinis
- perbandingan dengan ground truth
- model version
- timestamp

6. Analytics
- distribusi data
- korelasi feature
- RMSE / MAE / R²
- outlier analysis
- trend analysis

7. Settings
- konfigurasi device
- endpoint API
- model info
- environment config
- optional access control

## Required Features

### Core Features
- dashboard monitoring
- data ingestion / submit form
- subject history
- prediction display
- analytics summary
- export CSV / PDF jika memungkinkan

### UX States
- loading skeleton
- empty state
- error state
- offline / disconnected state
- success toast
- validation error message

### Dashboard Priority
1. latest predicted glucose
2. clinical category
3. device connection status
4. last sync time
5. trend chart
6. recent readings
7. alerts / anomaly indicator

### Data Fields to Show
- subject_id anonim
- sampling_date
- sampling_time
- fasting_hours
- saliva_ph
- saliva_viscosity_sec
- saliva_glucose_mgdl
- bg_reference_mgdl
- predicted_bg_mgdl
- clinical_category
- proto_glucose_raw
- model version
- device status

## Frontend Component List

- Sidebar navigation
- Top navbar
- KPI stat cards
- Trend chart card
- Recent records table
- Filter chips
- Status badge / pill
- Device status card
- Alert banner
- Subject profile card
- Metric summary card
- Empty state panel
- Skeleton loader
- Modal / drawer for record details
- Toast notification
- Date range picker
- Search input
- Sortable table header

## UX / Interaction Rules

- hover state harus subtle
- active filter harus jelas
- chart tooltip clean dan ringkas
- table row highlight lembut
- loading state jangan mengganggu
- mobile layout stacked dan tetap terbaca
- aksesibilitas tetap diperhatikan

## Prompt Detail untuk Hermes

Gunakan prompt berikut untuk eksekusi frontend:

---

You are building a production-quality website for a PKM project: non-invasive blood glucose monitoring via saliva.

Project context:
- The system collects saliva-based measurements and predicts blood glucose.
- Data comes from a prototype hardware device and may also be entered manually during development.
- Core data fields: subject_id (anonymous), sampling_date, sampling_time, fasting_hours, saliva_ph, saliva_viscosity_sec, saliva_glucose_mgdl, bg_reference_mgdl, bg_category, proto_glucose_raw, predicted_bg_mgdl, clinical_category.
- The website is for internal monitoring, data review, prediction display, and analytics for the PKM team.
- The UI must feel trustworthy, clean, data-dense, and scientific.

Design direction:
Create a “Clinical Precision Light” dashboard:
- light mode by default
- clean, precise, minimal, data-first
- inspired by Linear / Supabase / Sentry structure, but adapted to medical monitoring
- use emerald/teal as the primary accent for health/status
- avoid generic AI startup aesthetics
- avoid excessive glow, gradients, and glassmorphism
- use Inter or Geist for typography, JetBrains Mono for technical values
- use subtle borders, soft elevation, and clear hierarchy
- the main visual language should be calm, professional, and technical

Mandatory UI principles:
1. No generic template look.
2. No random stock illustrations.
3. No huge hero section that dominates the page.
4. No overly decorative gradients or abstract blobs.
5. No heavy animation or flashy motion.
6. Numbers and status must be immediately readable.
7. Data tables and charts must be the core of the interface.
8. Use a compact but breathable dashboard layout.
9. Make the UI look like a serious monitoring tool for healthcare data.

Pages to build:
1. Dashboard
- KPI cards: latest predicted glucose, clinical category, device status, last sync time
- primary trend chart
- recent readings table
- alerts panel
- quick actions

2. Subjects
- searchable anonymized subject list
- subject stats
- records count
- status badges

3. Subject detail
- subject profile summary
- history timeline
- trend chart per subject
- measurement table
- sample metadata

4. Data ingestion
- form for device/manual input
- validation
- success/error feedback
- last request log

5. Predictions
- prediction output card
- predicted mg/dL
- category label
- comparison with reference
- model version

6. Analytics
- distribution charts
- feature correlation
- RMSE / MAE / R² summary
- outlier analysis
- trends over time

7. Settings
- device/API settings
- model info
- environment config
- optional access controls

Visual system:
- Background: `#F7F9FC`
- Secondary background: `#EEF3F8`
- Card surface: `#FFFFFF`
- Border: `#DCE5EE`
- Text primary: `#102033`
- Text secondary: `#4B5C70`
- Muted: `#748599`
- Accent: emerald/teal
- Warning: amber
- Danger: red
- Info: blue

Component requirements:
- sticky sidebar navigation
- compact top bar with search and connection status
- stat cards with big numbers and small labels
- line chart card with tooltips
- recent readings table with sortable columns
- badge system for clinical category
- device status card with online/offline state
- alert banner for abnormal or missing data
- empty states and skeleton loaders
- modal or drawer for record detail
- toast notifications for submit and sync events

Data presentation rules:
- Make the predicted glucose number the most prominent value.
- Show clinical category clearly as a badge.
- Show sampling time and fasting hours near the top.
- Make sensor/connection status obvious.
- Keep all table rows compact and readable.
- Add filters for date range, subject, and category.
- Use clear labels and avoid clutter.

Frontend implementation rules:
- Use a modern React/Next.js structure.
- Prefer App Router architecture if available.
- Use TypeScript.
- Use Tailwind CSS or clean component styling.
- Components must be reusable and consistent.
- Do not hardcode a generic marketing page; build a real dashboard system.
- Use responsive behavior for tablet and mobile.
- Make the mobile layout stacked but still readable.

Suggested layout:
- Sidebar on the left
- Header on top
- Main content in cards and grids
- KPI row first
- chart section second
- table and activity panels below
- use 12-column grid for desktop

Accessibility and UX:
- Ensure contrast is sufficient.
- Keep labels readable.
- Use semantic HTML.
- Ensure keyboard navigation works.
- Use meaningful empty states.
- Show loading placeholders while data is fetching.
- Show error states gracefully.

Output expectation:
- Build the full dashboard UI and supporting pages.
- Make it feel like a real PKM medical monitoring product.
- The final UI must not look AI-generated or generic.
- The design should be polished, consistent, and implementation-ready.

If any part of the brief is ambiguous, infer the most credible product-design direction and proceed without asking multiple questions. However, if a single critical ambiguity blocks implementation, ask exactly one concise question.

Acceptance criteria:
- The website looks unique and intentional.
- The UI matches a medical monitoring + ML dashboard.
- The feature set fits the PKM saliva glucose project.
- The pages are responsive and polished.
- The charts, tables, and cards feel production-ready.
- The design does not look like a stock template.
---

## Execution Recommendation

For the first implementation pass:
1. build the design system tokens
2. build the dashboard shell
3. add KPI cards, charts, and tables
4. add subject detail page
5. add data ingestion form
6. polish responsive states and empty states

## Short Version for Direct Reuse

If you need a very short prompt for Hermes, use this:

> Build a light-mode, clinical precision dashboard for a PKM saliva glucose monitoring project. The UI must feel scientific, trustworthy, data-dense, and not generic. Use a white/soft-blue background, subtle borders, emerald/teal accents, Inter/Geist typography, and JetBrains Mono for technical values. Create pages for Dashboard, Subjects, Subject Detail, Data Ingestion, Predictions, Analytics, and Settings. Focus on charts, tables, KPI cards, device status, and alert states. Avoid dark theme, generic SaaS gradients, stock illustrations, and heavy animation. Make the result production-quality, responsive, and implementation-ready.
