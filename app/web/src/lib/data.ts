export type ClinicalCategory = "Normal" | "Pre-Diabetes" | "Diabetes";
export type DeviceState = "Online" | "Syncing" | "Offline" | "Maintenance";

export type Reading = {
  id: string;
  subjectId: string;
  samplingDate: string;
  samplingTime: string;
  fastingHours: number;
  salivaPh: number;
  salivaViscositySec: number;
  salivaGlucoseMgdl: number;
  bgReferenceMgdl: number;
  predictedBgMgdl: number;
  bgCategory: string;
  clinicalCategory: ClinicalCategory;
  protoGlucoseRaw: number;
  modelVersion: string;
  deviceStatus: DeviceState;
  anomaly?: string;
};

export type Subject = {
  id: string;
  code: string;
  alias: string;
  cohort: string;
  recordsCount: number;
  latestSampling: string;
  latestPredictedBgMgdl: number;
  lastReferenceBgMgdl: number;
  fastingAverage: number;
  deviceStatus: DeviceState;
  clinicalCategory: ClinicalCategory;
  trendDelta: number;
  note: string;
};

export type SubjectHistory = {
  id: string;
  code: string;
  samples: Array<Pick<Reading, "id" | "samplingDate" | "samplingTime" | "fastingHours" | "salivaPh" | "salivaViscositySec" | "salivaGlucoseMgdl" | "bgReferenceMgdl" | "predictedBgMgdl" | "clinicalCategory" | "protoGlucoseRaw" | "deviceStatus" | "bgCategory">>;
};

export const dashboardMetrics = {
  latestPredictedBgMgdl: 142,
  clinicalCategory: "Pre-Diabetes" as ClinicalCategory,
  deviceStatus: "Online" as DeviceState,
  lastSync: "Today, 10:42",
  modelVersion: "svr-v2.3.1",
  subjectCount: 24,
  anomalyRate: 7.5,
  r2: 0.62,
  rmse: 32,
  mae: 24,
};

export const trendLabels = ["07:30", "09:00", "10:30", "12:00", "13:30", "15:00", "16:30", "18:00"];

export const dashboardTrend = {
  labels: trendLabels,
  series: [
    {
      label: "Predicted BG",
      color: "#14B8A6",
      values: [108, 112, 118, 131, 139, 142, 137, 129],
    },
    {
      label: "Reference BG",
      color: "#3B82F6",
      values: [104, 108, 115, 126, 134, 138, 136, 124],
    },
  ],
};

