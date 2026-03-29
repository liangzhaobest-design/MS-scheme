from __future__ import annotations

import csv
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))

from ms_scheme.evaluation import BenchmarkRecord, run_benchmark_cl, run_benchmark_csas, run_benchmark_ibms, run_benchmark_ni

OUT_DIR = Path("reports")
OUT_DIR.mkdir(parents=True, exist_ok=True)


def _save_csv(records: list[BenchmarkRecord], path: Path) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow([
            "scheme", "n", "q", "signer_count", "rounds",
            "key_extract_ms_mean", "partial_sign_ms_mean", "aggregate_ms_mean", "verify_ms_mean",
            "verify_success_rate", "signature_size_bytes",
        ])
        for r in records:
            w.writerow([
                r.scheme, r.n, r.q, r.signer_count, r.rounds,
                f"{r.key_extract_ms_mean:.6f}", f"{r.partial_sign_ms_mean:.6f}", f"{r.aggregate_ms_mean:.6f}",
                f"{r.verify_ms_mean:.6f}", f"{r.verify_success_rate:.4f}", r.signature_size_bytes,
            ])


def _svg_line_chart(path: Path, title: str, x_label: str, y_label: str, series: list[tuple[str, list[float], list[float]]]) -> None:
    width, height = 900, 500
    left, right, top, bottom = 80, 20, 50, 60
    plot_w = width - left - right
    plot_h = height - top - bottom

    all_x = [x for _, xs, _ in series for x in xs]
    all_y = [y for _, _, ys in series for y in ys]
    min_x, max_x = min(all_x), max(all_x)
    min_y, max_y = 0.0, max(all_y) * 1.15 if max(all_y) > 0 else 1.0

    def tx(x: float) -> float:
        return left + ((x - min_x) / (max_x - min_x) * plot_w if max_x != min_x else plot_w / 2)

    def ty(y: float) -> float:
        return top + plot_h - (y - min_y) / (max_y - min_y) * plot_h

    colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd"]
    parts: list[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        f'<text x="{width/2}" y="28" text-anchor="middle" font-size="20" font-family="Arial">{title}</text>',
    ]

    for i in range(6):
        yv = min_y + (max_y - min_y) * i / 5
        ypx = ty(yv)
        parts.append(f'<line x1="{left}" y1="{ypx:.1f}" x2="{left+plot_w}" y2="{ypx:.1f}" stroke="#eeeeee"/>')
        parts.append(f'<text x="{left-10}" y="{ypx+4:.1f}" text-anchor="end" font-size="11" font-family="Arial">{yv:.1f}</text>')

    for xv in sorted(set(all_x)):
        xpx = tx(xv)
        parts.append(f'<line x1="{xpx:.1f}" y1="{top}" x2="{xpx:.1f}" y2="{top+plot_h}" stroke="#f3f3f3"/>')
        parts.append(f'<text x="{xpx:.1f}" y="{top+plot_h+20}" text-anchor="middle" font-size="11" font-family="Arial">{xv:g}</text>')

    parts.append(f'<line x1="{left}" y1="{top+plot_h}" x2="{left+plot_w}" y2="{top+plot_h}" stroke="#333"/>')
    parts.append(f'<line x1="{left}" y1="{top}" x2="{left}" y2="{top+plot_h}" stroke="#333"/>')

    for idx, (name, xs, ys) in enumerate(series):
        c = colors[idx % len(colors)]
        points = " ".join(f"{tx(x):.1f},{ty(y):.1f}" for x, y in zip(xs, ys))
        parts.append(f'<polyline points="{points}" fill="none" stroke="{c}" stroke-width="2.5"/>')
        for x, y in zip(xs, ys):
            parts.append(f'<circle cx="{tx(x):.1f}" cy="{ty(y):.1f}" r="3.5" fill="{c}"/>')
        lx, ly = left + plot_w - 280, top + 20 + idx * 20
        parts.append(f'<line x1="{lx}" y1="{ly}" x2="{lx+20}" y2="{ly}" stroke="{c}" stroke-width="2.5"/>')
        parts.append(f'<text x="{lx+28}" y="{ly+4}" font-size="12" font-family="Arial">{name}</text>')

    parts.append(f'<text x="{left+plot_w/2}" y="{height-15}" text-anchor="middle" font-size="13" font-family="Arial">{x_label}</text>')
    parts.append(f'<text x="20" y="{top+plot_h/2}" transform="rotate(-90,20,{top+plot_h/2})" text-anchor="middle" font-size="13" font-family="Arial">{y_label}</text>')
    parts.append('</svg>')
    path.write_text("\n".join(parts), encoding="utf-8")


