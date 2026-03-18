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
| IBMS-NTRU | 0.0004 | 0.0033 | 73.106 |
| NI-IBMS-PKA | 0.0004 | 0.0036 | 50.936 |
| CL-NTRU-MS-IRS (Ours) | 0.0005 | 0.0043 | 74.801 |
| CLSAS-NTRU | 0.0007 | 0.0055 | 73.885 |

## Table 3. 理论开销对比（渐进复杂度）

说明：n 为环维度，t 为签名者数量。该表基于本仓库实现流程抽象（用于论文中的实现级理论对比）。

| Scheme | Partial Sign | Aggregate | Verify | Signature Size |
|---|---|---|---|---|
| IBMS-NTRU | O(n) + 1·PolyMul | O(t·n) | O(t·PolyMul) | O(n) |
| CL-NTRU-MS-IRS (Ours) | O(n) + 1·PolyScalar | O(t·n) | O(t·PolyMul) | O(n) (compressed) |
| NI-IBMS-PKA | O(n) + 2·PolyScalar | O(t·n) | O(t·PolyMul) | O(n) |
| CLSAS-NTRU | O(n) + 1·PolyScalar (per step) | sequential (implicit) | O(t·PolyMul) | O(n) (minimal) |

## Figures

![Size comparison](size_comparison.svg)

![Revocation check comparison](revoke_check_comparison.svg)

![Verify comparison](verify_comparison.svg)