export const recentReadings: Reading[] = [
  {
    id: "r-1048",
    subjectId: "SUB-1048",
    samplingDate: "2026-07-04",
    samplingTime: "08:14",
    fastingHours: 9,
    salivaPh: 6.7,
    salivaViscositySec: 4.2,
    salivaGlucoseMgdl: 10.3,
    bgReferenceMgdl: 109,
    predictedBgMgdl: 112,
    bgCategory: "Normal",
    clinicalCategory: "Normal",
    protoGlucoseRaw: 1048,
    modelVersion: "svr-v2.3.1",
    deviceStatus: "Online",
  },
  {
    id: "r-1081",
    subjectId: "SUB-1081",
    samplingDate: "2026-07-04",
    samplingTime: "09:42",
    fastingHours: 10,
    salivaPh: 6.4,
    salivaViscositySec: 5.1,
    salivaGlucoseMgdl: 12.2,
    bgReferenceMgdl: 129,
    predictedBgMgdl: 134,
    bgCategory: "Pre-Diabetes",
    clinicalCategory: "Pre-Diabetes",
    protoGlucoseRaw: 1112,
    modelVersion: "svr-v2.3.1",
    deviceStatus: "Online",
  },
  {
    id: "r-1094",
    subjectId: "SUB-1094",
    samplingDate: "2026-07-04",
    samplingTime: "10:25",
    fastingHours: 8,
    salivaPh: 6.2,
    salivaViscositySec: 6.0,
    salivaGlucoseMgdl: 14.1,
    bgReferenceMgdl: 148,
    predictedBgMgdl: 152,
    bgCategory: "Diabetes",
    clinicalCategory: "Diabetes",
    protoGlucoseRaw: 1187,
    modelVersion: "svr-v2.3.1",
    deviceStatus: "Syncing",
    anomaly: "Viscosity drift detected",
  },
  {
    id: "r-1120",
    subjectId: "SUB-1120",
    samplingDate: "2026-07-04",
    samplingTime: "11:06",
    fastingHours: 7,
    salivaPh: 6.8,
    salivaViscositySec: 3.9,
    salivaGlucoseMgdl: 9.8,
    bgReferenceMgdl: 101,
    predictedBgMgdl: 105,
    bgCategory: "Normal",
    clinicalCategory: "Normal",
    protoGlucoseRaw: 1004,
    modelVersion: "svr-v2.3.1",
    deviceStatus: "Online",
  },
  {
    id: "r-1133",
    subjectId: "SUB-1133",
    samplingDate: "2026-07-04",
    samplingTime: "12:33",
    fastingHours: 6,
    salivaPh: 6.5,
    salivaViscositySec: 4.8,
    salivaGlucoseMgdl: 11.0,
    bgReferenceMgdl: 122,
    predictedBgMgdl: 126,
    bgCategory: "Normal",
    clinicalCategory: "Normal",
    protoGlucoseRaw: 1077,
    modelVersion: "svr-v2.3.1",
    deviceStatus: "Online",
  },
  {
    id: "r-1147",
    subjectId: "SUB-1147",
    samplingDate: "2026-07-04",
    samplingTime: "13:20",
    fastingHours: 8,
    salivaPh: 6.1,
    salivaViscositySec: 5.9,
    salivaGlucoseMgdl: 13.4,
    bgReferenceMgdl: 157,
    predictedBgMgdl: 163,
    bgCategory: "Diabetes",
    clinicalCategory: "Diabetes",
    protoGlucoseRaw: 1219,
    modelVersion: "svr-v2.3.1",
    deviceStatus: "Offline",
    anomaly: "Packet lost, fallback cache used",
  },
  {
    id: "r-1160",
    subjectId: "SUB-1160",
    samplingDate: "2026-07-04",
    samplingTime: "14:05",
    fastingHours: 9,
    salivaPh: 6.9,
    salivaViscositySec: 3.8,
    salivaGlucoseMgdl: 9.4,
    bgReferenceMgdl: 98,
    predictedBgMgdl: 100,
    bgCategory: "Normal",
    clinicalCategory: "Normal",
    protoGlucoseRaw: 987,
    modelVersion: "svr-v2.3.1",
    deviceStatus: "Online",
  },
  {
    id: "r-1175",
    subjectId: "SUB-1175",
    samplingDate: "2026-07-04",
    samplingTime: "15:12",
    fastingHours: 5,
    salivaPh: 6.6,
    salivaViscositySec: 4.6,
    salivaGlucoseMgdl: 10.7,
    bgReferenceMgdl: 116,
    predictedBgMgdl: 118,
    bgCategory: "Normal",
    clinicalCategory: "Normal",
    protoGlucoseRaw: 1044,
    modelVersion: "svr-v2.3.1",
    deviceStatus: "Online",
  },
  {
    id: "r-1188",
    subjectId: "SUB-1188",
    samplingDate: "2026-07-04",
    samplingTime: "16:48",
    fastingHours: 10,
    salivaPh: 6.3,
    salivaViscositySec: 5.7,
    salivaGlucoseMgdl: 12.8,
    bgReferenceMgdl: 136,
    predictedBgMgdl: 139,
    bgCategory: "Pre-Diabetes",
    clinicalCategory: "Pre-Diabetes",
    protoGlucoseRaw: 1135,
    modelVersion: "svr-v2.3.1",
    deviceStatus: "Syncing",
  },
];

export const alerts = [
  {
    title: "Viscosity drift on SUB-1147",
    tone: "danger",
    detail: "Raw packet dropped once, then recovered from cache. Check the reader probe before the next run.",
  },
  {
    title: "Predicted BG crossed pre-diabetes band",
    tone: "warning",
    detail: "Three samples in the last hour moved above 126 mg/dL. Review the fasting window and collection timing.",
  },
  {
    title: "Device heartbeat is stable",
    tone: "emerald",
    detail: "Prototype has stayed online for 12 hours with sub-200 ms sync latency.",
  },
];

