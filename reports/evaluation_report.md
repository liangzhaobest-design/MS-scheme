# Comparative Evaluation Report

## Protocol
- Baseline-1: IBMS-NTRU.
- Baseline-2: CL-NTRU-MS-IRS.
- New implementation: NI-IBMS-PKA (non-interactive identity-based multi-signature with public-key aggregation).
- Metrics are averaged over 20 rounds.

## Table 1. Runtime comparison (n=107, q=2048)

| Scheme | #Signers | Sign(ms/signer) | Aggregate(ms) | Verify(ms) | Success | Size(B) |
|---|---:|---:|---:|---:|---:|---:|
| CL-NTRU-MS-IRS | 2 | 5.772 | 0.200 | 23.599 | 1.00 | 894 |
| CL-NTRU-MS-IRS | 4 | 5.725 | 0.369 | 41.443 | 1.00 | 932 |
| CL-NTRU-MS-IRS | 8 | 5.750 | 0.691 | 74.114 | 1.00 | 1008 |
| CL-NTRU-MS-IRS | 16 | 5.737 | 1.745 | 144.935 | 1.00 | 1160 |
| IBMS-NTRU | 2 | 2.982 | 0.099 | 14.198 | 1.00 | 466 |
| IBMS-NTRU | 4 | 2.896 | 0.165 | 26.902 | 1.00 | 504 |
| IBMS-NTRU | 8 | 3.013 | 0.358 | 49.013 | 1.00 | 580 |
| IBMS-NTRU | 16 | 2.892 | 0.639 | 95.143 | 1.00 | 732 |
| NI-IBMS-PKA | 2 | 0.148 | 0.090 | 14.727 | 1.00 | 680 |
| NI-IBMS-PKA | 4 | 0.134 | 0.171 | 21.320 | 1.00 | 718 |
| NI-IBMS-PKA | 8 | 0.130 | 0.348 | 31.900 | 1.00 | 794 |
| NI-IBMS-PKA | 16 | 0.129 | 0.705 | 56.880 | 1.00 | 946 |

## Table 2. Parameter sensitivity comparison (8 signers)

| Scheme | n | Verify(ms) | Size(B) |
|---|---:|---:|---:|
| CL-NTRU-MS-IRS | 107 | 74.114 | 1008 |
| CL-NTRU-MS-IRS | 167 | 188.454 | 1488 |
| CL-NTRU-MS-IRS | 251 | 450.255 | 2160 |
| IBMS-NTRU | 107 | 49.013 | 580 |
| IBMS-NTRU | 167 | 126.669 | 820 |
| IBMS-NTRU | 251 | 289.584 | 1156 |
| NI-IBMS-PKA | 107 | 31.900 | 794 |
| NI-IBMS-PKA | 167 | 80.871 | 1154 |
| NI-IBMS-PKA | 251 | 185.060 | 1658 |

## Figures

![Verify comparison](verify_comparison.svg)

![Size comparison](size_comparison.svg)