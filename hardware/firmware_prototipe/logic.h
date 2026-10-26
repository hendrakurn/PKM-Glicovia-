// Logika murni (tanpa Arduino) supaya bisa diuji di PC: lihat test_logic.cpp
#pragma once
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

struct Pt { float x, y; };

inline void sortf(float* a, int n) {
  for (int i = 1; i < n; i++) {
    float k = a[i]; int j = i - 1;
    while (j >= 0 && a[j] > k) { a[j + 1] = a[j]; j--; }
    a[j + 1] = k;
  }
}

// Rata-rata 50% tengah. MENGURUTKAN array a di tempat.
inline float trimMean(float* a, int n) {
  if (n <= 0) return NAN;
  sortf(a, n);
  int lo = n / 4, hi = n - n / 4;
  float s = 0;
  for (int i = lo; i < hi; i++) s += a[i];
  return s / (hi - lo);
}

inline float sdev(const float* a, int n) {
  if (n < 2) return 0;
  double m = 0, s = 0;
  for (int i = 0; i < n; i++) m += a[i];
  m /= n;
  for (int i = 0; i < n; i++) s += (a[i] - m) * (a[i] - m);
  return (float)sqrt(s / (n - 1));
}

// Regresi linear y = s*x + c. false bila titik < 2 atau semua x sama.
inline bool fitLine(const Pt* p, int n, float* s, float* c, float* r2) {
  if (n < 2) return false;
  double sx = 0, sy = 0, sxx = 0, sxy = 0, syy = 0;
  for (int i = 0; i < n; i++) {
    sx += p[i].x; sy += p[i].y;
    sxx += (double)p[i].x * p[i].x; sxy += (double)p[i].x * p[i].y; syy += (double)p[i].y * p[i].y;
  }
  double dx = n * sxx - sx * sx;
  if (fabs(dx) < 1e-12) return false;
  double slope = (n * sxy - sx * sy) / dx;
  double icpt = (sy - slope * sx) / n;
  double dy = n * syy - sy * sy;
  double r = (dy < 1e-18) ? 1.0 : (n * sxy - sx * sy) / sqrt(dx * dy);
  *s = (float)slope; *c = (float)icpt; *r2 = (float)(r * r);
  return true;
}

inline float phFromV(float v, float m, float c) { return (v - c) / m; }   // V = m*pH + c
inline float gluFromI(float i, float b, float a) { return (i - b) / a; }  // I = a*C + b

// Angka untuk JSON; "null" bila NaN/Inf supaya JSON tetap valid.
inline const char* fmtNum(char* buf, size_t sz, float v, int dec) {
  if (!isfinite(v)) snprintf(buf, sz, "null");
  else snprintf(buf, sz, "%.*f", dec, v);
  return buf;
}

// Ambil angka dari JSON datar: "key": 12.3  (spasi setelah ':' boleh ada)
inline bool jsonNum(const char* js, const char* key, float* out) {
  char pat[48];
  snprintf(pat, sizeof pat, "\"%s\"", key);
  const char* p = strstr(js, pat);
  if (!p) return false;
  p = strchr(p + strlen(pat), ':');
  if (!p) return false;
  p++;
  while (*p == ' ') p++;
  char* end;
  double v = strtod(p, &end);
  if (end == p) return false;
  *out = (float)v;
  return true;
}

inline bool jsonStr(const char* js, const char* key, char* out, size_t sz) {
  char pat[48];
  snprintf(pat, sizeof pat, "\"%s\"", key);
  const char* p = strstr(js, pat);
  if (!p) return false;
  p = strchr(p + strlen(pat), ':');
  if (!p) return false;
  p++;
  while (*p == ' ') p++;
  if (*p != '"') return false;
  p++;
  size_t i = 0;
  while (*p && *p != '"' && i + 1 < sz) out[i++] = *p++;
  out[i] = 0;
  return true;
}