export const quickActions = [
  {
    label: "Sync latest packet",
    description: "Pull the newest hardware payload and append it to the live log.",
  },
  {
    label: "Add manual reading",
    description: "Enter a backup sample from the bench or classroom test run.",
  },
  {
    label: "Export filtered CSV",
    description: "Send the current view to the team for analysis or reporting.",
  },
];

export const deviceChannels = [
  { name: "Saliva probe", state: "Online", value: "4 ms sampling" },
  { name: "Temperature compensation", state: "Online", value: "36.8 C locked" },
  { name: "API endpoint", state: "Online", value: "POST /api/ingest" },
  { name: "Cache queue", state: "Syncing", value: "1 item buffered" },
];

export const subjects: Subject[] = [
  {
    id: "SUB-1048",
    code: "SUB-1048",
    alias: "Atlas",
    cohort: "Pilot A",
    recordsCount: 18,
    latestSampling: "2026-07-04 08:14",
    latestPredictedBgMgdl: 112,
    lastReferenceBgMgdl: 109,
    fastingAverage: 8.7,
    deviceStatus: "Online",
    clinicalCategory: "Normal",
    trendDelta: 3,
    note: "Stable fasting profile with a tight saliva pH band.",
  },
  {
    id: "SUB-1081",
    code: "SUB-1081",
    alias: "Cendana",
    cohort: "Pilot A",
    recordsCount: 16,
    latestSampling: "2026-07-04 09:42",
    latestPredictedBgMgdl: 134,
    lastReferenceBgMgdl: 129,
    fastingAverage: 9.2,
    deviceStatus: "Online",
    clinicalCategory: "Pre-Diabetes",
    trendDelta: 5,
    note: "Needs a longer rest window to compare against post-meal runs.",
  },
  {
    id: "SUB-1094",
    code: "SUB-1094",
    alias: "Nadir",
    cohort: "Pilot B",
    recordsCount: 14,
    latestSampling: "2026-07-04 10:25",
    latestPredictedBgMgdl: 152,
    lastReferenceBgMgdl: 148,
    fastingAverage: 7.8,
    deviceStatus: "Syncing",
    clinicalCategory: "Diabetes",
    trendDelta: 4,
    note: "Highest anomaly density in the pilot set, mostly viscosity spikes.",
  },
  {
    id: "SUB-1120",
    code: "SUB-1120",
    alias: "Bima",
    cohort: "Pilot B",
    recordsCount: 20,
    latestSampling: "2026-07-04 11:06",
    latestPredictedBgMgdl: 105,
    lastReferenceBgMgdl: 101,
    fastingAverage: 8.9,
    deviceStatus: "Online",
    clinicalCategory: "Normal",
    trendDelta: 2,
    note: "Cleanest repeatability across pH and glucose samples.",
  },
  {
    id: "SUB-1133",
    code: "SUB-1133",
    alias: "Savana",
    cohort: "Pilot C",
    recordsCount: 12,
    latestSampling: "2026-07-04 12:33",
    latestPredictedBgMgdl: 126,
    lastReferenceBgMgdl: 122,
    fastingAverage: 6.4,
    deviceStatus: "Online",
    clinicalCategory: "Normal",
    trendDelta: 4,
    note: "Fastest turnaround time during manual entry sessions.",
  },
  {
    id: "SUB-1147",
    code: "SUB-1147",
    alias: "Orion",
    cohort: "Pilot C",
    recordsCount: 11,
    latestSampling: "2026-07-04 13:20",
    latestPredictedBgMgdl: 163,
    lastReferenceBgMgdl: 157,
    fastingAverage: 8.1,
    deviceStatus: "Offline",
    clinicalCategory: "Diabetes",
    trendDelta: 6,
    note: "Investigate packet loss on the reader bridge.",
  },
];

const subjectTimeline = [
  [111, 113, 115, 112, 110, 112],
  [125, 127, 131, 134, 132, 134],
  [141, 145, 149, 151, 153, 152],
  [103, 105, 104, 106, 107, 105],
  [119, 121, 123, 124, 125, 126],
  [156, 159, 161, 164, 162, 163],
];

