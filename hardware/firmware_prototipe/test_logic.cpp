// Uji logika murni:  g++ -std=c++11 -Wall -o /tmp/test_logic test_logic.cpp && /tmp/test_logic
#include <assert.h>
#include "logic.h"

static bool near(float a, float b, float tol) { return fabsf(a - b) <= tol; }

int main() {
  // regresi pH: V = -0.0296*pH + 0.205 (3 buffer)
  Pt ph[3] = {{4.01f, 0.0863f}, {6.86f, 0.0020f}, {9.18f, -0.0667f}};
  float m, c, r2;
  assert(fitLine(ph, 3, &m, &c, &r2));
  assert(m < 0 && r2 > 0.99f);
  // konversi bolak-balik
  float v = m * 6.86f + c;
  assert(near(phFromV(v, m, c), 6.86f, 1e-3f));

  // regresi glukosa: I = 250*C + 30 nA
  Pt g[4] = {{0, 30}, {1, 280}, {2, 530}, {5, 1280}};
  assert(fitLine(g, 4, &m, &c, &r2));
  assert(near(m, 250, 0.01f) && near(c, 30, 0.01f) && r2 > 0.9999f);
  assert(near(gluFromI(780, c, m), 3.0f, 1e-3f));

  // x sama semua -> gagal; titik kurang -> gagal
  Pt same[3] = {{1, 1}, {1, 2}, {1, 3}};
  assert(!fitLine(same, 3, &m, &c, &r2));
  assert(!fitLine(g, 1, &m, &c, &r2));

  // trimmed mean menolak pencilan
  float a[8] = {1, 1, 1, 1, 1, 1, 100, -100};
  assert(near(trimMean(a, 8), 1.0f, 1e-6f));
  assert(isnan(trimMean(a, 0)));

  // JSON angka: NaN -> null
  char b[16];
  assert(strcmp(fmtNum(b, sizeof b, NAN, 2), "null") == 0);
  assert(strcmp(fmtNum(b, sizeof b, 6.8249f, 2), "6.82") == 0);

  // parser balasan prediksi (dengan dan tanpa spasi)
  float x; char s[16];
  const char* j1 = "{\"device_code\":\"GLICO-01\",\"glucose_estimate\":150.94,\"clinical_category\":\"Diabetes\",\"confidence_score\":0.9938}";
  const char* j2 = "{\"glucose_estimate\": 88.0, \"clinical_category\": \"Normal\", \"confidence_score\": 0.8}";
  assert(jsonNum(j1, "glucose_estimate", &x) && near(x, 150.94f, 1e-3f));
  assert(jsonNum(j1, "confidence_score", &x) && near(x, 0.9938f, 1e-4f));
  assert(jsonStr(j1, "clinical_category", s, sizeof s) && strcmp(s, "Diabetes") == 0);
  assert(jsonNum(j2, "glucose_estimate", &x) && near(x, 88.0f, 1e-3f));
  assert(jsonStr(j2, "clinical_category", s, sizeof s) && strcmp(s, "Normal") == 0);
  assert(!jsonNum(j2, "tidak_ada", &x));

  puts("OK semua");
  return 0;
}
