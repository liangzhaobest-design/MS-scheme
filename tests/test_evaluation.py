from ms_scheme.evaluation import signature_size_bytes


def test_signature_size_bytes_grows_with_polynomial_count() -> None:
    s1 = signature_size_bytes(n=107, q=2048, signer_ids=["a", "b"], poly_count=2)
    s2 = signature_size_bytes(n=107, q=2048, signer_ids=["a", "b"], poly_count=4)
    assert s2 > s1
