# Setup Graphify Dari Nol

Dokumen ini menjelaskan cara memasang dan memakai Graphify agar AI agent bisa memahami struktur project lewat knowledge graph, sekaligus cara membuka graph lewat interface visual.

Project contoh:

```bash
/home/hendra/projects/solusi247/dokProjekLangchain-1
```

## 1. Apa Itu Graphify

Graphify adalah tool untuk mengubah folder project menjadi knowledge graph. Graph ini bisa dipakai untuk:

- melihat hubungan antar file, fungsi, class, dan konsep project;
- membantu AI agent menjawab pertanyaan tentang arsitektur project;
- membuka visualisasi graph lewat file HTML;
- menjalankan query seperti `graphify query`, `graphify path`, dan `graphify explain`.

Output utama Graphify biasanya ada di folder:

```bash
graphify-out/
```

Isi pentingnya:

```text
graphify-out/
  graph.html       # interface visual graph
  graph.json       # data graph mentah untuk agent/tool
  GRAPH_REPORT.md  # ringkasan hasil analisis graph, jika dibuat
  manifest.json    # cache/index untuk update incremental
```

## 2. Prasyarat

Pastikan Python sudah ada:

```bash
python3 --version
```

Disarankan memakai virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

Kalau memakai Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

## 3. Install Graphify

Pilih salah satu cara.

### Opsi A: Install Dengan pip di Virtualenv

```bash
pip install graphifyy
```

### Opsi B: Install Dengan uv

```bash
uv tool install graphifyy
```

### Opsi C: Install Dengan pipx

```bash
pipx install graphifyy
```

Cek apakah command sudah tersedia:

```bash
graphify --help
```

## 4. Masuk Ke Folder Project

```bash
cd /home/hendra/projects/solusi247/dokProjekLangchain-1
```

Pastikan isi project terlihat:

```bash
ls -la
```

## 5. Generate Graph Pertama Kali

Jalankan:

```bash
graphify .
```

Perintah ini akan membaca file yang didukung, mengekstrak struktur project, membuat graph, dan menyimpan hasilnya ke `graphify-out/`.

Kalau ingin hasil lebih detail:

```bash
graphify . --mode deep
```

Catatan:

- Untuk code, Graphify bisa membaca struktur secara AST tanpa API key.
- Untuk dokumen, paper, atau image, Graphify bisa memakai semantic extraction.
- Jika ingin semantic extraction lewat Gemini, set `GEMINI_API_KEY` atau `GOOGLE_API_KEY`.

Contoh:

```bash
export GEMINI_API_KEY="isi_api_key_kamu"
```

Graphify tidak perlu `OPENAI_API_KEY` atau `ANTHROPIC_API_KEY` untuk proses dasarnya.

## 6. Buka Interface Visual Graph

Setelah graph dibuat, buka file ini di browser:

```bash
graphify-out/graph.html
xdg-open graphify-out/graph.html
```

Di project ini path lengkapnya:

```bash
/home/hendra/projects/solusi247/dokProjekLangchain-1/graphify-out/graph.html
```

File HTML ini bisa dibuka langsung. Tidak perlu menjalankan web server.

Kalau `graph.html` belum ada, generate ulang:

```bash
graphify export html
```

## 7. Pakai Graphify Untuk Bertanya Tentang Project

Setelah `graphify-out/graph.json` ada, kamu bisa bertanya ke graph:

```bash
graphify query "jelaskan struktur project ini"
```

Contoh query lain:

```bash
graphify query "bagaimana alur data dari ingest.py sampai chat.py menjawab user?"
graphify explain "tanya_hgrid"
graphify path "chat.py" "ingest.py"
```

Penjelasan command:

- `graphify query "..."`
  Untuk pertanyaan umum tentang project.
- `graphify explain "..."`
  Untuk menjelaskan node tertentu, misalnya nama fungsi/class/file.
- `graphify path "A" "B"`
  Untuk mencari hubungan antara dua node/konsep.

## 8. Integrasi Dengan AI Agent

Agar AI agent memakai graph ini saat membaca project, project perlu punya aturan agent.

Di project ini sudah ada:

```text
.agents/rules/graphify.md
.agents/workflows/graphify.md
```

Artinya, saat kamu bertanya tentang struktur project, agent diarahkan untuk memakai:

```bash
graphify query "<pertanyaan>"
```

Contoh pertanyaan ke agent:

```text
Jelaskan struktur project ini pakai Graphify.
```

```text
Trace alur dari proses ingest dokumen sampai chat menjawab user.
```

```text
Apa fungsi utama di project ini dan file mana yang saling berkaitan?
```