def _plot_metric_compare(records: list[BenchmarkRecord], path: Path, metric: str, title: str, y_label: str) -> None:
    schemes = ["IBMS-NTRU", "CL-NTRU-MS-IRS", "NI-IBMS-PKA", "CLSAS-NTRU"]
    series = []
    for scheme in schemes:
        recs = sorted([r for r in records if r.scheme == scheme and r.n == 107 and r.q == 2048], key=lambda x: x.signer_count)
        x = [r.signer_count for r in recs]
        y = [getattr(r, metric) for r in recs]
        series.append((scheme, x, y))
    _svg_line_chart(path, title, "Number of signers", y_label, series)


def _write_markdown(records: list[BenchmarkRecord], path: Path) -> None:
    lines = [
        "# Comparative Evaluation Report",
        "",
        "## Protocol",
        "- Baseline-1: IBMS-NTRU.",
        "- Baseline-2: CL-NTRU-MS-IRS.",
        "- New implementation-1: NI-IBMS-PKA (non-interactive identity-based multi-signature with public-key aggregation).",
        "- New implementation-2: CLSAS-NTRU (certificateless sequential aggregate signature on NTRU lattice).",
        "- Metrics are averaged over 20 rounds.",
        "",
        "## Table 1. Runtime comparison (n=107, q=2048)",
        "",
        "| Scheme | #Signers | Sign(ms/signer) | Aggregate(ms) | Verify(ms) | Success | Size(B) |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    rows = sorted([r for r in records if r.n == 107 and r.q == 2048], key=lambda x: (x.scheme, x.signer_count))
    for r in rows:
        lines.append(f"| {r.scheme} | {r.signer_count} | {r.partial_sign_ms_mean:.3f} | {r.aggregate_ms_mean:.3f} | {r.verify_ms_mean:.3f} | {r.verify_success_rate:.2f} | {r.signature_size_bytes} |")

    lines.extend(["", "## Table 2. Parameter sensitivity comparison (8 signers)", "", "| Scheme | n | Verify(ms) | Size(B) |", "|---|---:|---:|---:|"])
    rows2 = sorted([r for r in records if r.signer_count == 8], key=lambda x: (x.scheme, x.n))
    for r in rows2:
        lines.append(f"| {r.scheme} | {r.n} | {r.verify_ms_mean:.3f} | {r.signature_size_bytes} |")

    lines.extend(["", "## Figures", "", "![Verify comparison](verify_comparison.svg)", "", "![Size comparison](size_comparison.svg)"])
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    records: list[BenchmarkRecord] = []
    for runner in [run_benchmark_ibms, run_benchmark_cl, run_benchmark_ni, run_benchmark_csas]:
        for signer_count in [2, 4, 8, 16]:
            records.append(runner(n=107, q=2048, signer_count=signer_count, rounds=20))
        for n in [167, 251]:
            records.append(runner(n=n, q=2048, signer_count=8, rounds=20))

    _save_csv(records, OUT_DIR / "benchmark_results.csv")
    _plot_metric_compare(records, OUT_DIR / "verify_comparison.svg", "verify_ms_mean", "Verification runtime comparison", "Verify time (ms)")
    _plot_metric_compare(records, OUT_DIR / "size_comparison.svg", "signature_size_bytes", "Signature size comparison", "Signature size (bytes)")
    _write_markdown(records, OUT_DIR / "evaluation_report.md")


if __name__ == "__main__":
    main()
