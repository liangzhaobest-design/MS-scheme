# Comparative Evaluation Report

## Protocol
- Baseline: A novel identity-based multi-signature scheme over NTRU (implemented as `IBMS-NTRU`).
- New implementation: `CL-NTRU-MS-IRS` based on `CL_NTRU_MS_IRS_en_final (1).pdf` naming and workflow abstraction.
- Metrics are averaged over 20 rounds.

## Table 1. Runtime comparison (n=107, q=2048)

| Scheme | #Signers | Sign(ms/signer) | Aggregate(ms) | Verify(ms) | Success | Size(B) |
|---|---:|---:|---:|---:|---:|---:|
| CL-NTRU-MS-IRS | 2 | 5.917 | 0.169 | 22.801 | 1.00 | 894 |
| CL-NTRU-MS-IRS | 4 | 6.031 | 0.371 | 42.376 | 1.00 | 932 |
| CL-NTRU-MS-IRS | 8 | 6.255 | 0.712 | 79.062 | 1.00 | 1008 |
| CL-NTRU-MS-IRS | 16 | 5.884 | 1.424 | 148.056 | 1.00 | 1160 |
| IBMS-NTRU | 2 | 2.965 | 0.092 | 14.774 | 1.00 | 466 |
| IBMS-NTRU | 4 | 3.043 | 0.187 | 27.140 | 1.00 | 504 |
| IBMS-NTRU | 8 | 2.964 | 0.376 | 52.763 | 1.00 | 580 |
| IBMS-NTRU | 16 | 2.858 | 0.659 | 93.758 | 1.00 | 732 |

## Table 2. Parameter sensitivity comparison (8 signers)

| Scheme | n | Verify(ms) | Size(B) |
|---|---:|---:|---:|
| CL-NTRU-MS-IRS | 107 | 79.062 | 1008 |
| CL-NTRU-MS-IRS | 167 | 190.103 | 1488 |
| CL-NTRU-MS-IRS | 251 | 437.514 | 2160 |
| IBMS-NTRU | 107 | 52.763 | 580 |
| IBMS-NTRU | 167 | 122.924 | 820 |
| IBMS-NTRU | 251 | 291.941 | 1156 |

## Figures

![Verify comparison](verify_comparison.svg)

![Size comparison](size_comparison.svg)