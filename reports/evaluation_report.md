# Comparative Evaluation Report

## 核心结论（论文展示版）
- 已在图表中将 **CL-NTRU-MS-IRS (Ours)** 高亮标注。
- 重点展示签名压缩率与撤销效率。

## Table 1. 签名大小与压缩率（n=107, q=2048, 8 signers）

| Scheme | Signature Size (B) | Size Reduction vs Max |
|---|---:|---:|
| CL-NTRU-MS-IRS (Ours) | 366 | 53.90% |
| CLSAS-NTRU | 366 | 53.90% |
| IBMS-NTRU | 580 | 26.95% |
| NI-IBMS-PKA | 794 | 0.00% |

## Table 2. 撤销效率（n=107, q=2048, 8 signers）

| Scheme | Revoke Update (ms) | Revoke Check (ms) | Verify (ms) |
|---|---:|---:|---:|
| NI-IBMS-PKA | 0.0002 | 0.0013 | 15.646 |
| CLSAS-NTRU | 0.0004 | 0.0013 | 24.234 |
| CL-NTRU-MS-IRS (Ours) | 0.0002 | 0.0013 | 22.504 |
| IBMS-NTRU | 0.0002 | 0.0014 | 24.013 |

## Figures

![Size comparison](size_comparison.svg)

![Revocation check comparison](revoke_check_comparison.svg)

![Verify comparison](verify_comparison.svg)