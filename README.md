# MS-scheme

基于论文 **A novel identity-based multi-signature scheme over NTRU** 的可运行复现实验，并补充了可投稿风格（top-journal style）的评估流程。

## 1) 实现内容

当前仓库给出一个工程化可复现基线：在 NTRU 型环 `Z_q[x]/(x^N+1)` 上实现身份绑定多签流程：

- `setup`
- `extract_user_key`
- `partial_sign`
- `aggregate`
- `verify`

核心代码：`ms_scheme/ibms_ntru.py`。

## 2) 一键评估（表格 + 图表）

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m pytest -q
python benchmarks/run_benchmark.py
```

运行后会生成：

- `reports/benchmark_results.csv`：原始结果
- `reports/evaluation_report.md`：论文式表格（均值±标准差）
- `reports/runtime_scaling.svg`：签名方规模扩展图
- `reports/parameter_tradeoff.svg`：参数-开销权衡图

## 3) 对比维度（建议和你的方案统一）

- 正确性：验签成功率
- 效率：密钥提取 / 单方签名 / 聚合 / 验签耗时
- 可扩展性：签名方数量变化下的耗时曲线
- 开销：签名长度（字节）

## 4) 目录

- `ms_scheme/ibms_ntru.py`：方案实现
- `ms_scheme/evaluation.py`：评估函数
- `benchmarks/run_benchmark.py`：实验脚本（产出表格与图）
- `reports/`：评估产物目录
- `tests/`：正确性和评估工具单测
