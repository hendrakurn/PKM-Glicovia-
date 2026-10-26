# Graph Report - hasil_artikel  (2026-10-22)

## Corpus Check
- 4 files · ~35,342 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 12 nodes · 8 edges · 4 communities (1 shown, 3 thin omitted)
- Extraction: 100% EXTRACTED · 0% INFERRED · 0% AMBIGUOUS
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `3a9f6358`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- buat_grafik.py
- buat_grafik_klasifikasi.py
- hasil_pembahasan.md
- hasil_pembahasan_2kelas.md

## God Nodes (most connected - your core abstractions)
1. `settle()` - 2 edges
2. `Grafik Hasil dan Pembahasan artikel Glicovia (Gambar 9-11) dari rekaman sensor…` - 1 edges
3. `Waktu pertama sinyal masuk dan bertahan dalam +-(1-frac)*|final-awal| dari…` - 1 edges
4. `Eksplorasi 2 kelas (Normal vs Diabetes): tiap pembacaan fase stabil dianggap…` - 1 edges
5. `Respons Sensor terhadap Dua Kelas Sampel` - 1 edges
6. `Klasifikasi Dua Kelas Berbasis SVM pada Pembacaan Sensor` - 1 edges

## Surprising Connections (you probably didn't know these)
- None detected - all connections are within the same source files.

## Import Cycles
- None detected.

## Communities (4 total, 3 thin omitted)

### Community 0 - "buat_grafik.py"
Cohesion: 0.40
Nodes (3): Grafik Hasil dan Pembahasan artikel Glicovia (Gambar 9-11) dari rekaman sensor…, Waktu pertama sinyal masuk dan bertahan dalam +-(1-frac)*|final-awal| dari…, settle()

## Knowledge Gaps
- **2 isolated node(s):** `Respons Sensor terhadap Dua Kelas Sampel`, `Klasifikasi Dua Kelas Berbasis SVM pada Pembacaan Sensor`
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 9 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **3 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What connects `Respons Sensor terhadap Dua Kelas Sampel`, `Klasifikasi Dua Kelas Berbasis SVM pada Pembacaan Sensor` to the rest of the system?**
  _2 weakly-connected nodes found - possible documentation gaps or missing edges._