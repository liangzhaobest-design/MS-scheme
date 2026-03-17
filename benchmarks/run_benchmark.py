from __future__ import annotations

import csv
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))

from ms_scheme.evaluation import BenchmarkRecord, run_benchmark

OUT_DIR = Path("reports")
OUT_DIR.mkdir(parents=True, exist_ok=True)


def _save_csv(records: list[BenchmarkRecord], path: Path) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(
            [
                "n",
                "q",
                "signer_count",
                "rounds",
                "key_extract_ms_mean",
                "key_extract_ms_std",
                "partial_sign_ms_mean",
                "partial_sign_ms_std",
                "aggregate_ms_mean",
                "aggregate_ms_std",
                "verify_ms_mean",
                "verify_ms_std",
                "verify_success_rate",
                "signature_size_bytes",
            ]
        )
        for r in records:
            w.writerow(
                [
                    r.n,
                    r.q,
                    r.signer_count,
                    r.rounds,
                    f"{r.key_extract_ms_mean:.6f}",
                    f"{r.key_extract_ms_std:.6f}",
                    f"{r.partial_sign_ms_mean:.6f}",
                    f"{r.partial_sign_ms_std:.6f}",
                    f"{r.aggregate_ms_mean:.6f}",
                    f"{r.aggregate_ms_std:.6f}",
                    f"{r.verify_ms_mean:.6f}",
                    f"{r.verify_ms_std:.6f}",
                    f"{r.verify_success_rate:.4f}",
                    r.signature_size_bytes,
                ]
            )


def _svg_line_chart(path: Path, title: str, x_label: str, y_label: str, series: list[tuple[str, list[float], list[float]]]) -> None:
    width, height = 860, 480
    left, right, top, bottom = 80, 20, 50, 60
    plot_w = width - left - right
    plot_h = height - top - bottom

    all_x = [x for _, xs, _ in series for x in xs]
    all_y = [y for _, _, ys in series for y in ys]
    min_x, max_x = min(all_x), max(all_x)
    min_y, max_y = 0.0, max(all_y) * 1.15 if max(all_y) > 0 else 1.0

    def tx(x: float) -> float:
        if max_x == min_x:
            return left + plot_w / 2
        return left + (x - min_x) / (max_x - min_x) * plot_w

    def ty(y: float) -> float:
        return top + plot_h - (y - min_y) / (max_y - min_y) * plot_h

    colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728"]
    parts: list[str] = []
    parts.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">')
    parts.append('<rect width="100%" height="100%" fill="white"/>')
    parts.append(f'<text x="{width/2}" y="28" text-anchor="middle" font-size="20" font-family="Arial">{title}</text>')

    for i in range(6):
        yv = min_y + (max_y - min_y) * i / 5
        ypx = ty(yv)
        parts.append(f'<line x1="{left}" y1="{ypx:.1f}" x2="{left+plot_w}" y2="{ypx:.1f}" stroke="#eeeeee"/>')
        parts.append(f'<text x="{left-10}" y="{ypx+4:.1f}" text-anchor="end" font-size="11" font-family="Arial">{yv:.1f}</text>')

    uniq_x = sorted(set(all_x))
    for xv in uniq_x:
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

        lx = left + plot_w - 220
        ly = top + 20 + idx * 20
        parts.append(f'<line x1="{lx}" y1="{ly}" x2="{lx+20}" y2="{ly}" stroke="{c}" stroke-width="2.5"/>')
        parts.append(f'<text x="{lx+28}" y="{ly+4}" font-size="12" font-family="Arial">{name}</text>')

    parts.append(f'<text x="{left+plot_w/2}" y="{height-15}" text-anchor="middle" font-size="13" font-family="Arial">{x_label}</text>')
    parts.append(f'<text x="20" y="{top+plot_h/2}" transform="rotate(-90,20,{top+plot_h/2})" text-anchor="middle" font-size="13" font-family="Arial">{y_label}</text>')
    parts.append('</svg>')

    path.write_text("\n".join(parts), encoding="utf-8")


