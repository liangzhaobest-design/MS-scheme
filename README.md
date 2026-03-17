# MS-scheme

本仓库包含两套基于 NTRU 环的多签原型实现，并提供统一评测脚本用于直接横向对比。

- 方案 A：`IBMS-NTRU`（对应 `A novel identity-based multi-signature scheme over NTRU`）
- 方案 B：`CL-NTRU-MS-IRS`（对应 `CL_NTRU_MS_IRS_en_final (1).pdf`）

## 1) 快速运行

```bash
python -m pytest -q
python benchmarks/run_benchmark.py
```

## 2) 生成结果

运行评测后输出到 `reports/`：

- `benchmark_results.csv`：两方案统一格式原始数据
- `evaluation_report.md`：对比表格（可直接贴论文实验章节）
- `verify_comparison.svg`：验签耗时对比图
- `size_comparison.svg`：签名长度对比图

## 3) 代码结构

- `ms_scheme/ibms_ntru.py`：方案 A 实现
- `ms_scheme/cl_ntru_ms_irs.py`：方案 B 实现
- `ms_scheme/evaluation.py`：统一评测框架
- `benchmarks/run_benchmark.py`：实验入口与报告生成
- `tests/`：正确性与评测工具测试
