from ms_scheme.evaluation import run_benchmark_csas, run_benchmark_ni, signature_size_bytes


def test_signature_size_bytes_grows_with_polynomial_count() -> None:
    s1 = signature_size_bytes(n=107, q=2048, signer_ids=["a", "b"], poly_count=2)
    s2 = signature_size_bytes(n=107, q=2048, signer_ids=["a", "b"], poly_count=4)
    assert s2 > s1


def test_run_benchmark_ni_success_rate() -> None:
    rec = run_benchmark_ni(n=107, q=2048, signer_count=2, rounds=2)
    assert rec.verify_success_rate == 1.0


def test_run_benchmark_csas_success_rate() -> None:
    rec = run_benchmark_csas(n=107, q=2048, signer_count=2, rounds=2)
    assert rec.verify_success_rate == 1.0