def _plot_scaling(records: list[BenchmarkRecord], path: Path) -> None:
    recs = sorted([r for r in records if r.n == 107 and r.q == 2048], key=lambda x: x.signer_count)
    x = [r.signer_count for r in recs]
    sign_total = [r.partial_sign_ms_mean * r.signer_count for r in recs]
    aggr = [r.aggregate_ms_mean for r in recs]
    ver = [r.verify_ms_mean for r in recs]

    _svg_line_chart(
        path,
        title="Runtime scaling at n=107, q=2048",
        x_label="Number of signers",
        y_label="Time (ms)",
        series=[
            ("Total signing (all signers)", x, sign_total),
            ("Aggregation", x, aggr),
            ("Verification", x, ver),
        ],
    )


def _plot_param_tradeoff(records: list[BenchmarkRecord], path: Path) -> None:
    recs = sorted([r for r in records if r.signer_count == 8], key=lambda x: x.n)
    x = [r.n for r in recs]
    verify = [r.verify_ms_mean for r in recs]
    size = [float(r.signature_size_bytes) for r in recs]

    _svg_line_chart(
        path,
        title="Parameter trade-off at 8 signers",
        x_label="Ring degree n",
        y_label="Verification time (ms) / Signature size (B)",
        series=[("Verification", x, verify), ("Signature size", x, size)],
    )


def _write_markdown(records: list[BenchmarkRecord], path: Path) -> None:
    lines = []
    lines.append("# Evaluation Report (journal-style)")
    lines.append("")
    lines.append("## Experimental protocol")
    lines.append("- Environment: Python reference implementation in this repository.")
    lines.append("- Metrics: key extraction, partial signing, aggregation, verification, signature size.")
    lines.append("- Each setting is averaged over 20 rounds.")
    lines.append("")
    lines.append("## Table 1. Runtime scaling (n=107, q=2048)")
    lines.append("")
    lines.append("| #Signers | KeyExtract (ms) | PartialSign (ms/signer) | Aggregate (ms) | Verify (ms) | Verify Success | Signature Size (B) |")
    lines.append("|---:|---:|---:|---:|---:|---:|---:|")

    for r in sorted([r for r in records if r.n == 107 and r.q == 2048], key=lambda x: x.signer_count):
        lines.append(
            f"| {r.signer_count} | {r.key_extract_ms_mean:.3f}±{r.key_extract_ms_std:.3f} | {r.partial_sign_ms_mean:.3f}±{r.partial_sign_ms_std:.3f} | {r.aggregate_ms_mean:.3f}±{r.aggregate_ms_std:.3f} | {r.verify_ms_mean:.3f}±{r.verify_ms_std:.3f} | {r.verify_success_rate:.2f} | {r.signature_size_bytes} |"
        )

    lines.append("")
    lines.append("## Table 2. Parameter sensitivity (8 signers)")
    lines.append("")
    lines.append("| n | q | Verify (ms) | Signature Size (B) |")
    lines.append("|---:|---:|---:|---:|")
    for r in sorted([r for r in records if r.signer_count == 8], key=lambda x: x.n):
        lines.append(f"| {r.n} | {r.q} | {r.verify_ms_mean:.3f}±{r.verify_ms_std:.3f} | {r.signature_size_bytes} |")

    lines.append("")
    lines.append("## Figures")
    lines.append("")
    lines.append("![Runtime scaling](runtime_scaling.svg)")
    lines.append("")
    lines.append("![Parameter tradeoff](parameter_tradeoff.svg)")
    lines.append("")
    lines.append("## Notes")
    lines.append("- This benchmark is intended for reproducible engineering comparison in your own environment.")
    lines.append("- For strict cryptographic security claims, map parameters to standardized security levels before publication.")

    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    records: list[BenchmarkRecord] = []

    for signer_count in [2, 4, 8, 16]:
        records.append(run_benchmark(n=107, q=2048, signer_count=signer_count, rounds=20))

    for n in [167, 251]:
        records.append(run_benchmark(n=n, q=2048, signer_count=8, rounds=20))

    _save_csv(records, OUT_DIR / "benchmark_results.csv")
    _plot_scaling(records, OUT_DIR / "runtime_scaling.svg")
    _plot_param_tradeoff(records, OUT_DIR / "parameter_tradeoff.svg")
    _write_markdown(records, OUT_DIR / "evaluation_report.md")


if __name__ == "__main__":
    main()
