"""Script untuk visualisasi grafik data sampling sensor GlicoSaliva.
Membaca CSV dari ml_pipeline/sampling/ dan menyimpan grafik ke ml_pipeline/grafik/sampling/.
"""

import os
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

SAMPLING_DIR = Path("/home/hendra/projects/pkmGlico/ml_pipeline/sampling")
OUTPUT_DIR = Path("/home/hendra/projects/pkmGlico/ml_pipeline/grafik/sampling")

COLORS = {
    "fru": "#e67e22",  # Orange
    "glu": "#2980b9",  # Blue
    "ph":  "#27ae60",  # Green
}

def plot_voltages_per_dataset(csv_path: Path, out_dir: Path) -> Path:
    """Plot 3 subplots: Vfru, Vglu, VpH untuk satu file CSV."""
    df = pd.read_csv(csv_path)
    out_file = out_dir / f"volt_{csv_path.stem}.png"
    
    fig, axes = plt.subplots(3, 1, figsize=(11, 9), sharex=True)
    fig.patch.set_facecolor('#ffffff')

    # 1. Vfru
    ax_fru = axes[0]
    ax_fru.plot(df['t_detik'], df['Vfru_V'], color=COLORS['fru'], linewidth=1.5, label='Vfru (Fruktosamin)')
    ax_fru.set_ylabel('Vfru (V)', fontsize=11, fontweight='bold', color=COLORS['fru'])
    ax_fru.set_title(f'Tegangan Sensor: {csv_path.name}\nTotal: {len(df)} sampel | Durasi: {df["t_detik"].max():.1f}s', fontsize=12, fontweight='bold', pad=8)
    ax_fru.grid(True, linestyle='--', alpha=0.6)
    ax_fru.legend(loc='upper right')

    # 2. Vglu
    ax_glu = axes[1]
    ax_glu.plot(df['t_detik'], df['Vglu_V'], color=COLORS['glu'], linewidth=1.5, label='Vglu (Glukosa)')
    ax_glu.set_ylabel('Vglu (V)', fontsize=11, fontweight='bold', color=COLORS['glu'])
    ax_glu.grid(True, linestyle='--', alpha=0.6)
    ax_glu.legend(loc='upper right')

    # 3. VpH
    ax_ph = axes[2]
    ax_ph.plot(df['t_detik'], df['VpH_V'], color=COLORS['ph'], linewidth=1.5, label='VpH (pH)')
    ax_ph.set_ylabel('VpH (V)', fontsize=11, fontweight='bold', color=COLORS['ph'])
    ax_ph.set_xlabel('Waktu (detik)', fontsize=11, fontweight='bold')
    ax_ph.grid(True, linestyle='--', alpha=0.6)
    ax_ph.legend(loc='upper right')

    plt.tight_layout()
    plt.savefig(out_file, dpi=300)
    plt.close(fig)
    return out_file

def plot_individual_parameters(csv_path: Path, param_dir: Path):
    """Plot grafik terpisah per parameter (Vfru, Vglu, VpH)."""
    df = pd.read_csv(csv_path)
    params = [
        ("Vfru_V", "Vfru (Fruktosamin)", COLORS["fru"], "Vfru"),
        ("Vglu_V", "Vglu (Glukosa)", COLORS["glu"], "Vglu"),
        ("VpH_V", "VpH (pH)", COLORS["ph"], "VpH")
    ]
    for col, label, color, prefix in params:
        out_file = param_dir / f"{prefix}_{csv_path.stem}.png"
        fig, ax = plt.subplots(figsize=(10, 4.5))
        fig.patch.set_facecolor('#ffffff')
        ax.plot(df['t_detik'], df[col], color=color, linewidth=1.5, label=label)
        ax.set_title(f'{label} - {csv_path.name}', fontsize=12, fontweight='bold')
        ax.set_xlabel('Waktu (detik)', fontsize=10, fontweight='bold')
        ax.set_ylabel(f'{col} (Volt)', fontsize=10, fontweight='bold')
        ax.grid(True, linestyle='--', alpha=0.6)
        ax.legend(loc='upper right')
        plt.tight_layout()
        plt.savefig(out_file, dpi=300)
        plt.close(fig)

def plot_parameter_comparisons(csv_files: list[Path], out_dir: Path):
    """Plot komparasi gabungan seluruh sesi untuk masing-masing parameter."""
    params = [
        ("Vfru_V", "Tegangan Fruktosamin (Vfru)", COLORS["fru"], "volt_fru_comparison.png"),
        ("Vglu_V", "Tegangan Glukosa (Vglu)", COLORS["glu"], "volt_glu_comparison.png"),
        ("VpH_V", "Tegangan pH (VpH)", COLORS["ph"], "volt_ph_comparison.png"),
    ]
    for col, title, base_color, fname in params:
        out_file = out_dir / fname
        fig, ax = plt.subplots(figsize=(13, 7))
        fig.patch.set_facecolor('#ffffff')
        
        for f in csv_files:
            df = pd.read_csv(f)
            short_name = f.stem.replace("glicovia_", "")
            ax.plot(df['t_detik'], df[col], linewidth=1.3, alpha=0.85, label=short_name)

        ax.set_title(f'Komparasi Semua Sesi: {title}', fontsize=13, fontweight='bold', pad=10)
        ax.set_xlabel('Waktu (detik)', fontsize=11, fontweight='bold')
        ax.set_ylabel(f'{col} (Volt)', fontsize=11, fontweight='bold')
        ax.grid(True, linestyle='--', alpha=0.6)
        ax.legend(bbox_to_anchor=(1.02, 1), loc='upper left', fontsize=9)
        plt.tight_layout()
        plt.savefig(out_file, dpi=300)
        plt.close(fig)

def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    param_dir = OUTPUT_DIR / "per_parameter"
    param_dir.mkdir(parents=True, exist_ok=True)

    csv_files = sorted(SAMPLING_DIR.glob("*.csv"))
    if not csv_files:
        print(f"Tidak ada file CSV di {SAMPLING_DIR}")
        return

    print(f"Memproses visualisasi tegangan untuk {len(csv_files)} file CSV...")
    for f in csv_files:
        out = plot_voltages_per_dataset(f, OUTPUT_DIR)
        plot_individual_parameters(f, param_dir)
        print(f"  [OK] Volt 3-in-1: {out.name} & individual parameter files")

    plot_parameter_comparisons(csv_files, OUTPUT_DIR)
    print("  [OK] Komparasi seluruh sesi per parameter (Vfru, Vglu, VpH)")
    print(f"Selesai! Disimpan di: {OUTPUT_DIR}")

if __name__ == "__main__":
    main()
