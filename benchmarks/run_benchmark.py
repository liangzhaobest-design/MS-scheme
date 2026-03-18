from __future__ import annotations

import csv
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))

from ms_scheme.evaluation import BenchmarkRecord, run_benchmark_cl, run_benchmark_csas, run_benchmark_ibms, run_benchmark_ni

OUT_DIR = Path("reports")
OUT_DIR.mkdir(parents=True, exist_ok=True)

SCHEMES = ["IBMS-NTRU", "CL-NTRU-MS-IRS", "NI-IBMS-PKA", "CLSAS-NTRU"]
DISPLAY = {
    "IBMS-NTRU": "IBMS-NTRU",
    "CL-NTRU-MS-IRS": "CL-NTRU-MS-IRS (Ours)",
    "NI-IBMS-PKA": "NI-IBMS-PKA",
    "CLSAS-NTRU": "CLSAS-NTRU",
}
COLORS = {
    "IBMS-NTRU": "#4e79a7",
    "CL-NTRU-MS-IRS": "#e15759",
    "NI-IBMS-PKA": "#59a14f",
    "CLSAS-NTRU": "#af7aa1",
}


def _save_csv(records: list[BenchmarkRecord], path: Path) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow([
            "scheme", "n", "q", "signer_count", "rounds",
            "key_extract_ms_mean", "partial_sign_ms_mean", "aggregate_ms_mean", "verify_ms_mean",
            "verify_success_rate", "signature_size_bytes", "revoke_update_ms_mean", "revoke_check_ms_mean",
        ])
        for r in records:
            w.writerow([
                r.scheme, r.n, r.q, r.signer_count, r.rounds,
                f"{r.key_extract_ms_mean:.6f}", f"{r.partial_sign_ms_mean:.6f}", f"{r.aggregate_ms_mean:.6f}",
                f"{r.verify_ms_mean:.6f}", f"{r.verify_success_rate:.4f}", r.signature_size_bytes,
                f"{r.revoke_update_ms_mean:.6f}", f"{r.revoke_check_ms_mean:.6f}",
            ])


def _svg_line_chart(path: Path, title: str, x_label: str, y_label: str, series: list[tuple[str, list[float], list[float]]]) -> None:
    width, height = 980, 560
    left, right, top, bottom = 90, 40, 60, 70
    plot_w = width - left - right
    plot_h = height - top - bottom

    all_x = [x for _, xs, _ in series for x in xs]
    all_y = [y for _, _, ys in series for y in ys]
    min_x, max_x = min(all_x), max(all_x)
    max_y = max(all_y) * 1.12 if max(all_y) > 0 else 1.0

    def tx(x: float) -> float:
        if max_x == min_x:
            return left + plot_w / 2
        return left + (x - min_x) / (max_x - min_x) * plot_w

    def ty(y: float) -> float:
        return top + plot_h - (y / max_y) * plot_h

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        f'<text x="{width/2}" y="32" text-anchor="middle" font-size="22" font-family="Arial" font-weight="600">{title}</text>',
    ]

    # horizontal grid + y ticks
    for i in range(6):
        yv = max_y * i / 5
        ypx = ty(yv)
        parts.append(f'<line x1="{left}" y1="{ypx:.1f}" x2="{left+plot_w}" y2="{ypx:.1f}" stroke="#ececec"/>')
        parts.append(f'<text x="{left-10}" y="{ypx+4:.1f}" text-anchor="end" font-size="11" font-family="Arial">{yv:.2f}</text>')

    for xv in sorted(set(all_x)):
        xpx = tx(xv)
        parts.append(f'<line x1="{xpx:.1f}" y1="{top}" x2="{xpx:.1f}" y2="{top+plot_h}" stroke="#f6f6f6"/>')
        parts.append(f'<text x="{xpx:.1f}" y="{top+plot_h+22}" text-anchor="middle" font-size="12" font-family="Arial">{xv:g}</text>')

    parts.append(f'<line x1="{left}" y1="{top+plot_h}" x2="{left+plot_w}" y2="{top+plot_h}" stroke="#333"/>')
    parts.append(f'<line x1="{left}" y1="{top}" x2="{left}" y2="{top+plot_h}" stroke="#333"/>')

    for idx, (scheme, xs, ys) in enumerate(series):
        color = COLORS[scheme]
        stroke_w = 4.0 if scheme == "CL-NTRU-MS-IRS" else 2.5
        points = " ".join(f"{tx(x):.1f},{ty(y):.1f}" for x, y in zip(xs, ys))
        parts.append(f'<polyline points="{points}" fill="none" stroke="{color}" stroke-width="{stroke_w}"/>')
        for x, y in zip(xs, ys):
            r = 5 if scheme == "CL-NTRU-MS-IRS" else 3.5
            parts.append(f'<circle cx="{tx(x):.1f}" cy="{ty(y):.1f}" r="{r}" fill="{color}"/>')

        lx, ly = left + plot_w - 320, top + 24 + idx * 22
        parts.append(f'<line x1="{lx}" y1="{ly}" x2="{lx+22}" y2="{ly}" stroke="{color}" stroke-width="{stroke_w}"/>')
        fw = "700" if scheme == "CL-NTRU-MS-IRS" else "400"
        parts.append(f'<text x="{lx+30}" y="{ly+4}" font-size="12" font-family="Arial" font-weight="{fw}">{DISPLAY[scheme]}</text>')

    # label ours near last point
    ours = next(s for s in series if s[0] == "CL-NTRU-MS-IRS")
    ox, oy = tx(ours[1][-1]), ty(ours[2][-1])
    parts.append(f'<text x="{ox+10:.1f}" y="{oy-10:.1f}" font-size="12" font-family="Arial" font-weight="700" fill="{COLORS["CL-NTRU-MS-IRS"]}">Ours</text>')

    parts.append(f'<text x="{left+plot_w/2}" y="{height-18}" text-anchor="middle" font-size="14" font-family="Arial">{x_label}</text>')
    parts.append(f'<text x="22" y="{top+plot_h/2}" transform="rotate(-90,22,{top+plot_h/2})" text-anchor="middle" font-size="14" font-family="Arial">{y_label}</text>')
    parts.append('</svg>')
    path.write_text("\n".join(parts), encoding="utf-8")


