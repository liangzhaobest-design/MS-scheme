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
| NI-IBMS-PKA | 0.0002 | 0.0012 | 15.647 |
| IBMS-NTRU | 0.0002 | 0.0013 | 23.583 |
| CL-NTRU-MS-IRS (Ours) | 0.0002 | 0.0013 | 23.048 |
| CLSAS-NTRU | 0.0004 | 0.0013 | 22.680 |

## Table 3. 理论开销对比（渐进复杂度）

说明：n 为环维度，t 为签名者数量。该表基于本仓库实现流程抽象（用于论文中的实现级理论对比）。

| Scheme | Partial Sign | Aggregate | Verify | Signature Size |
|---|---|---|---|---|
| IBMS-NTRU | O(n) + 1·PolyMul | O(t·n) | O(t·PolyMul) | O(n) |
| CL-NTRU-MS-IRS (Ours) | O(n) + 1·PolyScalar | O(t·n) | O(t·PolyMul) | O(n) (compressed) |
| NI-IBMS-PKA | O(n) + 2·PolyScalar | O(t·n) | O(t·PolyMul) | O(n) |
| CLSAS-NTRU | O(n) + 1·PolyScalar (per step) | sequential (implicit) | O(t·PolyMul) | O(n) (minimal) |

## Table 4. 理论空间复杂度对比（密钥与签名）

说明：以下空间复杂度按本仓库实现中的多项式/向量存储口径给出；n 为环维度，t 为签名者数量。

| Scheme | User Secret Key Space | Public Key Space | Signature Space |
|---|---|---|---|
| IBMS-NTRU | O(n) | O(n) | O(n) + O(t) signer list |
| CL-NTRU-MS-IRS (Ours) | O(n) (compact secret) | O(n) | O(n) + O(t) signer list |
| NI-IBMS-PKA | O(n) + O(n) | O(n) aggregated/public key material | O(n) + O(n) + O(t) signer list |
| CLSAS-NTRU | O(n) + O(n) | O(n) | O(n) + O(t) sequential signer list |

## Figures

![Size comparison](size_comparison.svg)

![Revocation check comparison](revoke_check_comparison.svg)

![Verify comparison](verify_comparison.svg)