export const subjectHistories: SubjectHistory[] = subjects.map((subject, index) => {
  const samples = subjectTimeline[index % subjectTimeline.length].map((value, sampleIndex) => ({
    id: `${subject.code.toLowerCase()}-${sampleIndex + 1}`,
    samplingDate: `2026-06-${24 + sampleIndex}`,
    samplingTime: `${8 + sampleIndex}:${sampleIndex === 0 ? "10" : "20"}`,
    fastingHours: 6 + (sampleIndex % 4),
    salivaPh: Number((6.1 + (index % 4) * 0.15 + sampleIndex * 0.03).toFixed(1)),
    salivaViscositySec: Number((3.8 + index * 0.25 + sampleIndex * 0.2).toFixed(1)),
    salivaGlucoseMgdl: Number((9.2 + index * 0.8 + sampleIndex * 0.35).toFixed(1)),
    bgReferenceMgdl: value,
    predictedBgMgdl: value + (sampleIndex % 2 === 0 ? 2 : -1),
    clinicalCategory: (value < 126 ? "Normal" : value < 180 ? "Pre-Diabetes" : "Diabetes") as ClinicalCategory,
    protoGlucoseRaw: 990 + index * 47 + sampleIndex * 9,
    deviceStatus: (sampleIndex === 4 && index === 5 ? "Offline" : "Online") as DeviceState,
    bgCategory: value < 126 ? "Normal" : value < 180 ? "Pre-Diabetes" : "Diabetes",
  }));

  return {
    id: subject.id,
    code: subject.code,
    samples,
  };
});

export const predictions = recentReadings.slice(0, 5).map((reading) => ({
  id: reading.id,
  subjectId: reading.subjectId,
  predictedBgMgdl: reading.predictedBgMgdl,
  bgReferenceMgdl: reading.bgReferenceMgdl,
  clinicalCategory: reading.clinicalCategory,
  modelVersion: reading.modelVersion,
  samplingDate: reading.samplingDate,
  samplingTime: reading.samplingTime,
  delta: reading.predictedBgMgdl - reading.bgReferenceMgdl,
}));

export const analyticsMetrics = [
  { label: "R2", value: "0.62", helper: "Cross-validated on 5 folds" },
  { label: "RMSE", value: "32 mg/dL", helper: "Within the clinical target" },
  { label: "MAE", value: "24 mg/dL", helper: "Stable on repeated fasted tests" },
  { label: "Anomaly rate", value: "7.5%", helper: "Mostly packet or viscosity issues" },
];

export const distributionBuckets = [
  { label: "Normal", count: 11, color: "#10B981" },
  { label: "Pre-Diabetes", count: 8, color: "#3B82F6" },
  { label: "Diabetes", count: 5, color: "#EF4444" },
];

export const featureCorrelation = [
  { label: "saliva_glucose_mgdl", value: 0.78 },
  { label: "saliva_ph", value: -0.42 },
  { label: "saliva_viscosity_sec", value: 0.55 },
  { label: "fasting_hours", value: -0.28 },
  { label: "proto_glucose_raw", value: 0.64 },
];

export const analyticsTrend = {
  labels: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat"],
  values: [110, 114, 118, 129, 138, 142],
};

export const requestLogs = [
  { time: "10:42:11", source: "hardware", status: "accepted", message: "Packet appended to live queue" },
  { time: "10:45:22", source: "manual", status: "validated", message: "Manual reading stored after range check" },
  { time: "10:53:09", source: "hardware", status: "warning", message: "Viscosity exceeded baseline, sample flagged" },
  { time: "11:04:40", source: "hardware", status: "accepted", message: "Prediction emitted and synced to history" },
];

export const modelInfo = {
  name: "SVR regression",
  version: "svr-v2.3.1",
  kernel: "rbf",
  scaler: "StandardScaler",
  trainingSet: "148 samples",
  validationMethod: "5-fold cross validation",
  target: "R2 >= 0.50, RMSE <= 80%, MAE <= 60%",
};

export const settingsConfig = {
  apiEndpoint: "/api/ingest",
  pollInterval: "15 seconds",
  retention: "90 days",
  access: "Team only",
  subjectPrivacy: "Anonymous subject IDs only",
};
