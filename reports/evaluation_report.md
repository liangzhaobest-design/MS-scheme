# Comparative Evaluation Report

## 核心结论（突出签名压缩 + 撤销效率）
- 本报告重点比较签名长度压缩效果与撤销处理效率。

## Table 1. 签名大小与压缩率（n=107, q=2048, 8 signers）

| Scheme | Signature Size (B) | Size Reduction vs Max |
|---|---:|---:|
| CL-NTRU-MS-IRS | 366 | 53.90% |
| CLSAS-NTRU | 366 | 53.90% |
| IBMS-NTRU | 580 | 26.95% |
| NI-IBMS-PKA | 794 | 0.00% |

## Table 2. 撤销效率（n=107, q=2048, 8 signers）

| Scheme | Revoke Update (ms) | Revoke Check (ms) | Verify (ms) |
|---|---:|---:|---:|
| IBMS-NTRU | 0.0004 | 0.0018 | 47.917 |
| CL-NTRU-MS-IRS | 0.0004 | 0.0018 | 48.661 |
| NI-IBMS-PKA | 0.0008 | 0.0022 | 31.556 |
| CLSAS-NTRU | 0.0014 | 0.0029 | 46.708 |

## Figures

![Size comparison](size_comparison.svg)

![Revocation check comparison](revoke_check_comparison.svg)

![Verify comparison](verify_comparison.svg)