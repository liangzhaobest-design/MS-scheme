# Comparative Evaluation Report

## Protocol
- Baseline-1: IBMS-NTRU.
- Baseline-2: CL-NTRU-MS-IRS.
- New implementation-1: NI-IBMS-PKA (non-interactive identity-based multi-signature with public-key aggregation).
- New implementation-2: CLSAS-NTRU (certificateless sequential aggregate signature on NTRU lattice).
- Metrics are averaged over 20 rounds.

## Table 1. Runtime comparison (n=107, q=2048)

| Scheme | #Signers | Sign(ms/signer) | Aggregate(ms) | Verify(ms) | Success | Size(B) |
|---|---:|---:|---:|---:|---:|---:|
| CL-NTRU-MS-IRS | 2 | 5.689 | 0.179 | 23.266 | 1.00 | 894 |
| CL-NTRU-MS-IRS | 4 | 5.697 | 0.332 | 40.405 | 1.00 | 932 |
| CL-NTRU-MS-IRS | 8 | 5.764 | 0.638 | 74.900 | 1.00 | 1008 |
| CL-NTRU-MS-IRS | 16 | 5.748 | 1.381 | 145.807 | 1.00 | 1160 |
| CLSAS-NTRU | 2 | 0.084 | 0.000 | 13.846 | 1.00 | 252 |
| CLSAS-NTRU | 4 | 0.069 | 0.000 | 24.436 | 1.00 | 290 |
| CLSAS-NTRU | 8 | 0.077 | 0.000 | 49.107 | 1.00 | 366 |
| CLSAS-NTRU | 16 | 0.085 | 0.000 | 99.998 | 1.00 | 518 |
| IBMS-NTRU | 2 | 2.767 | 0.101 | 14.331 | 1.00 | 466 |
| IBMS-NTRU | 4 | 2.862 | 0.194 | 26.472 | 1.00 | 504 |
| IBMS-NTRU | 8 | 2.959 | 0.308 | 48.786 | 1.00 | 580 |
| IBMS-NTRU | 16 | 2.910 | 0.666 | 97.145 | 1.00 | 732 |
| NI-IBMS-PKA | 2 | 0.156 | 0.100 | 15.268 | 1.00 | 680 |
| NI-IBMS-PKA | 4 | 0.124 | 0.167 | 20.756 | 1.00 | 718 |
| NI-IBMS-PKA | 8 | 0.118 | 0.335 | 32.525 | 1.00 | 794 |
| NI-IBMS-PKA | 16 | 0.120 | 0.735 | 58.436 | 1.00 | 946 |

## Table 2. Parameter sensitivity comparison (8 signers)

| Scheme | n | Verify(ms) | Size(B) |
|---|---:|---:|---:|
| CL-NTRU-MS-IRS | 107 | 74.900 | 1008 |
| CL-NTRU-MS-IRS | 167 | 183.430 | 1488 |
| CL-NTRU-MS-IRS | 251 | 442.199 | 2160 |
| CLSAS-NTRU | 107 | 49.107 | 366 |
| CLSAS-NTRU | 167 | 112.138 | 486 |
| CLSAS-NTRU | 251 | 265.541 | 654 |
| IBMS-NTRU | 107 | 48.786 | 580 |
| IBMS-NTRU | 167 | 123.762 | 820 |
| IBMS-NTRU | 251 | 287.526 | 1156 |
| NI-IBMS-PKA | 107 | 32.525 | 794 |
| NI-IBMS-PKA | 167 | 78.061 | 1154 |
| NI-IBMS-PKA | 251 | 188.519 | 1658 |

## Figures

![Verify comparison](verify_comparison.svg)

![Size comparison](size_comparison.svg)