## 9. Update Graph Setelah Code Berubah

Kalau kamu mengubah file project, update graph:

```bash
graphify . --update
```

Lalu regenerate interface:

```bash
graphify export html
```

Untuk project yang sering berubah, lakukan ini setelah perubahan besar agar AI agent tidak membaca graph yang sudah stale.

## 10. Workflow Harian Yang Disarankan

Untuk penggunaan normal:

```bash
cd /home/hendra/projects/solusi247/dokProjekLangchain-1
source venv/bin/activate
graphify . --update
graphify export html
```

Lalu tanyakan ke graph:

```bash
graphify query "apa saja komponen utama project ini?"
```

Atau buka visual:

```bash
graphify-out/graph.html
```

## 11. Status Graphify Di Project Ini

Saat dokumen ini dibuat, project ini sudah punya:

```text
.agents/rules/graphify.md
.agents/workflows/graphify.md
graphify-out/graph.json
graphify-out/graph.html
graphify-out/manifest.json
```

Graph yang sudah ada saat ini membaca file utama:

```text
chat.py
ingest.py
```

Ringkasan struktur yang terlihat:

- `ingest.py` mengambil dokumentasi HGrid247 dari web, melakukan chunking, membuat embedding, lalu menyimpan data ke Qdrant collection `hgrid247_docs`.
- `chat.py` membaca collection `hgrid247_docs` dari Qdrant, mencari dokumen relevan, lalu mengirim konteks ke Gemini.
- Fungsi utama untuk tanya jawab adalah `tanya_hgrid()` di `chat.py`.

Jika ingin Graphify juga membaca dokumen seperti `step.md`, `implemetation.md`, atau `PRODUCT.md`, jalankan ulang:

```bash
graphify . --mode deep
graphify export html
```

## 12. Troubleshooting

### Command `graphify` tidak ditemukan

Aktifkan virtualenv dulu:

```bash
source venv/bin/activate
```

Lalu cek:

```bash
which graphify
```

Kalau masih tidak ada:

```bash
pip install graphifyy
```

### `graph.html` belum ada

Jalankan:

```bash
graphify export html
```

### Graph terlalu kecil

Kemungkinan Graphify baru membaca sedikit file, atau file tertentu belum terdeteksi. Jalankan ulang:

```bash
graphify . --mode deep
```

Lalu cek output:

```bash
ls -la graphify-out
```

### Hubungan antar file belum muncul

Graphify lebih mudah mendeteksi hubungan langsung seperti import, function call, class, dan reference eksplisit.

Kalau dua file terhubung lewat layanan eksternal, misalnya sama-sama memakai collection Qdrant `hgrid247_docs`, hubungan itu mungkin tidak selalu muncul sebagai edge langsung. Solusinya:

- tambahkan dokumentasi arsitektur singkat di Markdown;
- jelaskan alur antar komponen secara eksplisit;
- jalankan `graphify . --mode deep`.

Contoh file dokumentasi yang membantu:

```text
ARCHITECTURE.md
```

Isi minimal:

```markdown
# Architecture

ingest.py mengambil dokumentasi HGrid247, membuat embedding, dan menyimpan chunk ke Qdrant collection hgrid247_docs.

chat.py membaca collection hgrid247_docs dari Qdrant, melakukan similarity search, lalu mengirim konteks ke Gemini lewat fungsi tanya_hgrid().
```

Setelah itu:

```bash
graphify . --update
graphify export html
```

## 13. Command Ringkas

Setup pertama:

```bash
python3 -m venv venv
source venv/bin/activate
pip install graphifyy
graphify .
graphify export html
```

Pemakaian harian:

```bash
source venv/bin/activate
graphify . --update
graphify query "jelaskan struktur project ini"
```

Buka visual:

```bash
graphify-out/graph.html
```



Kalau ingin file Markdown seperti step.md, implemetation.md, PRODUCT.md, dan
  GRAPHIFY_SETUP.md ikut dianalisis lebih baik, pakai Gemini key:

  pip install 'graphifyy[gemini]'
  export GEMINI_API_KEY="isi_api_key_kamu"
  graphify . --mode deep
  graphify export html


Supaya hubungan ingest.py dan chat.py lebih mudah dipahami Graphify, buat file
  ARCHITECTURE.md yang menjelaskan alurnya secara eksplisit, lalu update graph:

  graphify . --update
  graphify export html


graphify install --platform antigravity
graphify install --platform codex

pip install "graphify[gemini]" --force


1. uv tool install graphifyy
2. graphify --help
3. graphify codex install
4. graphify antigravity install 
5. export GEMINI_API_KEY="isi_api_key_kamu"
6. graphify update .
7. 