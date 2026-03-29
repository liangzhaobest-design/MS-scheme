from ms_scheme.evaluation import signature_size_bytes


def test_signature_size_bytes_grows_with_signer_ids() -> None:
    small = signature_size_bytes(n=107, q=2048, signer_ids=["a", "b"])
    large = signature_size_bytes(n=107, q=2048, signer_ids=["alice", "bob", "carol"])
    assert large > small
