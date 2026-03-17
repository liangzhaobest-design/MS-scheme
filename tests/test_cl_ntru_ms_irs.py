from ms_scheme.cl_ntru_ms_irs import aggregate, extract_user_key, partial_sign, setup, verify


def _gen_signature(message: bytes):
    mkeys = setup()
    signers = ["id:alice", "id:bob", "id:carol"]
    user_keys = [extract_user_key(mkeys, sid) for sid in signers]
    partials = [partial_sign(mkeys, uk, message, signers) for uk in user_keys]
    msig = aggregate(partials, signers, mkeys.pp.params.q)
    return mkeys, msig, signers


def test_valid_multisignature_cl() -> None:
    mkeys, msig, _ = _gen_signature(b"hello")
    assert verify(mkeys.pp, b"hello", msig)


def test_message_tamper_fails_cl() -> None:
    mkeys, msig, _ = _gen_signature(b"hello")
    assert not verify(mkeys.pp, b"HELLO", msig)
