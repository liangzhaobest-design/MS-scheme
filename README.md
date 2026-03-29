# MS-scheme

本仓库包含四套基于 NTRU/格环的签名原型实现，并提供统一评测脚本做横向对比。

- 方案 A：`IBMS-NTRU`
- 方案 B：`CL-NTRU-MS-IRS`
- 方案 C：`NI-IBMS-PKA`
- 方案 D：`CLSAS-NTRU`（Certificateless Sequential Aggregate Signature Scheme on NTRU Lattice）

## 快速运行

```bash
python -m pytest -q
python benchmarks/run_benchmark.py
```

## 生成结果

运行评测后输出到 `reports/`：

- `benchmark_results.csv`：四方案统一格式原始数据
- `evaluation_report.md`：对比表格（可直接贴论文实验章节）
- `verify_comparison.svg`：验签耗时对比图
- `size_comparison.svg`：签名长度对比图

## 代码结构

- `ms_scheme/ibms_ntru.py`：方案 A
- `ms_scheme/cl_ntru_ms_irs.py`：方案 B
- `ms_scheme/ni_ibms_pka.py`：方案 C
- `ms_scheme/clsas_ntru.py`：方案 D
- `ms_scheme/evaluation.py`：统一评测框架
- `benchmarks/run_benchmark.py`：实验入口与报告生成
- `tests/`：正确性与评测工具测试