def _plot_metric(records: list[BenchmarkRecord], path: Path, metric: str, title: str, y_label: str) -> None:
    series = []
    for scheme in SCHEMES:
        recs = sorted([r for r in records if r.scheme == scheme and r.n == 107 and r.q == 2048], key=lambda x: x.signer_count)
        series.append((scheme, [r.signer_count for r in recs], [getattr(r, metric) for r in recs]))
    _svg_line_chart(path, title, "Number of signers", y_label, series)


def _write_markdown(records: list[BenchmarkRecord], path: Path) -> None:
    base = [r for r in records if r.n == 107 and r.q == 2048 and r.signer_count == 8]
    size_ref = max(r.signature_size_bytes for r in base)

    lines = [
        "# Comparative Evaluation Report",
        "",
        "## 核心结论（论文展示版）",
        "- 已在图表中将 **CL-NTRU-MS-IRS (Ours)** 高亮标注。",
        "- 重点展示签名压缩率与撤销效率。",
        "",
        "## Table 1. 签名大小与压缩率（n=107, q=2048, 8 signers）",
        "",
        "| Scheme | Signature Size (B) | Size Reduction vs Max |",
        "|---|---:|---:|",
    ]

    for r in sorted(base, key=lambda x: x.signature_size_bytes):
        red = (size_ref - r.signature_size_bytes) / size_ref * 100.0
        name = DISPLAY[r.scheme]
        lines.append(f"| {name} | {r.signature_size_bytes} | {red:.2f}% |")

    lines.extend([
        "",
        "## Table 2. 撤销效率（n=107, q=2048, 8 signers）",
        "",
        "| Scheme | Revoke Update (ms) | Revoke Check (ms) | Verify (ms) |",
        "|---|---:|---:|---:|",
    ])

    for r in sorted(base, key=lambda x: x.revoke_check_ms_mean):
        lines.append(f"| {DISPLAY[r.scheme]} | {r.revoke_update_ms_mean:.4f} | {r.revoke_check_ms_mean:.4f} | {r.verify_ms_mean:.3f} |")

    lines.extend([
        "",
        "## Figures",
        "",
        "![Size comparison](size_comparison.svg)",
        "",
        "![Revocation check comparison](revoke_check_comparison.svg)",
        "",
        "![Verify comparison](verify_comparison.svg)",
    ])
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    records: list[BenchmarkRecord] = []
    for runner in [run_benchmark_ibms, run_benchmark_cl, run_benchmark_ni, run_benchmark_csas]:
        for signer_count in [2, 4, 8, 16]:
            records.append(runner(n=107, q=2048, signer_count=signer_count, rounds=20))
        for n in [167, 251]:
            records.append(runner(n=n, q=2048, signer_count=8, rounds=20))

    _save_csv(records, OUT_DIR / "benchmark_results.csv")
    _plot_metric(records, OUT_DIR / "size_comparison.svg", "signature_size_bytes", "Signature size comparison", "Signature size (bytes)")
    _plot_metric(records, OUT_DIR / "revoke_check_comparison.svg", "revoke_check_ms_mean", "Revocation check comparison", "Revoke check time (ms)")
    _plot_metric(records, OUT_DIR / "verify_comparison.svg", "verify_ms_mean", "Verification runtime comparison", "Verify time (ms)")
    _write_markdown(records, OUT_DIR / "evaluation_report.md")


if __name__ == "__main__":
    main()
