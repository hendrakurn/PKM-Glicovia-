// Membuat hasil_pembahasan_v2.docx dari hasil_pembahasan_v2.md + gambar PNG di folder ini.
const fs = require("fs");
const path = require("path");
const {
  Document, Packer, Paragraph, TextRun, ImageRun, Table, TableRow, TableCell,
  AlignmentType, WidthType, BorderStyle, ShadingType, HeadingLevel,
} = require("docx");

const FONT = "Times New Roman";
const NAMA = process.argv[2] || "hasil_pembahasan_v2";
const md = fs.readFileSync(path.join(__dirname, NAMA + ".md"), "utf8").split("\n");

// "*miring*" dan "**tebal**" -> TextRun
function runs(text, size = 24) {
  return text.split(/(\*\*[^*]+\*\*|\*[^*]+\*)/).filter(Boolean).map((s) => {
    if (s.startsWith("**")) return new TextRun({ text: s.slice(2, -2), bold: true, font: FONT, size });
    if (s.startsWith("*")) return new TextRun({ text: s.slice(1, -1), italics: true, font: FONT, size });
    return new TextRun({ text: s, font: FONT, size });
  });
}
function pngSize(file) {
  const b = fs.readFileSync(file);
  return [b.readUInt32BE(16), b.readUInt32BE(20)];
}
function figure(file, widthIn) {
  const [w, h] = pngSize(file);
  const px = Math.round(widthIn * 96);
  return new Paragraph({
    alignment: AlignmentType.CENTER, keepNext: true, spacing: { before: 120, after: 60 },
    children: [new ImageRun({ type: "png", data: fs.readFileSync(file), transformation: { width: px, height: Math.round(px * h / w) },
      altText: { title: path.basename(file), description: path.basename(file), name: path.basename(file) } })],
  });
}
const WIDTH_IN = { "ringkas_gambar9": 5.6, "ringkas_gambar10": 6.0, "ringkas_gambar11": 4.2, "gambar9": 5.6, "gambar10": 6.0, "gambar11": 4.2, "gambar12": 6.2, "gambar13": 5.4,
  "final_gambar11": 6.0, "final_gambar12": 6.0 };

const thin = { style: BorderStyle.SINGLE, size: 4, color: "808080" };
const borders = { top: thin, bottom: thin, left: thin, right: thin };
const COLS8 = [700, 1100, 1000, 900, 1500, 1226, 1000, 1600]; // jumlah 9026 (tabel 8 kolom)
function table(lines) {
  const rows = lines.filter((l) => !/^\|[-| ]+\|$/.test(l)).map((l) => l.split("|").slice(1, -1).map((c) => c.trim()));
  const n = rows[0].length;
  const COLS = n === 8 ? COLS8 : Array.from({ length: n }, (_, i) => (i === 0 ? 9026 - Math.floor(9026 / n) * (n - 1) : Math.floor(9026 / n)));
  return new Table({
    width: { size: 9026, type: WidthType.DXA }, columnWidths: COLS,
    rows: rows.map((r, i) => new TableRow({
      tableHeader: i === 0, cantSplit: true,
      children: r.map((c, j) => new TableCell({
        width: { size: COLS[j], type: WidthType.DXA }, borders,
        shading: i === 0 ? { fill: "D9E2F3", type: ShadingType.CLEAR, color: "auto" } : undefined,
        margins: { top: 50, bottom: 50, left: 80, right: 80 },
        children: [new Paragraph({ alignment: j < 2 ? AlignmentType.LEFT : AlignmentType.CENTER,
          children: [new TextRun({ text: c, bold: i === 0, font: FONT, size: 20 })] })],
      })),
    })),
  });
}

const kids = [];
for (let i = 0; i < md.length; i++) {
  const l = md[i];
  if (!l.trim()) continue;
  if (l.startsWith("### ")) {
    kids.push(new Paragraph({ keepNext: true, spacing: { before: 240, after: 120 },
      children: [new TextRun({ text: l.slice(4), bold: true, font: FONT, size: 24 })] }));
  } else if (l.startsWith("## ")) {
    kids.push(new Paragraph({ heading: HeadingLevel.HEADING_1, spacing: { before: 0, after: 200 },
      children: [new TextRun({ text: l.slice(3), bold: true, font: FONT, size: 28 })] }));
  } else if (l.startsWith("|")) {
    const t = []; while (i < md.length && md[i].startsWith("|")) t.push(md[i++]); i--;
    kids.push(table(t), new Paragraph({ spacing: { after: 160 }, children: [] }));
  } else if (l.startsWith("![")) {
    const f = l.match(/\(([^)]+)\)/)[1];
    kids.push(figure(path.join(__dirname, f), WIDTH_IN[Object.keys(WIDTH_IN).find((k) => f.startsWith(k))]));
  } else if (l.startsWith("**Tabel") || l.startsWith("**Gambar")) {
    const isTabel = l.startsWith("**Tabel");
    kids.push(new Paragraph({ alignment: isTabel ? AlignmentType.LEFT : AlignmentType.JUSTIFIED, keepNext: isTabel,
      spacing: { before: isTabel ? 120 : 0, after: isTabel ? 80 : 240 }, children: runs(l, 20) }));
  } else {
    kids.push(new Paragraph({ alignment: AlignmentType.JUSTIFIED, spacing: { after: 200, line: 360 },
      indent: { firstLine: 567 }, children: runs(l) }));
  }
}

const doc = new Document({
  creator: "Glicovia", title: "Glicovia - Hasil dan Pembahasan v2",
  styles: { default: { document: { run: { font: FONT, size: 24 } } },
    paragraphStyles: [{ id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
      run: { size: 28, bold: true, font: FONT }, paragraph: { spacing: { before: 0, after: 200 }, outlineLevel: 0 } }] },
  sections: [{ properties: { page: { size: { width: 11906, height: 16838 }, margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 } } },
    children: kids }],
});
Packer.toBuffer(doc).then((b) => { fs.writeFileSync(path.join(__dirname, NAMA + ".docx"), b); console.log("ok"); });
